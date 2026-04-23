import requests
import os
from datetime import datetime

API_KEY = os.getenv("TWELVEDATA_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbol = "XAU/USD"

# ===== TELEGRAM FUNCTION =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== GET WEEKLY DATA =====
def get_weekly_candle():
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1week&outputsize=1&apikey={API_KEY}"
    data = requests.get(url).json()
    candle = data["values"][0]
    return float(candle["high"]), float(candle["low"]), float(candle["open"]), float(candle["close"])

# ===== GET CURRENT PRICE =====
def get_price():
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
    data = requests.get(url).json()
    return float(data["price"])

# ===== CALCULATE LEVELS =====
def calculate_levels():
    H, L, O, C = get_weekly_candle()
    LQ = (H+L+O+C)/4
    RANGE = H-L
    OVERBOUGHT = LQ + RANGE
    OVERSOLD = LQ - RANGE
    return LQ, OVERBOUGHT, OVERSOLD

# ===== MAIN LOGIC =====
def run_bot():
    LQ, OB, OS = calculate_levels()
    price = get_price()

    magnet_low = LQ - 2
    magnet_high = LQ + 2

    if price >= OB:
        send_telegram(f"🔴 XAUUSD OVERBOUGHT\nPrice: {price}\nTarget: {LQ}")

    elif price <= OS:
        send_telegram(f"🟢 XAUUSD OVERSOLD\nPrice: {price}\nTarget: {LQ}")

    elif magnet_low <= price <= magnet_high:
        send_telegram(f"🎯 MAGNET HIT\nPrice kembali ke LQ {LQ}")

run_bot()
