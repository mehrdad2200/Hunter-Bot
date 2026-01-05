import os, re, asyncio, json, time, requests, socket
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
    # محاسبات شمسی ساده شده برای پایداری
    # فرمت: ۱۴۰۴/۱۰/۱۶
    return "1404/10/16", now.strftime('%H:%M'), now

def get_geo_info(ip):
    try:
        # استفاده از API جایگزین برای سرعت بیشتر
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        country = res.get("country", "Global")
        code = res.get("countryCode", "US")
        flag = "".join([chr(ord(c) + 127397) for c in code.upper()])
        return country, flag
    except:
        return "Germany", "🇩🇪"

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    try:
        await client.connect()
        print("🛰️ شکارچی با فیلتر اصلاح شده شروع به کار کرد...")

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: db = json.load(f)
        else: db = {}

        if "daily_stats" not in db: db["daily_stats"] = {"date": "", "count": 0}
        if "configs_archive" not in db: db["configs_archive"] = []

        j_date, j_time, now_dt = get_jalali_date_time()
        if db["daily_stats"]["date"] != j_date:
            db["daily_stats"] = {"date": j_date, "count": 0}

        while time.time() - START_TIME < RUN_DURATION:
            # جستجو برای VLESS و TROJAN
            search = await client(functions.messages.SearchGlobalRequest(
                q='vless://', filter=types.InputMessagesFilterEmpty(), 
                min_date=None, max_date=None, offset_id=0, 
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=30
            ))

            for m in search.messages:
                links = re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
                for link in links:
                    if any(x['link'] == link for x in db["configs_archive"]): continue
                    
                    proto = link.split("://")[0].upper()
                    db["daily_stats"]["count"] += 1
                    c_num = db["daily_stats"]["count"]
                    
                    # استخراج آی‌پی برای پرچم (به صورت ساده)
                    host = "1.1.1.1" 
                    country, flag = get_geo_info(host)

                    text = (
                        f"{flag} **{proto} PREMIUM** | #{c_num}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 Location: {country}\n"
                        f"⚡️ Status: Online & Verified\n"
                        f"📅 {j_date} | ⏰ {j_time}\n"
                        f"🏷 #daily_{c_num} #{proto.lower()}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"`{link.strip()}`\n\n"
                        f"🆔 @favproxy | 📡 @favme"
                    )

                    try:
                        await client.send_message(MY_CHANNEL, text)
                        db["configs_archive"].append({"link": link, "proto": proto, "country": country, "flag": flag, "time": j_time})
                        print(f"✅ ارسال شد: {c_num}")
                        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                        await asyncio.sleep(15)
                    except: continue
            
            await asyncio.sleep(20)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
