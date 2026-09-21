import os
import requests

# Recupera le credenziali da GitHub Secrets
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Endpoint API per le dichiarazioni della Camera USA
HOUSE_TRADES_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def fetch_and_analyze_trades():
    try:
        response = requests.get(HOUSE_TRADES_URL)
        if response.status_code != 200:
            print("Errore nel recupero dati API")
            return
        
        trades = response.json()
        recent_trades = trades[:3]  # Prende le ultime 3 operazioni
        
        for trade in recent_trades:
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

    except Exception as e:
        print(f"Errore analisi: {e}")

if __name__ == "__main__":
    fetch_and_analyze_trades()
