from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from supabase import create_client
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.output_parsers import StrOutputParser
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.schema import Document
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Literal
from typing import List
from typing_extensions import TypedDict
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from pprint import pprint
from typing import Any,  Literal, Union
from langchain_core.messages import  AnyMessage
from langchain.schema import AIMessage
from langchain_core.prompts import MessagesPlaceholder
import logging
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION=os.getenv("OPENAI_API_VERSION")

chat= AzureChatOpenAI(azure_deployment="gpt-4o_rfmanrique")



#Prompt feedback 
system = """

"Eres un tutor de programación encargado de brindar retroalimentación formativa a estudiantes del curso de introducción a la programación, quienes estan aprendiendo python. 
Tu vas a recibir toda la información del problema que se quiere revisar. 

No escribas bloques de código de ejemplo. No escribas una versión corregida o actualizada del código del estudiante. 
No debes escribir código para el estudiante. ¿Cómo responderías al estudiante para guiarlo y explicar conceptos sin proporcionar un ejemplo de código?"


La información consiste en :
1. Descripción del problema :
{problem_description}
2. Parametros de entrada:
{parameter_description} 
3. Retorno 
{return_description}
4. Funciones y primitivas prohibidas :
{primitives_forbiden_description}

La solución del estudiante no puede contener ninguna de las funciones y primitivas prohibidas. 

Los estudiantes proporcionarán el codigo de la solución : 
{user_input}

Si el user_input del usuario no es codigo, responde con un error diciendole que debe proveer el codigo del solución que tiene planeada. Debes ser simple y directo

Si el user_input es codigo, entonces: 
Analiza el codigo proporcionado por el usuario, y responde con una explicacion educativa, ayudando al estudiante a descubrir los problemas con su solución. 
Si la solución no presenta errores, dile al ususario que lo hizo muy bien. Se simple y conciso con tu respuesta


Asegurate de que la retroalimentación sea constructiva y fácil de entender, evitando cualquier tipo de critica negativa y enfocandote en como el estudiante puede aprender y mejorar

¡Sé positivo y alentador! Utiliza el formato Markdown, incluyendo ‘ para código en línea.
Primero realiza tu la solución para mirar diferencias con la solución que te manda el estudiante.

Recuerda que no puedes escribir bloques de codigo.


"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        
        ("placeholder","{messages}")
    ]
)

feedback_agent=prompt | chat

descripcion="""

En una estación de Transmilenio los operarios usan una fórmula matemática sencilla para saber si deben o no despachar un bus nuevo. Para esto tienen un contador de pasajeros en el bus entrante (personas_bus) y un contador de personas paradas en la plataforma (personas_estacion).

Los operarios saben que la capacidad teórica máxima del bus es de 150 personas. Sin embargo, también saben que si se aprietan pueden transportar a máximo 200 personas. Los pasajeros no quieren viajar incómodos pero tampoco quieren demorarse mucho tomando el bus, así que sólo se montarán a un bus con sobrecupo que llegue a la estación si hay 40 o más personas en la plataforma. Luego de que el bus se detenga y entren las personas, los operarios decidirán si deben enviar un bus adicional: enviarán un bus nuevo, si al salir de la estación el bus quedó con sobrecupo o si en la plataforma quedaron 50 o más personas.

Su trabajo es construir una función en Python que le ayude a los operarios de Transmilenio a tomar la decisión de despachar o no un bus nuevo.

"""

parametros=[
    {"nombre" : "personas_bus", "tipo" : "int", "descripcion" : "Numero de personas en el bus que va a detenerse"},
    {"nombre" : "personas_estacion", "tipo" : "int", "descripcion" : "Numero de personas esperando el bus de la estación"} 
]

retorno={"tipo":"bool", "descripcion": "Retorna el valor True si se debe despachar un bus nuevo y retorna False de lo contrario."}

primitivas=[{"nombre":"for" ,"descripcion":"No deberia usar la primitiva for para resolver este problema", "nombre" : "while", "descripcion": "No deberia usar la primitiva while para resolver este problema"}]



#solucion="cual es el modelo que estas usando"
solucion2="""
def despacho_buses(personas_bus: int, personas_estacion: int)->bool:
    despachar_bus = False
    sobrecupo = personas_bus > 150
    if sobrecupo and personas_estacion >= 40:
      despachar_bus = True
      
    capacidad = 200 - personas_bus
    
    if capacidad < personas_estacion:
      personas_estacion -= capacidad
      personas_bus += capacidad
    else:
      personas_bus += personas_estacion
      personas_estacion = 0
    if personas_bus > 150 or personas_estacion >=50:
      despachar_bus = True
      
    return despachar_bus
"""
solucion1="""
def despacho_buses(personas_bus: int, personas_estacion: int)->bool:

    # Definimos las constantes
    return True
"""

# Prompt rag
class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder=StateGraph(State)
memory = SqliteSaver.from_conn_string(":memory:")

def senecode_assistant(state:State):
    message=feedback_agent.invoke(
    {"problem_description":descripcion,"parameter_description":parametros,
    "return_description":retorno, "primitives_forbiden_description":primitivas,"user_input":state["messages"][-1], "messages":state["messages"]})

    return {"messages": [message]}

graph_builder.add_node("senecode_assistant",senecode_assistant)
graph_builder.add_edge(START, "senecode_assistant")
graph_builder.add_edge("senecode_assistant", END)

graph = graph_builder.compile(checkpointer=memory)
config={"configurable":{"thread_id":1}}
lista=["hola",solucion1,solucion2,"como puedes mejorar el codigo"]
for i in lista:
    for event in graph.stream({"messages": ("user", i)},config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
