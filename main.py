import os, re, asyncio, json, time, requests
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات پایه ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = -1003576265638 
START_TIME = time.time()

# منابع گیت‌هاب (تضمینی)
SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ متصل شد. شروع ارسال مستقیم...")

        while time.time() - START_TIME < 300: # ۵ دقیقه بیدار ماندن
            links = []
            
            # ۱. دریافت از گیت‌هاب
            for url in SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            # ۲. دریافت از تلگرام
            for kw in ['vless://', 'trojan://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), limit=30))
                    for m in res.messages:
                        if m.message: links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message))
                except: continue

            # حذف تکراری‌ها و ارسال
            unique_links = list(set(links))
            print(f"🔎 {len(unique_links)} لینک پیدا شد. در حال ارسال...")

            for link in unique_links[:20]: # در هر دور حداکثر ۲۰ تا بفرست
                if time.time() - START_TIME > 300: break
                
                proto = link.split('://')[0].upper()
                t_now = (datetime.utcnow() + timedelta(hours=3, minutes=30)).strftime('%H:%M')
                
                text = (
                    f"🚀 **NEW {proto} CONFIG**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⏰ Time: {t_now}\n"
                    f"🛰 Status: Online\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{link}`\n\n"
                    f"🆔 @favproxy | #daily"
                )
                
                try:
                    await client.send_message(MY_CHANNEL, text)
                    print(f"✈️ Sent: {proto}")
                    await asyncio.sleep(8) # فاصله برای جلوگیری از اسپم
                except Exception as e:
                    print(f"❌ Error: {e}")
                    await asyncio.sleep(30) # اگر محدود شدی استراحت کن

            print("😴 استراحت کوتاه...")
            await asyncio.sleep(40)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    from datetime import datetime, timedelta
    asyncio.run(main())
