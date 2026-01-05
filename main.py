import os, re, asyncio, json, time, requests, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = -1003576265638 
DB_FILE = "hunter_db.json"
START_TIME = time.time()
LIMIT_TIME = 300  # ۵ دقیقه فعالیت اجباری

GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

def get_jalali_date_time():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return "1404/10/16", now.strftime('%H:%M'), now

def get_geo_and_ping(link):
    try:
        host_match = re.search(r'@([^:/?#]+)', link) or re.search(r'://([^:/?#]+)', link)
        if not host_match: return None
        host = host_match.group(1)
        start = time.time()
        socket.create_connection((host, 443), timeout=1.5).close()
        ping = int((time.time() - start) * 1000)
        res = requests.get(f"http://ip-api.com/json/{host}?fields=status,country,countryCode", timeout=2).json()
        if res.get("status") == "success":
            code = res.get("countryCode", "US")
            flag = "".join([chr(ord(c) + 127397) for c in code.upper()])
            return {"country": res.get("country"), "flag": flag, "ping": ping}
    except: pass
    return None

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        # لود ایمن دیتابیس
        db = {"archive": [], "sent_msgs": [], "daily": {"date": "", "count": 0, "start_members": 0}}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    old_db = json.load(f)
                    for key in db:
                        if key in old_db: db[key] = old_db[key]
            except: pass

        j_date, j_time, now_dt = get_jalali_date_time()
        
        # شروع حلقه ۵ دقیقه‌ای
        print(f"🚀 شروع شکار ۵ دقیقه‌ای...")
        while time.time() - START_TIME < LIMIT_TIME:
            all_links = []
            
            # ۱. گرفتن از گیت‌هاب
            for url in GITHUB_SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    all_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            # ۲. گرفتن از تلگرام
            for kw in ['vless://', 'trojan://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), limit=20))
                    for m in res.messages:
                        if m.message: all_links.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message))
                except: continue

            # حذف تکراری‌ها در این دور
            unique_links = list(set(all_links))
            
            for link in unique_links:
                # چک کردن زمان باقیمانده
                if time.time() - START_TIME > LIMIT_TIME: break
                
                # اگر قبلاً نفرستادیم
                if any(x['link'] == link for x in db["archive"]): continue
                
                geo = get_geo_and_ping(link)
                # فیلتر پینگ را کمی آزادتر کردم (۱۵۰۰ms) تا حتماً ارسال داشته باشی
                if not geo or geo['ping'] > 1500: continue
                
                db["daily"]["count"] += 1
                c_num = db["daily"]["count"]
                proto = link.split('://')[0].upper()
                
                text = (
                    f"{geo['flag']} **{proto} PREMIUM** | #{c_num}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 Location: {geo['country']}\n"
                    f"⚡️ Ping: {geo['ping']}ms\n"
                    f"📅 {j_date} | ⏰ {j_time}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{link}`\n\n"
                    f"🆔 @favproxy | 📡 @favme"
                )
                
                try:
                    sent = await client.send_message(MY_CHANNEL, text)
                    db["archive"].append({"link": link})
                    db["sent_msgs"].append({"id": sent.id, "time": now_dt.isoformat()})
                    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                    print(f"✅ ارسال شد: {proto} #{c_num}")
                    await asyncio.sleep(10) # وقفه کوتاه بین ارسال‌ها
                except: continue

            print("🔄 در حال جستجوی مجدد برای لینک‌های تازه‌تر...")
            await asyncio.sleep(20) # صبر کن تا دیتای جدید در تلگرام/گیت‌هاب بیاید

    finally:
        await client.disconnect()
        print(f"⏱ زمان ۵ دقیقه به پایان رسید. کل سرورهای ارسال شده: {db['daily']['count']}")

if __name__ == "__main__":
    asyncio.run(main())
