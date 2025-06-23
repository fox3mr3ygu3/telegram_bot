import time
import a2s
import requests
import psycopg2
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, ContextTypes
from config import bot_token, db_url


AUTHORIZED_USERNAME = "bb_814"

def lawyer_handler(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return

    if update.message.text.lower() == "адвокат":
        user = update.message.from_user
        if user.username == AUTHORIZED_USERNAME:
            update.message.reply_text("⚖️ Я заявляю: мой клиент невиновен! Все обвинения — ложь и клевета.")
        else:
            update.message.reply_text("🤫 Тише, тише.")


def add_player(name: str, gender: str) -> bool:
    name = name.strip()
    if not name:
        return False
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO players (name, gender) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
            (name, gender)
        )
        conn.commit()
        return True
    except Exception as e:
        print("❌ DB Insert Error:", e)
        return False
    finally:
        conn.close()

def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.strip()
    user_text_lower = user_text.lower()
    result = None

    if user_text_lower in ["сервер", "server"]:
        result = parser()

    elif user_text_lower == "top":
        result = top()
    elif user_text_lower == "адвокат":
        result = lawyer_handler(update, context)
    elif user_text_lower == "инфо":
        result = (
            "🤖 Информация о боте\n\n"
            "Этот бот следит за CS 1.6 сервером:\n"
            "`CODE RED © (46.174.49.228:27015)`\n\n"
            "📌 Команды:\n"
            "• сервер или server — текущая карта, онлайн и список игроков\n"
            "• top — топ игроков со статистикой\n"
            "• инфо — информация о боте\n"
        )

    

    if not result:
        return

    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            update.message.reply_text(result[i:i+4000])
    else:
        update.message.reply_text(result)



def run_bot():
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print("🤖 Бот запущен. Ожидаем сообщения.")
    updater.start_polling()
    updater.idle()

def parser():
    address = ("46.174.49.228", 27015)
    result = "🌐 Сервер: CODE RED ©\n46.174.49.228:27015\n"

    try:
        info = a2s.info(address)
        players = a2s.players(address)

        result += f"🗺️  Карта: {info.map_name}\n"
        result += f"🎮⚡ Онлайн: {info.player_count}/{info.max_players}\n\n"

        if not players:
            result += "Нету игроков на сервере"
        else:
            result += "📋 Список игроков:\n"
            for i, p in enumerate(players, 1):
                name = p.name or "Без имени"
                score = p.score
                duration = int(p.duration or 0)
                mins = duration // 60
                secs = duration % 60
                result += f"{i}) {name} | Фраги: {score} | Время: {mins}м {secs}с\n"

    except Exception as e:
        result += f"\n❌ Ошибка при подключении: {e}"

    return result

def top():
    timestamp = int(time.time())
    url = f"https://onerussiapublic.ru/stats?_={timestamp}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    result = "🌐 Сервер: CODE RED ©\n46.174.49.228:27015\n\n📋 Топ игроков:\n\n"
    players = []

    try:
        table = soup.find("div", class_="table-responsive mb-0")
        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False)

        for row in rows:
            cols = row.find_all("td", recursive=False)
            if len(cols) >= 6 and "Статистика игрока" not in row.text:
                profile_td = cols[1]
                i_tag = profile_td.find("i")
                if i_tag:
                    nick = i_tag.get_text(strip=True)
                else:
                    img_tag = profile_td.find("img")
                    nick = img_tag["alt"].strip() if img_tag and img_tag.has_attr("alt") else profile_td.get_text(strip=True)

                nick = nick.replace("`", "'")
                kills = cols[2].text.strip()
                deaths = cols[3].text.strip()
                headshot = cols[4].text.strip()
                skill_raw = cols[5].text.strip()

                skill_digits = ''.join(filter(str.isdigit, skill_raw))
                skill_value = int(skill_digits) if skill_digits else 0

                players.append({
                    "nick": nick,
                    "kills": kills,
                    "deaths": deaths,
                    "hs": headshot,
                    "skill": skill_value,
                    "skill_raw": skill_raw
                })

        for index, p in enumerate(players, start=1):
            if index == 1:
                rank = "🥇-место-> "
            elif index == 2:
                rank = "🥈-место-> "
            elif index == 3:
                rank = "🥉-место-> "
            else:
                rank = f"{index:>2}-место -> "

            result += (
                f"{rank} {p['nick'].ljust(15)} "
                f"🗡️ {str(p['kills']).ljust(3)}  "
                f"💀 {str(p['deaths']).ljust(3)}  "
                f"🎯 {str(p['hs']).ljust(3)}  "
                f"📈 {p['skill_raw']}\n"
            )
    except AttributeError:
        result += "⚠️ Таблица не найдена или структура изменилась.\n"

    return result
