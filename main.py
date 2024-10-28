from frontend.chatbot_ui import app
from frontend.login import login
import asyncio
import dotenv
import os
import streamlit as st

if __name__ == "__main__":
    if 'token' in st.session_state:
        dotenv.load_dotenv()
        asyncio.run(app())
    else:
        token = login()
        if token:
            st.session_state['token'] = token
            st.rerun()