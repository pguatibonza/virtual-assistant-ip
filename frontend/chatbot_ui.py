import streamlit as st
from backend.model import graph
import random
import time
import asyncio

def disable():
    st.session_state["disabled"] = True
    
def enable():
    st.session_state["disabled"] = False

async def app():

    st.title("Asistente Virtual IP")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
        

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("¿En qué podemos ayudarte hoy?", on_submit=disable, disabled=st.session_state.disabled):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Define the config variable
        config = {"configurable": {"thread_id": "1"}}
        
        with st.chat_message("assistant"):
            response = ""
            message_placeholder = st.empty()  # Create a placeholder to update the response
            
            async for event in graph.astream_events({"messages": ("user", user_input), "level": 2,"user_input" : user_input}, config, version="v1"):
                kind=event["event"]
                # Check if the event comes from the 'revise_answer' node
                if kind=="on_chat_model_stream" and event["metadata"]["langgraph_node"] in ["revise_feedback_answer","revise_conceptual_answer"]:
                    content=event["data"]["chunk"].content
                    if content:
                        response += content
                        message_placeholder.markdown(response)
                    
                    
        st.session_state.messages.append({"role": "assistant", "content": response})
        enable()
        st.rerun()