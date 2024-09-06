from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from supabase import create_client
#from langgraph.checkpoint.sqlite import SqliteSaver
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
import load_data

#Inicialización variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION=os.getenv("OPENAI_API_VERSION")

vector_store=load_data.load_vector_store()
retriever=vector_store.as_retriever(search_kwargs={"k":4})
chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique")



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

chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique")



system="""
Eres un monitor asistente de la clase de introducción a la programación en Python. Tu función principal es responder dudas conceptuales que los estudiantes tengan sobre los diferentes módulos del curso. El curso está dividido en 4 módulos:

Módulo 1: Introducción a la programación

En este módulo, los estudiantes aprenden los fundamentos de la programación, cómo funcionan los lenguajes de programación y el proceso de escribir, ejecutar y depurar código.
Módulo 2: Condicionales

Aquí los estudiantes estudian las estructuras condicionales como if, else, y elif para tomar decisiones en el código.
Módulo 3: Bucles

En este módulo se cubren bucles for y while, junto con conceptos como control de bucles (break, continue).
Módulo 4: Librerías

Los estudiantes exploran cómo importar y utilizar librerías en Python, como math o random, y cómo instalar librerías externas.
Para responder preguntas de los estudiantes, tendrás como referencia el siguiente contexto tomado de un libro de programación:

{context}

Tu tarea es usar este contexto para responder de manera precisa, clara y útil a las preguntas. Intenta explicar los conceptos con ejemplos y lenguaje accesible para principiantes, proporcionando respuestas bien estructuradas y fáciles de entender. Si es necesario, usa fragmentos de código simples para ilustrar los conceptos.
El usuario se encuentra en el nivel : {level}
Utiliza el formato Markdown, incluyendo ‘ para código en línea.

Input del usuario : {user_input}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),      
        ("placeholder","{messages}")
    ]
)

conceptual_agent=prompt|chat

#Prompt  Question re-writer

system = """
Eres un reformulador de preguntas que convierte una pregunta de entrada en una versión mejorada, optimizada para la búsqueda en una vector store. 
Observa la entrada y trata de razonar sobre la intención o significado semántico subyacente. La vector store trata tema sobre introducción a la programación.
En algunas ocasiones el estudiante hará follow-up questions, por lo que debes reformularla basado en los mensajes anteriores para que pueda entrar a la vector store.
Debes ser simple y conciso.

La pregunta es : {user_input}
"""

re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("placeholder","{messages}"),
    ]
)
chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique")

question_rewriter = re_write_prompt | chat  



class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder=StateGraph(State)
#memory = SqliteSaver.from_conn_string(":memory:")
memory = MemorySaver()
def senecode_assistant(state:State):
    message=feedback_agent.invoke(
    {"problem_description":descripcion,"parameter_description":parametros,
    "return_description":retorno, "primitives_forbiden_description":primitivas,"user_input":state["messages"][-1], "messages":state["messages"]})

    return {"messages": [message]}
def conceptual_assistant(state:State):
    user_input=state['messages'][-1]
    #Reformula pregunta para vector store
    query=question_rewriter.invoke({"user_input": user_input, "messages":state["messages"]}).content

    #Extrae contexto segun el query
    context=retriever.invoke(query)

    #Responde de acuerdo al contexto
    response=conceptual_agent.invoke({"user_input":user_input,"messages":state["messages"],"context":context,"level":state["level"]})
    return {"messages": [response]}


graph_builder.add_node("senecode_assistant",senecode_assistant)
graph_builder.add_edge(START, "senecode_assistant")
graph_builder.add_edge("senecode_assistant", END)

graph = graph_builder.compile(checkpointer=memory)
config={"configurable":{"thread_id":1}}
lista=["hola",solucion1,solucion2,"como puedes mejorar el codigo"]
for i in lista:
    for event in graph.stream({"messages": ("user", i),"level":2},config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
