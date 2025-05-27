import time
import a2s
import requests
from config import bot_token, server_ip, chat_id

# Server and Telegram Bot Config
SERVER_ADDRESS = (server_ip, 27015)
BOT_TOKEN = bot_token
CHAT_ID = chat_id

# Players to watch
TARGET_MEN = {
    "white763", "Гаджет", "ChipWar", "X?", "SKOVER", "NarKotiK", "shakаl", "Nikitanos763",
    "Fnatik", "MapeD", "xddd", "LLirik", "kuniman", "PUPSIK", "VaLeRka 72", "hoho^", "Medved",
    "sokol", "Doctor", "dA-60Jlb", "[ORP] SHkiper", "Mamlyutskiy Killer Ivan", "дядя АМИР",
    "не обижайся", "Ковен", "007", "тень", "ORP Who s next", "BERSERKER", "SWAG :)", "ProtoTip4ik",
    "bb_814"
}
TARGET_WOMEN = {
    "Ная",                              
    "XyLiGaNkA",                   
    "KOFEMANKA",         
    "Madina",            
    "Malaya",            
}

# Keep track of who was online last time
previous_online_tracked = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_player_type(name):
    if name in TARGET_MEN:
        return "man"
    elif name in TARGET_WOMEN:
        return "woman"
    return None  # unknown

def check_players():
    global previous_online_tracked
    try:
        # Get current players
        players = a2s.players(SERVER_ADDRESS)
        online_now = {p.name.strip() for p in players if p.name.strip()}

        # Combine both watchlists
        all_tracked_players = TARGET_MEN | TARGET_WOMEN
        currently_online_tracked = online_now & all_tracked_players

        # Detect joins
        joined = currently_online_tracked - previous_online_tracked
        for player in joined:
            gender = get_player_type(player)
            if gender == "man":
                send_telegram_message(f"⚠️!!!ВНИМАНИЕ *{player}* зашёл на сервер")
            elif gender == "woman":
                send_telegram_message(f"⚠️!!!ВНИМАНИЕ *{player}* зашла на сервер")

        # Detect leaves
        left = previous_online_tracked - currently_online_tracked
        for player in left:
            gender = get_player_type(player)
            if gender == "man":
                send_telegram_message(f"🕊️ *{player}* вышел из сервера")
            elif gender == "woman":
                send_telegram_message(f"🕊️ *{player}* вышла из сервера.")
        
        # Update state
        previous_online_tracked = currently_online_tracked

    except Exception as e:
        print("❌ Error during check:", e)



