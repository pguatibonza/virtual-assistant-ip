import logging
import os
import sys
import asyncio
import dotenv
import streamlit as st
from frontend.chatbot_ui import app
from frontend.login import login

logging.basicConfig()
log = logging.getLogger(__name__)
 
if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,  # Make sure this is set to INFO or lower
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]  # Send logs to stdout
)
    log.info("Starting the app")
    if 'token' in st.session_state:
        dotenv.load_dotenv()
        asyncio.run(app())
    else:
        token = login()
        if token:
            st.session_state['token'] = token
            st.rerun()