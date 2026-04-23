import requests
import os
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")

RISK_PERCENT = 1
BALANCE = 1000


def get_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1week&outputsize=1&apikey={API_KEY}"
    res = requests.get(url, timeout=10)
    data = res.json()

    if "values" not in data:
        raise Exception(data)

    candle = data["values"][0]

    return {
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "open": float(candle["open"]),
        "close": float(candle["close"])
    }


def calculate_levels(h, l, o, c):
    lq = (h + l + o + c) / 4
    r = h - l

    return {
        "LQ": lq,
        "magnet_low": lq - 2.5,
        "magnet_high": lq + 2.5,
        "extreme_high": lq + r,
        "extreme_low": lq - r
    }


def generate_trade(close, lvl):
    if lvl["magnet_low"] <= close <= lvl["magnet_high"]:
        return None

    if close > lvl["LQ"]:
        return {
            "type": "BUY",
            "entry": close,
            "sl": lvl["magnet_low"],
            "tp": lvl["extreme_high"]
        }

    if close < lvl["LQ"]:
        return {
            "type": "SELL",
            "entry": close,
            "sl": lvl["magnet_high"],
            "tp": lvl["extreme_low"]
        }


def position_size(balance, risk_percent, entry, sl):
    risk_amount = balance * (risk_percent / 100)
    sl_distance = abs(entry - sl)

    lot = risk_amount / sl_distance
    return round(lot, 2)


def send(msg):
    Bot(token=TOKEN).send_message(chat_id=CHAT_ID, text=msg)


def main():
    try:
        raw = get_data()
        lvl = calculate_levels(raw["high"], raw["low"], raw["open"], raw["close"])
        trade = generate_trade(raw["close"], lvl)

        if not trade:
            send("❌ NO TRADE minggu ini (harga di magnet zone)")
            return

        lot = position_size(BALANCE, RISK_PERCENT, trade["entry"], trade["sl"])

        message = f"""
📊 XAUUSD WEEKLY SYSTEM

📢 SIGNAL: {trade['type']}

📍 Entry: {round(trade['entry'],2)}
🛑 SL: {round(trade['sl'],2)}
🎯 TP: {round(trade['tp'],2)}

💰 Lot: {lot}
⚠️ Risk: {RISK_PERCENT}%

========================
🧲 LQ: {round(lvl['LQ'],2)}
========================
"""
        send(message)

    except Exception as e:
        send(f"❌ ERROR:\n{str(e)}")


if __name__ == "__main__":
    main()
