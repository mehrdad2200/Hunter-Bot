import os, re, asyncio, requests, json, time, base64
from datetime import datetime
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# تنظیمات اصلی
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')

# لیست مخازن گیت‌هاب برای شکار
GITHUB_SOURCES = {
    "Joker-funland": "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/Splitted-Configs/vless.txt",
    "MahdiKharyab": "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "Yebekhe": "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"
}

ARCHIVE_FILE = "proxies_data.json"

def fetch_github_proxies():
    found = []
    for name, url in GITHUB_SOURCES.items():
        try:
            res = requests.get(url, timeout=10)
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res.text)
            for l in links:
                found.append({"link": l, "source": f"GitHub: {name}", "time": datetime.now().strftime("%H:%M")})
        except: pass
    return found

async def fetch_telegram_proxies():
    found = []
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        for kw in ['vless://', 'vmess://']:
            result = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), min_date=None, max_date=None, offset_id=0, offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=30))
            for msg in result.messages:
                if hasattr(msg, 'message') and msg.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                    for l in links:
                        found.append({"link": l, "source": "Telegram Global", "time": datetime.now().strftime("%H:%M")})
    await client.disconnect()
    return found

async def main():
    print("🚀 در حال شکار از تلگرام و گیت‌هاب...")
    all_configs = fetch_github_proxies() + await fetch_telegram_proxies()
    
    # نگه داشتن ۱۰۰ عدد آخر
    final_data = all_configs[:100]
    
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"✅ {len(final_data)} کانفیگ در آرشیو ذخیره شد.")

if __name__ == "__main__":
    asyncio.run(main())
