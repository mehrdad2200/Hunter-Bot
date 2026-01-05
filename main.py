import os, re, asyncio, requests, json, time
from datetime import datetime
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')

GITHUB_SOURCES = {
    "Joker-funland": "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/Splitted-Configs/vless.txt",
    "MahdiKharyab": "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "Yebekhe": "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"
}

ARCHIVE_FILE = "proxies_data.json"

def fetch_github_proxies():
    found = []
    print("🛰 در حال استخراج از گیت‌هاب...")
    for name, url in GITHUB_SOURCES.items():
        try:
            res = requests.get(url, timeout=10)
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res.text)
            for l in links[:20]: # از هر منبع ۲۰ تا برای تست
                found.append({"link": l, "source": f"GitHub: {name}", "time": datetime.now().strftime("%H:%M")})
        except: pass
    return found

async def fetch_telegram_proxies():
    if not STRING_SESSION: return []
    found = []
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        # تنظیم مهلت زمانی برای جلوگیری از گیر کردن در ۱۷ ثانیه
        await asyncio.wait_for(client.connect(), timeout=15)
        if await client.is_user_authorized():
            print("✅ اتصال تلگرام برقرار شد.")
            result = await client(functions.messages.SearchGlobalRequest(q='vless://', filter=types.InputMessagesFilterEmpty(), min_date=None, max_date=None, offset_id=0, offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20))
            for msg in result.messages:
                if hasattr(msg, 'message') and msg.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                    for l in links:
                        found.append({"link": l, "source": "Telegram Global", "time": datetime.now().strftime("%H:%M")})
    except Exception as e:
        print(f"⚠️ خطای تلگرام (رد شد): {e}")
    finally:
        await client.disconnect()
    return found

async def main():
    github_data = fetch_github_proxies()
    telegram_data = await fetch_telegram_proxies()
    
    final_data = (github_data + telegram_data)[:100]
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"🔥 عملیات موفق: {len(final_data)} کانفیگ ذخیره شد.")

if __name__ == "__main__":
    asyncio.run(main())
