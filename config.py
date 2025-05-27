import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
server_ip = os.getenv("SERVER_IP")
db_url = os.getenv("DB_URL")


if not bot_token:
    raise ValueError("Bot token is not set in env")