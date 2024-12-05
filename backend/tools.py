import logging
from typing import Literal, Optional
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from backend.db_connection import fetch_data
# from db_connection import fetch_data

log = logging.getLogger(__name__)

class ContinueOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the student's needs."""
    proceed: bool =Field(description="True if the current assistant can handle the user request.  False otherwise")
    reason: str
    request: str=Field(description="Any necessary follow-up questions the assistant should clarify  before proceeding. ")

class toConceptualAssistant(BaseModel):
    """
    Transfers work to a specialized assistant  to handle any conceptual doubts/inquiries about the programming course. The doubts must be about programming
    """
    request: str=Field(description="Any necessary follow-up questions the conceptual assistant  should clarify  before proceeding. The questions must be about programming. ")

class toFeedbackAssistant(BaseModel):
    """
    Transfers work to a specialized assistant to give detailed feedback about a code problem.
    It helps to analize code and give feedback to the student
    It also answers questions about the code and helps the student to understand the problem
    """
    problem_description : str=Field(description="The detailed problem description the student wants to get feedback from")
    request :  str=Field(description="Any necessary follow-up questions the conceptual assistant  should clarify  before proceeding" )
class AssistantName(BaseModel):
    """Identify the agent """

    found: Literal["primary_assistant","conceptual_assistant","feedback_assistant"] = Field(description="Name of the assistant to redirect")
    
class ProblemName(BaseModel):
    """Identify the problem name """

    found: bool = Field(description="Whether the problem was found or not")
    problem_list: list[str] = Field(description="List of problems found", default=[])

@tool
def find_problem_name(problem_name):
    """
    A tool to find the correct problem name based on the user input and a list of problems.
    It returns a list of problem names that match the user input, if any.
    This tool is useful to get the correct problem name to query the database for the problem description.    
    """
    query = "SELECT titulo FROM calificador_anonimo.dashboard_problema;"
    log.warning(query)
    exercises=fetch_data(query); 

    chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique")

    FIND_PROBLEM_NAME_PROMPT = """
    You are a specialized SQL assistant who is going to receive a user_input.
    The user_input must be a problem name.
    Your task is to identify the most related problems the user is referring to based on the following list 
    of problems:

    {exercises}


    If the user_input is related to any of the problem list names, you must return a JSON structure in the format below.
    Take in mind that the user may write wrong the user input, so you must do your best effort to identify which problem the user is searching.
    {{
        "found": true,
        "problem_list": ['problem_name', 'problem_name', 'problem_name']
    }}

    If the user_input does not match any of the problem list names, return a JSON structure in the format:
    {{
        "found": false,
        "problem_list": []
    }}
    """
    log.warning(FIND_PROBLEM_NAME_PROMPT)
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FIND_PROBLEM_NAME_PROMPT),
            ('human',"{user_input}")

        ]
    )
    sql_agent = prompt | chat.with_structured_output(ProblemName)

    response=sql_agent.invoke({"user_input":problem_name,"exercises":exercises})
    log.warning(response)
    if response.found:
        return response.problem_list
    else :
        return "Problem not found"

@tool
def extract_problem_info(problem_name):
    """
    Extract the problem info based on the problem name
    """
    query = f"SELECT * FROM calificador_anonimo.dashboard_problema WHERE titulo = '{problem_name}' LIMIT 1;"
    log.warning(query)
    exercise=fetch_data(query)
    log.warning(exercise)
    if exercise:=fetch_data(query):
        try:
            exercise=exercise[0]
            query = f"SELECT * FROM calificador_anonimo.dashboard_argumento WHERE problema_id = {exercise['id']} ORDER BY posicion ASC;"
            if parameters := fetch_data(query):
                parameters_str = "\n".join([f"name: {param['nombre']} - type: {param['tipo']} - description: {param['descripcion']}" for param in parameters])
            else:
                parameters_str = "No parameters found"
            query = f"""
                SELECT *
                FROM calificador_anonimo.dashboard_problema_funciones_prohibidas AS fp
                JOIN calificador_anonimo.dashboard_funcion AS f
                ON f.id = fp.funcion_id
                WHERE fp.problema_id = {exercise['id']};
            """
            if primitives := fetch_data(query):
                primitives_str = "\n".join([f"name: {prim['nombre']} - description: {prim['descripcion']}" for prim in primitives])
            else:
                primitives_str = "No primitives found"   
            return f"""
                problem_name: {exercise['titulo']}\n
                problem_description: {exercise['descripcion']}\n 
                function_name: {exercise['funcion']}\n 
                parameter_description: {parameters_str}\n
                return_description: {exercise['retorno_descripcion']}\n
                return_type : {exercise['retorno_tipo']}\n
                primitives_forbidden_description : {primitives_str}
                """
        except Exception as e:
            return "Error retrieving problem"
    else: 
        return "Problem not found"
                    