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
from typing import Any,  Literal, Union, Optional,Callable
from langchain_core.messages import  AnyMessage,HumanMessage,RemoveMessage,SystemMessage,ToolMessage
from langchain.schema import AIMessage
from langchain_core.prompts import MessagesPlaceholder
import logging
import os
from backend import load_data
from backend.prompts import PRIMARY_ASSISTANT_PROMPT, FEEDBACK_AGENT_SYSTEM_PROMPT, RAG_AGENT_SYSTEM_PROMPT, ASSISTANT_ROUTER_PROMPT,  FEEDBACK_REVISION_PROMPT, CONCEPTUAL_REVISION_PROMPT
from backend.tools import AssistantName, ContinueOrEscalate,toConceptualAssistant,toFeedbackAssistant, extract_problem_info, find_problem_name
# import load_data
# from prompts import PRIMARY_ASSISTANT_PROMPT, FEEDBACK_AGENT_SYSTEM_PROMPT, RAG_AGENT_SYSTEM_PROMPT, ASSISTANT_ROUTER_PROMPT,  FEEDBACK_REVISION_PROMPT, CONCEPTUAL_REVISION_PROMPT
# from tools import CompleteOrEscalate,toConceptualAssistant,toFeedbackAssistant,extract_problem_info,find_problem_name

#Inicialización variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION=os.getenv("OPENAI_API_VERSION")

vector_store=load_data.load_vector_store()
retriever=vector_store.as_retriever(search_kwargs={"k":1})

chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique",streaming=False)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FEEDBACK_AGENT_SYSTEM_PROMPT),
        ("placeholder","{messages}")
    ]
)

feedback_agent= prompt | chat


chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique",streaming=True)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_AGENT_SYSTEM_PROMPT),      
        ("placeholder","{messages}")
    ]
)

conceptual_agent=prompt|chat


#Main assistant 
chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique",streaming=True)


primary_assistant_prompt=ChatPromptTemplate.from_messages(
    [
        ("system",PRIMARY_ASSISTANT_PROMPT),
        ("placeholder","{messages}"),
        
    ]
)

primary_assistant = primary_assistant_prompt | chat.bind_tools([toConceptualAssistant,toFeedbackAssistant, extract_problem_info, find_problem_name])


#Route agents

chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique", streaming=False)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ASSISTANT_ROUTER_PROMPT),
        ("placeholder","{messages}"),
    ]
)

router_agent= prompt | chat.with_structured_output(ContinueOrEscalate)

# Feedback revision answer
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FEEDBACK_REVISION_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

feedback_revision_agent = prompt | chat


#Conceptual revision answer
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CONCEPTUAL_REVISION_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

conceptual_revision_agent = prompt | chat


#Utilities

def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        args = state["messages"][-1].tool_calls[0]["args"]

        # Crear el diccionario de retorno con cada llave y valor de args
        result_dict = {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

        # Agregar cada par llave-valor de args al diccionario de retorno
        result_dict.update(args)

        return result_dict

    return entry_node

#Graph
def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    messages:Annotated[list,add_messages]
    user_input : str
    dialog_state : Annotated[
        list[
            Literal[
                "primary_assistant",
                "router_feedback_assistant",
                "conceptual_assistant",
                "revise_answer"
            ]
        ],update_dialog_stack
    ]
    level : str
    problem_description : str
    escalated: bool
    request : str
    summary : str 


graph_builder=StateGraph(State)
memory = MemorySaver()

### Nodes 
async def router_senecode_assistant(state:State):

    #Identifica si el input del usuario lo puede responder el feedback assistant o lo redirecciona
    message = router_agent.invoke({"user_input":state["user_input"],"messages":state["messages"],"assistant_name":"feedback_assistant"})  
    return {"escalated": message.proceed, "problem_description":state.get("problem_description",""),"request":message.request} 

async def senecode_assistant(state:State):
    user_input=state["user_input"]

    feedback_message= feedback_agent.invoke({"problem_description":state["problem_description"], "user_input":user_input, "messages":state["messages"]})
        
    return {"messages" : [feedback_message]}

async def router_conceptual_assistant(state : State):
    #Identifica si el input del usuario lo puede responder el feedback assistant o lo redirecciona
    message = router_agent.invoke({"user_input":state["user_input"], "messages" : state['messages'], "assistant_name":"conceptual_assistant"})
    #Se almacena el request para usarlo como query en la vector db
    return {"escalated": message.proceed,"request":message.request} 

async def conceptual_assistant(state:State):
    user_input = state['user_input']
    user_request = state["request"]

    #Extrae contexto segun el query
    context= retriever.invoke(user_request)

    #Responde de acuerdo al contexto
    response= await conceptual_agent.ainvoke({"user_input":user_input,"messages":state["messages"],"context":context,"level":state["level"]})
    return {"messages": [response]}



async def main_assistant(state:State):

    message= await primary_assistant.ainvoke({"user_input":state['user_input'],"messages":state['messages']})
    return {"messages":[message] }


async def revise_feedback_answer_to_user(state: State) -> dict:
    """Revise the answer to the user.
    The answer cannot contain code snippets.
    """
    message = state["messages"][-1]
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        return {"messages": [message]}
    response = await feedback_revision_agent.ainvoke({"assistant_answer": state["messages"][-1].content})
    # Update the response message with the last message ID
    new_message = AIMessage(
    content=response.content,
    # Important! The ID is how LangGraph knows to REPLACE the message in the state rather than APPEND this messages
    id=message.id,
    )
    return {"messages": [new_message]}

# Revise answer before sending it to the user
async def revise_conceptual_answer_to_user(state: State) -> dict:
    """Revise the answer to the user.
    The answer cannot contain code snippets.
    """
    message = state["messages"][-1]
    if hasattr(message, "tool_calls") and len(message.tool_calls) > 0:
        return {"messages": [message]}
    response = await conceptual_revision_agent.ainvoke({"assistant_answer": state["messages"][-1].content})
    # Update the response message with the last message ID
    new_message = AIMessage(
    content=response.content,
    # Important! The ID is how LangGraph knows to REPLACE the message in the state rather than APPEND this messages
    id=message.id,
    )
    return {"messages": [new_message]}

async def summarize_conversation(state: State):
    # Get any existing summary
    summary = state.get("summary", "")
    
    # Create summarization prompt
    if summary:
        # A summary already exists
        summary_message = (
            f"This is the summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    
    # Add prompt to the history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = await chat.ainvoke(messages)

    summary_content = f"Summary of conversation earlier : {response.content}"
    summary_message = SystemMessage(content=summary_content)


    # Identify the last 2 messages, including their tool call pairs if necessary
    last_two_messages = state["messages"][-2:]  # Get the last two messages
    final_messages = []  # To store the final messages we want to keep

    for message in last_two_messages:
        
        final_messages.append(message)
        print(message)
        # If the message is a ToolMessage, make sure to include the following AI response
        if isinstance(message, ToolMessage):
            print("tool")
            tool_index = state["messages"].index(message)
            if tool_index - 1 < len(state["messages"]):
                i=1
                while  isinstance(state["messages"][tool_index - i],ToolMessage):
                    final_messages.append(state["messages"][tool_index - i])
                    i+=1   
                final_messages.append(state["messages"][tool_index - i])
    # Now prepare the list of messages to delete (all messages except the final ones)
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"] if m not in final_messages]
    new_messages = delete_messages + [summary_message]
    return {"summary": response.content, "messages": new_messages}

### Edges

def should_summarize(state: State):
        
    """Return the next node to execute."""
    
    messages = state["messages"]
    
    # If there are more than x messages, then we summarize the conversation
    if len(messages) > 12:
        return "summarize_conversation"
    
    # Otherwise we can just end
    return END


def route_primary_assistant(
    state: State,
) -> Literal[
    "enter_conceptual_assistant",
    "enter_feedback_assistant",
    "tools",
    "revise_feedback_answer"
]:
    route = tools_condition(state)
    if route == END:
        return "revise_feedback_answer"
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == toConceptualAssistant.__name__:
            return "enter_conceptual_assistant"
        elif tool_calls[0]["name"] == toFeedbackAssistant.__name__:
            return "enter_feedback_assistant"
        return "tools"
    raise ValueError("Invalid route")


async def route_to_workflow(
    state: State,
) -> Literal[
    "primary_assistant",
    "conceptual",
    "feedback",
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""

    
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]


# Maneja los edges del nodo router feedback assistant
def route_router_feedback_assistant(state:State):
    if not state["escalated"]:
        return "leave_skill"
    return "feedback_assistant"
# Maneja los ejes del nodo feedback assistant  
def route_feedback_assistant(
    state: State,
) -> Literal[
    "leave_skill",
    "revise_feedback_answer",
]:
    route = tools_condition(state)
    if route == END:
        return "revise_feedback_answer"
    
    ###Lo de abajo ya no va. #TODO Separa asistente en varios componentes
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == ContinueOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
# Maneja los edges del nodo router conceptual assistant
def route_router_conceptual_assistant(state:State):
    if not state["escalated"]:
        return "leave_skill"
    return "conceptual_assistant"
 
# Con las modificaciones de router, solo es necesario que el conceptual vaya al revise answer, pues no hay mas nodos
# def route_conceptual_assistant(
#     state: State,
# ) -> Literal[
#     "leave_skill",
#     "revise_conceptual_answer",
# ]:
#     route = tools_condition(state)
#     if route == END:
#         return "revise_conceptual_answer"
#     tool_calls = state["messages"][-1].tool_calls
#     did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
#     if did_cancel:
#         return "leave_skill"

# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the primary assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []

    messages.append(
            AIMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the student as needed.",
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }


graph_builder.add_conditional_edges(START,route_to_workflow,
                                     
                                    {"feedback" : "router_feedback_assistant" ,
                                     "primary_assistant" : "primary_assistant" ,
                                     "conceptual":"router_conceptual_assistant"} )
graph_builder.add_node("primary_assistant",main_assistant)

graph_builder.add_node("enter_conceptual_assistant",create_entry_node("Conceptual Programming assistant","conceptual"))
graph_builder.add_node("conceptual_assistant",conceptual_assistant)
graph_builder.add_edge("enter_conceptual_assistant", "conceptual_assistant")
graph_builder.add_node("router_conceptual_assistant",router_conceptual_assistant)
graph_builder.add_conditional_edges("router_conceptual_assistant",route_router_conceptual_assistant )

graph_builder.add_node("enter_feedback_assistant",create_entry_node("Feedback assistant","feedback"))
graph_builder.add_node("feedback_assistant",senecode_assistant)
graph_builder.add_edge("enter_feedback_assistant", "feedback_assistant")
graph_builder.add_node("router_feedback_assistant",router_senecode_assistant)
graph_builder.add_conditional_edges("router_feedback_assistant",route_router_feedback_assistant )

# Add revision node
graph_builder.add_node("revise_feedback_answer", revise_feedback_answer_to_user)
graph_builder.add_conditional_edges("revise_feedback_answer", should_summarize)

# Add conceptual revision node
graph_builder.add_node("revise_conceptual_answer", revise_conceptual_answer_to_user)
graph_builder.add_conditional_edges("revise_conceptual_answer", should_summarize)

#Add summarize conversarion node
graph_builder.add_node("summarize_conversation",summarize_conversation)

graph_builder.add_node("tools", ToolNode([extract_problem_info, find_problem_name]))
graph_builder.add_edge("tools","primary_assistant")

graph_builder.add_conditional_edges("primary_assistant",route_primary_assistant,)
graph_builder.add_edge("conceptual_assistant", "revise_conceptual_answer")
graph_builder.add_conditional_edges("feedback_assistant",route_feedback_assistant)
graph_builder.add_node("leave_skill",pop_dialog_state)
graph_builder.add_edge("leave_skill", "primary_assistant")

graph = graph_builder.compile(checkpointer=memory)
