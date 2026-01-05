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
LIMIT_TIME = 300  # ۵ دقیقه فعالیت

# منابع کمکی گیت‌هاب (برای وقتی تلگرام خالی است)
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

def get_jalali_now():
    # تاریخ و ساعت ساده شده برای پایداری
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return "1404/10/16", now.strftime('%H:%M'), now

def get_geo_and_ping(link):
    try:
        # استخراج هاست
        match = re.search(r'@([^:/?#]+)', link) or re.search(r'://([^:/?#]+)', link)
        if not match: return None
        host = match.group(1)
        
        # تست پینگ (سریع)
        start = time.time()
        socket.create_connection((host, 443), timeout=1.5).close()
        ping = int((time.time() - start) * 1000)
        
        # دریافت پرچم
        res = requests.get(f"http://ip-api.com/json/{host}?fields=country,countryCode", timeout=2).json()
        flag = "".join([chr(ord(c) + 127397) for c in res.get("countryCode", "XX").upper()])
        return {"country": res.get("country", "Unknown"), "flag": flag, "ping": ping}
    except: 
        return None

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ ربات متصل شد. شروع عملیات...")

        # لود دیتابیس با جلوگیری از ارور
        db = {"archive": [], "sent_msgs": [], "daily": {"date": "", "count": 0}}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    old = json.load(f)
                    db.update(old)
            except: pass
            
        # اطمینان از وجود کلیدهای ضروری
        if "sent_msgs" not in db: db["sent_msgs"] = []
        if "daily" not in db: db["daily"] = {"date": "", "count": 0}

        j_date, j_time, now_dt = get_jalali_now()
        
        # ریست روزانه
        if db["daily"].get("date") != j_date:
            db["daily"] = {"date": j_date, "count": 0}

        # --- حلقه اصلی ۵ دقیقه‌ای ---
        while time.time() - START_TIME < LIMIT_TIME:
            links_pool = []
            
            # ۱. دریافت از گیت‌هاب
            for url in GITHUB_SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    links_pool.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            # ۲. دریافت از تلگرام (بخش اصلاح شده)
            for kw in ['vless://', 'trojan://']:
                try:
                    # ✅ اینجا ارور شما رفع شد: اضافه کردن پارامترهای اجباری
                    res = await client(functions.messages.SearchGlobalRequest(
                        q=kw, 
                        filter=types.InputMessagesFilterEmpty(), 
                        min_date=None, 
                        max_date=None, 
                        offset_rate=0, 
                        offset_peer=types.InputPeerEmpty(), 
                        offset_id=0, 
                        limit=30
                    ))
                    for m in res.messages:
                        if m.message: links_pool.extend(re.findall(r'(?:vless|trojan|ss)://[^\s<>"]+', m.message))
                except Exception as e:
                    print(f"⚠️ خطا در جستجوی تلگرام: {e}")
                    continue

            # پردازش و ارسال
            unique_links = list(set(links_pool))
            for link in unique_links:
                if time.time() - START_TIME > LIMIT_TIME: break
                if any(x['link'] == link for x in db["archive"]): continue

                # تست کیفیت
                geo = get_geo_and_ping(link)
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
                    f"🔗 **Click to Copy:**\n`{link}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @favproxy | 📡 @favme"
                )

                try:
                    sent = await client.send_message(MY_CHANNEL, text)
                    print(f"✅ ارسال شد: {proto} #{c_num}")
                    
                    db["archive"].append({"link": link})
                    db["sent_msgs"].append({"id": sent.id, "time": now_dt.isoformat()})
                    
                    # پاکسازی خودکار پیام‌های ۲۴ ساعت قبل از کانال
                    cutoff = now_dt - timedelta(hours=24)
                    for msg in db["sent_msgs"][:]:
                        if datetime.fromisoformat(msg["time"]) < cutoff:
                            try:
                                await client.delete_messages(MY_CHANNEL, [msg["id"]])
                                db["sent_msgs"].remove(msg)
                                print(f"🗑 پیام قدیمی حذف شد: {msg['id']}")
                            except: pass

                    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                    await asyncio.sleep(10)
                except: continue
            
            print("🔄 جستجوی مجدد...")
            await asyncio.sleep(20)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
