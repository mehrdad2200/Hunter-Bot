import os, re, asyncio, requests, random, time, socket
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from datetime import datetime, timedelta

API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'

# منابع کمکی برای وقتی تلگرام چیزی پیدا نمی‌کند
EXTRA_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

async def main():
    if not STRING_SESSION: return
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.connect()
    
    start_run = time.time()
    processed_links = set()

    while time.time() - start_run < 300: # ۵ دقیقه بیدار می‌ماند
        all_links = []
        
        # دریافت از تلگرام
        for kw in ['vless://', 'trojan://']:
            res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), limit=50))
            for m in res.messages:
                if m.message:
                    all_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message))
        
        # دریافت از منابع گیت‌هاب
        for url in EXTRA_SOURCES:
            try:
                r = requests.get(url, timeout=5)
                all_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', r.text))
            except: continue

        new_links = [l for l in set(all_links) if l not in processed_links]
        
        for link in new_links[:10]:
            try:
                t_now = (datetime.utcnow() + timedelta(hours=3, minutes=30)).strftime('%H:%M')
                msg = f"🚀 **HUNTER CONFIG**\n━━━━━━━━━━━━\n⏰ {t_now}\n🔗 ` {link.strip()} `\n━━━━━━━━━━━━\n🆔 @{MY_CHANNEL}"
                await client.send_message(MY_CHANNEL, msg)
                processed_links.add(link)
                await asyncio.sleep(15) # فاصله بین پست‌ها
            except: continue
            
        await asyncio.sleep(30) # انتظار برای دور بعدی

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
