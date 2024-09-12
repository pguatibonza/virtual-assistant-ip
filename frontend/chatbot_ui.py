import streamlit as st
from backend.model import graph
import random
import time

def app():

    st.title("Asistente Virtual IP")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("¿En qué podemos ayudarte hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Define the config variable
        config = {"configurable": {"thread_id": "1"}}
        
        with st.chat_message("assistant"):
            response = ""
            for event in graph.stream({"messages": ("user", prompt), "level": 2}, config):
                for value in event.values():
                    response += value["messages"][-1].content + " "
                    st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})