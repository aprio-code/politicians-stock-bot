import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Endpoint API aggiornato e accessibile da GitHub Actions
DATA_URL = "https://raw.githubusercontent.com/house-stock-watcher/house-stock-watcher-data/main/data/all_transactions.json"

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERRORE: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID mancanti nei Secrets!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Risposta Telegram: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def fetch_and_analyze_trades():
    print("Download dati in corso...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(DATA_URL, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"❌ Errore download API: {response.status_code}")
            return

        trades = response.json()
        print(f"✅ Dati scaricati con successo ({len(trades)} record trovati). Invio primi 3 su Telegram...")
        
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

    except Exception as e:
        print(f"Errore durante l'analisi dati: {e}")

if __name__ == "__main__":
    fetch_and_analyze_trades()
