from frontend.chatbot_ui import app
import asyncio
import dotenv
import os

dotenv.load_dotenv()

asyncio.run(app())