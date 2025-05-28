from flask import Flask
from threading import Thread
from bot import run_bot
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ CS 1.6 Telegram Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)



if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    run_bot()

   
    
