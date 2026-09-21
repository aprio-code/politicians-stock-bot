import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Endpoint alternativo non bloccato da GitHub Actions
ALT_TRADES_URL = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
# Backup API (House stock watcher via API proxy)
PROXY_API_URL = "https://raw.githubusercontent.com/isabelle-dr/house-stock-watcher-data/main/data/all_transactions.json"

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
    
    # Prova prima dal mirror GitHub
    response = requests.get(PROXY_API_URL, headers=headers, timeout=15)
    
    if response.status_code != 200:
        print(f"Mirror fallito ({response.status_code}), provo S3...")
        response = requests.get(ALT_TRADES_URL, headers=headers, timeout=15)

    if response.status_code != 200:
        print(f"❌ Impossibile scaricare i dati. Codice errore: {response.status_code}")
        return

    try:
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
