import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HOUSE_TRADES_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ ERRORE: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non trovati nei Secrets!")
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
        print(f"Errore durante l'invio su Telegram: {e}")

def fetch_and_analyze_trades():
    print("Download dati in corso...")
    
    # Headers completi per simulare al 100% una richiesta da browser Chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        session = requests.Session()
        response = session.get(HOUSE_TRADES_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Errore download API: {response.status_code}")
            return
        
        trades = response.json()
        print(f"✅ Dati scaricati! Trovati {len(trades)} record. Invio primi 3 su Telegram...")
        
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
        print(f"Errore generale: {e}")

if __name__ == "__main__":
    fetch_and_analyze_trades()
