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
from langchain_core.messages import  AnyMessage
from langchain.schema import AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import ToolMessage
import logging
import os
from backend import load_data
from backend.prompts import PRIMARY_ASSISTANT_PROMPT, FEEDBACK_AGENT_SYSTEM_PROMPT, RAG_AGENT_SYSTEM_PROMPT, ASSISTANT_ROUTER_PROMPT
from backend.tools import AssistantName, CompleteOrEscalate,toConceptualAssistant,toFeedbackAssistant, extract_problem_info, find_problem_name
# import load_data
# from prompts import PRIMARY_ASSISTANT_PROMPT, FEEDBACK_AGENT_SYSTEM_PROMPT, RAG_AGENT_SYSTEM_PROMPT, QUESTION_REWRITER_PROMPT
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
        ("human", " {user_input}" ),
        
    ]
)

primary_assistant = primary_assistant_prompt | chat.bind_tools([toConceptualAssistant,toFeedbackAssistant, extract_problem_info, find_problem_name])

chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique", streaming=False)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ASSISTANT_ROUTER_PROMPT),
        ("placeholder","{messages}"),
        ("human","{user_input}")
    ]
)

router_agent= prompt | chat.bind_tools([CompleteOrEscalate])


#Utilities

def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

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
                "feedback_assistant",
                "conceptual_assistant",
                "revise_answer"
            ]
        ],update_dialog_stack
    ]
    level : str
    problem_description : str


graph_builder=StateGraph(State)
memory = MemorySaver()


async def senecode_assistant(state:State):
    message=state['messages'][-2]
    if message.tool_calls:
        if message.tool_calls[0]["name"]== toFeedbackAssistant.__name__:
            state["problem_description"]=message.tool_calls[0]["args"]['problem_description']
            state["user_input"]=message.tool_calls[0]["args"]["code"]
    else :
        state["user_input"]=state["messages"][-1]
        state["problem_description"]=state.get("problem_description")

    #Identifica si el input del usuario lo puede responder el feedback assistant o lo redirecciona
    message = router_agent.invoke({"user_input":state["user_input"],"messages":state["messages"],"assistant_name":"feedback_assistant"}) 
    
    if message.tool_calls:
        return {"messages":[message]}
    else :
        feedback_message= feedback_agent.invoke(
        {"problem_description":state["problem_description"], "user_input":state["user_input"], "messages":state["messages"]})
        
        return {"messages" : [feedback_message], "problem_description": state["problem_description"]}


async def conceptual_assistant(state:State):
    user_input = state['user_input']

    #Identifica si el input del usuario lo puede responder el conceptual assistant o lo redirecciona
    message = router_agent.invoke({"user_input":user_input, "messages" : state['messages'], "assistant_name":"conceptual_assistant"})
    if message.tool_calls:
        return {"messages" : [message]}
    else : 

        #Extrae contexto segun el query
        context= retriever.invoke(user_input)

        #Responde de acuerdo al contexto
        response= await conceptual_agent.ainvoke({"user_input":user_input,"messages":state["messages"],"context":context,"level":state["level"]})
        return {"messages": [response]}



async def main_assistant(state:State):

    message= await primary_assistant.ainvoke({"user_input":state['user_input'],"messages":state['messages']})
    return {"messages":[message] }

# Revise answer before sending it to the user
chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique", streaming=True)

prompt = """
The following was written to help a student in a CS class. 
However, any example code (such as in ``` Markdown delimiters) can give the student an assignment’s answer rather than help them figure it out themselves. 
We need to provide help without including example code. 
To do this, rewrite the following to remove any code blocks so that the response explains what the student should do but does not provide solution code.
[original response to be rewritten]: {assistant_answer}
"""

feedback_revision_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        ("placeholder", "{messages}"),
    ]
)

feedback_revision_agent = feedback_revision_prompt | chat

async def revise_feedback_answer_to_user(state: State) -> dict:
    """Revise the answer to the user.
    The answer cannot contain code snippets.
    """
    message = state["messages"][-1]
    if message.tool_calls:
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
chat= AzureChatOpenAI(azure_deployment="gpt-4o-rfmanrique", streaming=True)

prompt = """
The following was written to help a student in a CS class. 
However, any example code (such as in ``` Markdown delimiters) can give the student an assignment’s answer rather than help them figure it out themselves. 
Keep the code blocks that explain programming concepts in general.
If a code block gives a specific problem solution to a user problem, remove it.
[original response to be rewritten]: {assistant_answer}
"""

conceptual_revision_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        ("placeholder", "{messages}"),
    ]
)

conceptual_revision_agent = conceptual_revision_prompt | chat

async def revise_conceptual_answer_to_user(state: State) -> dict:
    """Revise the answer to the user.
    The answer cannot contain code snippets.
    """
    message = state["messages"][-1]
    if message.tool_calls:
        return {"messages": [message]}
    response = await conceptual_revision_agent.ainvoke({"assistant_answer": state["messages"][-1].content})
    # Update the response message with the last message ID
    new_message = AIMessage(
    content=response.content,
    # Important! The ID is how LangGraph knows to REPLACE the message in the state rather than APPEND this messages
    id=message.id,
    )
    return {"messages": [new_message]}

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
    "conceptual_assistant",
    "feedback_assistant",
]:
    """If we are in a delegated state, route directly to the appropriate assistant."""

    
    dialog_state = state.get("dialog_state")
    if not dialog_state:
        return "primary_assistant"
    return dialog_state[-1]


#Por el momento se usara uno en conjunto apra feedback y conceptual
def route_feedback_assistant(
    state: State,
) -> Literal[
    "leave_skill",
    "revise_feedback_answer",
]:
    route = tools_condition(state)
    if route == END:
        return "revise_answer"
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"
    
#Por el momento se usara uno en conjunto apra feedback y conceptual
def route_conceptual_assistant(
    state: State,
) -> Literal[
    "leave_skill",
    "revise_conceptual_answer",
]:
    route = tools_condition(state)
    if route == END:
        return "revise_answer"
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

# This node will be shared for exiting all specialized assistants
def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the primary assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        # Note: Doesn't currently handle the edge case where the llm performs parallel tool calls
        # TODO: Handle parallel tool calls
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the student as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }


graph_builder.add_conditional_edges(START,route_to_workflow)
graph_builder.add_node("primary_assistant",main_assistant)

graph_builder.add_node("enter_conceptual_assistant",create_entry_node("Conceptual Programming assistant","conceptual_assistant"))
graph_builder.add_node("conceptual_assistant",conceptual_assistant)
graph_builder.add_edge("enter_conceptual_assistant", "conceptual_assistant")

graph_builder.add_node("enter_feedback_assistant",create_entry_node("Feedback assistant","feedback_assistant"))
graph_builder.add_node("feedback_assistant",senecode_assistant)
graph_builder.add_edge("enter_feedback_assistant", "feedback_assistant")

# Add revision node
graph_builder.add_node("revise_feedback_answer", revise_feedback_answer_to_user)
graph_builder.add_edge("revise_feedback_answer", END)

# Add conceptual revision node
graph_builder.add_node("revise_conceptual_answer", revise_conceptual_answer_to_user)
graph_builder.add_edge("revise_conceptual_answer", END)


tools=[extract_problem_info, find_problem_name]
tool_node=ToolNode(tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge("tools","primary_assistant")

graph_builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    {
        "enter_conceptual_assistant": "enter_conceptual_assistant",
        "enter_feedback_assistant": "enter_feedback_assistant",
        "tools":"tools",
        "revise_feedback_answer": "revise_feedback_answer"
    },
)
graph_builder.add_conditional_edges("conceptual_assistant", route_conceptual_assistant)
graph_builder.add_conditional_edges("feedback_assistant",route_feedback_assistant)
graph_builder.add_node("leave_skill",pop_dialog_state)
graph_builder.add_edge("leave_skill", "primary_assistant")

graph = graph_builder.compile(checkpointer=memory)
