import requests
from bs4 import BeautifulSoup
import time
import os
import threading
from flask import Flask

# ✅ Your bot token and chat_id
BOT_TOKEN = "8346040048:AAEa5A3ZZ8BI4xppBEUMVNkgZn94KZJNSsk"
CHAT_ID = "8205635617"

URL = "https://androidmultitool.com"   # Change if status page is different

# Store last status for all servers
last_status = {}

def notify(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
        print(f"[INFO] Telegram alert sent: {msg}")
    except Exception as e:
        print("Error sending Telegram message:", e)

def check_status():
    global last_status
    try:
        print("Checking server status...\n")
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the server table
        table = soup.find("table", {"class": "table"})
        rows = table.find("tbody").find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                server_name = cols[0].get_text(strip=True)
                status_badge = cols[1].find("span")

                if status_badge:
                    server_status = status_badge.get_text(strip=True)

                    print(f"{server_name}: {server_status}")

                    prev_status = last_status.get(server_name)
                    if prev_status != server_status:  # Only notify on change
                        if server_status.lower() == "online":
                            notify(f"✅ {server_name} is ONLINE now!")
                        elif server_status.lower() == "offline":
                            notify(f"⚠️ {server_name} is OFFLINE now!")

                        # Update last status
                        last_status[server_name] = server_status

    except Exception as e:
        print("Error checking server:", e)

# Flask web app
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Server Monitor is running and sending Telegram alerts!"

# Background thread for monitoring
def run_checker():
    while True:
        check_status()
        time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_checker, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
