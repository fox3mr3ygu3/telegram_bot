import requests
from bs4 import BeautifulSoup

def parser():
    url = "https://www.gs4u.net/ru/s/373896.html"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Начинаем собирать результат как текст
    result = "🌐 Сервер: ONE RUSSIAN PUBLIC ©\n46.174.48.168:27015\n"

    try:
        map_div = soup.find("div", class_="inlineblocktop map")
        map_text = map_div.find("a", class_="hasTooltip").text.strip()
        result += f"🗺️  Карта: {map_text}\n"
    except:
        result += "🗺️  Карта: неизвестна\n"

    try:
        online_div = soup.find("div", class_="value players")
        online_text = online_div.find("b").text.strip()
        result += f"🎮⚡ Онлайн: {online_text}/32\n\n"
    except:
        result += "🎮⚡ Онлайн: неизвестно\n\n"

    try:
        table = soup.find("table", class_="serverplayers")
        rows = table.find("tbody").find_all("tr")

        result += "📋 Список игроков:\n"
        for i, row in enumerate(rows, start=1):
            cols = row.find_all("td")
            if len(cols) >= 3:
                nick = cols[0].text.strip()
                score = cols[1].text.strip()
                time_played = cols[2].text.strip()
                result += f"{i}) {nick} | Фраги: {score} | Время: {time_played}\n"

    except AttributeError:
        result += "Нету игроков на сервере"

    return result


def top():
    url = "https://onerussiapublic.ru/stats"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    result = "🌐 Сервер: ONE RUSSIAN PUBLIC ©\n"
    result += "46.174.48.168:27015\n\n"
    result += "📋 Топ игроков:\n\n"

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
                    if img_tag and img_tag.has_attr("alt"):
                        nick = img_tag["alt"].strip()
                    else:
                        nick = profile_td.get_text(strip=True)

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

        
        # Display with rank emojis
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

