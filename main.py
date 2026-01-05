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
        # استخراج آی‌پی یا دامنه از لینک
        ip_match = re.search(r'@([^:/]+)', link)
        if not ip_match: ip_match = re.search(r'://([^:/]+)', link)
        
        if ip_match:
            host = ip_match.group(1)
            res = requests.get(f"http://ip-api.com/json/{host}", timeout=3).json()
            if res.get("status") == "success":
                country = res.get("country", "Global")
                code = res.get("countryCode", "US")
                flag = "".join([chr(ord(c) + 127397) for c in code.upper()])
                return country, flag
    except: pass
    return "Germany", "🇩🇪"

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    try:
        await client.connect()
        print("🛰️ شکارچی در حال جستجوی عمیق...")

        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: db = json.load(f)
        else: db = {}

        if "daily_stats" not in db: db["daily_stats"] = {"date": "", "count": 0}
        if "configs_archive" not in db: db["configs_archive"] = []

        j_date, j_time, now_dt = get_jalali_date_time()
        if db["daily_stats"]["date"] != j_date:
            db["daily_stats"] = {"date": j_date, "count": 0}

        while time.time() - START_TIME < RUN_DURATION:
            search = await client(functions.messages.SearchGlobalRequest(
                q='vless://', filter=types.InputMessagesFilterEmpty(), 
                min_date=None, max_date=None, offset_id=0, 
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=30
            ))

            for m in search.messages:
                found_links = re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
                for link in found_links:
                    clean_link = link.strip()
                    if any(x['link'] == clean_link for x in db["configs_archive"]): continue
                    
                    proto = clean_link.split("://")[0].upper()
                    db["daily_stats"]["count"] += 1
                    c_num = db["daily_stats"]["count"]
                    
                    # دریافت لوکیشن واقعی از روی لینک
                    country, flag = get_geo_info(clean_link)

                    # 💎 متن نهایی با کد کامل
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
                        db["configs_archive"].append({
                            "link": clean_link, 
                            "proto": proto, 
                            "country": country, 
                            "flag": flag, 
                            "time": j_time
                        })
                        print(f"✅ ارسال موفق: {proto} شماره {c_num}")
                        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                        await asyncio.sleep(15) # وقفه برای امنیت اکانت
                    except Exception as e:
                        print(f"❌ خطا در ارسال: {e}")
                        continue
            
            await asyncio.sleep(30) # وقفه بین دورهای جستجو

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
