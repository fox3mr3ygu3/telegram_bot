import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
server_ip = os.getenv("SERVER_IP")
server_port = int(os.getenv("SERVER_PORT"))

if not bot_token:
    raise ValueError("Bot token is not set in env")