import streamlit as st
from backend.model import graph
import random
import time
import asyncio
import secrets

def disable():
    st.session_state["disabled"] = True
    
def enable():
    st.session_state["disabled"] = False
    
async def app():

    st.title("¡Hola!")
    st.write("Haz preguntas relacionadas con los temas de la clase o pide ayuda con los ejercicios de Senecode. Estoy aquí para ayudarte.")
    
    st.sidebar.markdown("Acciones")
    # Create a sidebar with a button to create a new chat
    if st.sidebar.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.disabled = False
        st.session_state.thread_id = secrets.token_hex(8)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = secrets.token_hex(8)
        
    # Display the thread id of the current conversation
    st.write(f"#### **ID Conversación Actual**: {st.session_state.thread_id}")
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("¿En qué podemos ayudarte hoy?", on_submit=disable, disabled=st.session_state.disabled):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Define the config variable
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        
        with st.chat_message("assistant"):
            response = ""
            message_placeholder = st.empty()  # Create a placeholder to update the response
            
            async for event in graph.astream_events({"messages": ("user", user_input), "level": 2, "user_input" : user_input}, config, version="v1"):
                kind=event["event"]
                # Check if the event comes from the 'revise_answer' node
                if kind=="on_chat_model_stream" and event["metadata"]["langgraph_node"] in ["evaluate_feedback_answer","evaluate_conceptual_answer"]:
                    content=event["data"]["chunk"].content
                    if content:
                        response += content
                        message_placeholder.markdown(response)
                        
            # # Get the current state of the conversation
            # conversation_state = graph.get_state(config=config)
            # st.session_state.current_state = conversation_state
                    
                    
        st.session_state.messages.append({"role": "assistant", "content": response})
        enable()
        st.rerun()