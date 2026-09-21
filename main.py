import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HOUSE_TRADES_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERRORE: Token o Chat ID mancanti nei Secrets!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    resp = requests.post(url, json=payload)
    print(f"Risposta Telegram: {resp.status_code} - {resp.text}")

def fetch_and_analyze_trades():
    print("Download dati in corso...")
    response = requests.get(HOUSE_TRADES_URL)
    
    if response.status_code != 200:
        print(f"Errore download API: {response.status_code}")
        return
    
    trades = response.json()
    print(f"Scaricati {len(trades)} record. Invio primi 3...")
    
    for trade in trades[:3]:
        representative = trade.get("representative", "Sconosciuto")
        ticker = trade.get("ticker", "N/A")
        type_trade = trade.get("type", "N/A")
        amount = trade.get("amount", "N/A")
        disclosure_date = trade.get("disclosure_date", "N/A")
        transaction_date = trade.get("transaction_date", "N/A")

        message = (
            f"🚨 *NUOVA TRANSAZIONE POLITICO USA* 🚨\n\n"
            f"👤 *Politico:* {representative}\n"
            f"📈 *Ticker:* `{ticker}`\n"
            f"🔄 *Operazione:* {type_trade.upper()}\n"
            f"💰 *Importo:* {amount}\n"
            f"📅 *Data Operazione:* {transaction_date}\n"
            f"📝 *Data Dichiarazione:* {disclosure_date}\n"
        )
        send_telegram_alert(message)

if __name__ == "__main__":
    fetch_and_analyze_trades()
