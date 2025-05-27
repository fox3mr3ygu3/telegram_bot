import a2s
import requests
import psycopg2
from config import bot_token, chat_id, db_url
from telegram.utils.helpers import escape_markdown

SERVER_ADDRESS = ("46.174.48.168", 27015)
BOT_TOKEN = bot_token
CHAT_ID = chat_id

def init_db():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            gender TEXT CHECK(gender IN ('man', 'woman')) NOT NULL
        )
    """)
    # Insert default tracked players
    cur.executemany(
        "INSERT INTO players (name, gender) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
        [
            ("bb_814", "man"),
            ("X?", "man"),
            ("[ORP]Doctor°", "man")
        ]
    )
    conn.commit()
    conn.close()

init_db()


def get_players_by_gender(gender):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT name FROM players WHERE gender = %s", (gender,))
    players = {row[0] for row in cur.fetchall()}
    conn.close()
    return players

TARGET_MEN = get_players_by_gender("man")
TARGET_WOMEN = get_players_by_gender("woman")

previous_online_tracked = set()

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "MarkdownV2"}
    requests.post(url, data=data)

def get_player_type(name):
    if name in TARGET_MEN:
        return "man"
    elif name in TARGET_WOMEN:
        return "woman"
    return None

def check_players():
    global previous_online_tracked
    print("🔁 check_players() is running")
    try:
        players = a2s.players(SERVER_ADDRESS)
        print("🧍 Players found:", [repr(p.name) for p in players])
        online_now = {
            p.name.strip().replace("'", "").replace('"', "")
            for p in players if p.name.strip()
        }

        all_tracked_players = TARGET_MEN | TARGET_WOMEN
        currently_online_tracked = online_now & all_tracked_players

        joined = currently_online_tracked - previous_online_tracked
        for player in joined:
            gender = get_player_type(player)
            safe_name = escape_markdown(player, version=2)
            if gender == "man":
                send_telegram_message(f"⚠️\\!\\!\\!ВНИМАНИЕ *{safe_name}* зашёл на сервер")
            elif gender == "woman":
                send_telegram_message(f"⚠️\\!\\!\\!ВНИМАНИЕ *{safe_name}* зашла на сервер")

        left = previous_online_tracked - currently_online_tracked
        for player in left:
            gender = get_player_type(player)
            safe_name = escape_markdown(player, version=2)
            if gender == "man":
                send_telegram_message(f"🕊️ *{safe_name}* вышел из сервера")
            elif gender == "woman":
                send_telegram_message(f"🕊️ *{safe_name}* вышла из сервера.")

        previous_online_tracked = currently_online_tracked

    except Exception as e:
        print("❌ Error during check:", e)
