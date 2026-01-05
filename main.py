import os, re, asyncio, json, time, requests
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = -1003576265638 

DB_FILE = "hunter_db.json"
START_TIME = time.time()
RUN_DURATION = 300 

def get_jalali_date_time():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return "1404/10/16", now.strftime('%H:%M'), now

def get_geo_info(link):
    try:
        # استخراج هاست برای تشخیص کشور
        host_match = re.search(r'@([^:/?#]+)', link)
        if not host_match: host_match = re.search(r'://([^:/?#]+)', link)
        if host_match:
            host = host_match.group(1)
            res = requests.get(f"http://ip-api.com/json/{host}", timeout=2).json()
            if res.get("status") == "success":
                return res.get("country", "Global"), "".join([chr(ord(c) + 127397) for c in res.get("countryCode", "US").upper()])
    except: pass
    return "Germany", "🇩🇪"

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    try:
        await client.connect()
        print("🚀 شکارچی با قدرت کامل بیدار شد...")

        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f: db = json.load(f)
            except: db = {}
        else: db = {}

        if "daily_stats" not in db: db["daily_stats"] = {"date": "", "count": 0}
        if "configs_archive" not in db: db["configs_archive"] = []

        j_date, j_time, now_dt = get_jalali_date_time()
        if db["daily_stats"]["date"] != j_date:
            db["daily_stats"] = {"date": j_date, "count": 0}

        # حلقه تا ۵ دقیقه
        while time.time() - START_TIME < RUN_DURATION:
            # جستجو برای انواع پروتکل‌ها
            for query in ['vless://', 'trojan://']:
                search = await client(functions.messages.SearchGlobalRequest(
                    q=query, filter=types.InputMessagesFilterEmpty(), 
                    min_date=None, max_date=None, offset_id=0, 
                    offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=50
                ))

                for m in search.messages:
                    # تفکیک لینک‌ها و اطمینان از کامل بودن متن
                    full_msg = m.message or ""
                    # اگر متن کوتاه بود، تلاش برای گرفتن پیام کامل
                    if len(full_msg) < 50:
                        try:
                            full_msg = (await client.get_messages(m.peer_id, ids=m.id)).message
                        except: continue

                    links = re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"]+', full_msg)
                    for link in links:
                        clean_link = link.strip()
                        # فیلتر تکراری و لینک‌های ناقص
                        if len(clean_link) < 20 or any(x['link'] == clean_link for x in db["configs_archive"]):
                            continue
                        
                        proto = clean_link.split("://")[0].upper()
                        db["daily_stats"]["count"] += 1
                        c_num = db["daily_stats"]["count"]
                        
                        country, flag = get_geo_info(clean_link)

                        text = (
                            f"{flag} **{proto} PREMIUM** | #{c_num}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📍 Location: {country}\n"
                            f"⚡️ Status: Online & Verified\n"
                            f"📅 {j_date} | ⏰ {j_time}\n"
                            f"🏷 #daily_{c_num} #{proto.lower()}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🔗 **Config (Click to Copy):**\n\n"
                            f"`{clean_link}`\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🆔 @favproxy | 📡 @favme"
                        )

                        try:
                            await client.send_message(MY_CHANNEL, text)
                            db["configs_archive"].append({"link": clean_link, "proto": proto, "country": country, "flag": flag, "time": j_time})
                            print(f"✅ ارسال شد: {proto} {c_num}")
                            # ذخیره در هر مرحله
                            with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                            await asyncio.sleep(10) # وقفه برای جلوگیری از بن شدن
                        except Exception as e:
                            print(f"❌ خطا در ارسال: {e}")

            print("🔄 در حال استراحت کوتاه برای دور بعدی جستجو...")
            await asyncio.sleep(30)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
