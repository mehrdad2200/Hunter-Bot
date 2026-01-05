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
RUN_DURATION = 300  # 5 دقیقه فعال بماند

NUM_EMOJI = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def get_jalali_date_time():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    gy, gm, gd = now.year, now.month, now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = gy - 621
    days = (gy - 1) * 365 + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + g_d_m[gm - 1] + gd
    jy_all_days = days - ((jy + 620) * 365 + (jy + 620) // 4 - (jy + 620) // 100 + (jy + 620) // 400)
    if jy_all_days > 286:
        jy += 1; jy_all_days -= 286
    else:
        jy_all_days += 79
    if jy_all_days <= 186:
        jm = 1 + (jy_all_days - 1) // 31
        jd = 1 + (jy_all_days - 1) % 31
    else:
        jm = 7 + (jy_all_days - 187) // 30
        jd = 1 + (jy_all_days - 187) % 30
    return f"{jy}/{jm:02d}/{jd:02d}", now.strftime('%H:%M'), now

def get_geo_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=country,countryCode", timeout=2)
        if response.status_code == 200:
            data = response.json()
            country = data.get("country", "Unknown")
            code = data.get("countryCode", "XX")
            flag = "".join([chr(ord(c) + 127397) for c in code.upper()]) if code != "XX" else "🌐"
            return country, flag
    except: pass
    return "Global", "🌐"

def check_ping(host):
    try:
        target = host.split(":")[0]
        start = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((target, 80))
        s.close()
        return int((time.time() - start) * 1000)
    except: return None

def number_to_emoji(n):
    return "".join(NUM_EMOJI[int(d)] for d in str(n)) if str(n).isdigit() else ""

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        print("🛰️ نسخه جدید شکارچی فعال شد...")

        # --- بخش اصلاح شده دیتابیس (رفع ارور) ---
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f: db = json.load(f)
            except: db = {}
        else:
            db = {}

        # تزریق کلیدهای جدید اگر وجود نداشته باشند (Fix KeyError)
        if "daily_stats" not in db:
            db["daily_stats"] = {"date": "", "count": 0, "start_members": 0}
        if "configs_archive" not in db:
            db["configs_archive"] = []
        if "sent_messages" not in db:
            db["sent_messages"] = []
        # ----------------------------------------

        # دریافت آمار اعضا
        try:
            full_channel = await client(functions.channels.GetFullChannelRequest(MY_CHANNEL))
            current_members = full_channel.full_chat.participants_count
        except: current_members = 0

        j_date, j_time_str, now_dt = get_jalali_date_time()

        # بررسی تغییر روز و گزارش‌دهی
        if db["daily_stats"]["date"] != j_date:
            if db["daily_stats"]["date"]: # گزارش دیروز
                prev_count = db["daily_stats"]["count"]
                start_m = db["daily_stats"].get("start_members", current_members)
                diff = current_members - start_m
                sign = "+" if diff >= 0 else ""
                
                rep = (f"📊 **گزارش عملکرد ۲۴ ساعت گذشته**\n"
                       f"📅 تاریخ بسته شده: {db['daily_stats']['date']}\n"
                       f"━━━━━━━━━━━━━━━━━━━━\n"
                       f"✅ تعداد شکار: {prev_count}\n"
                       f"👥 رشد کانال: {sign}{diff} نفر\n"
                       f"━━━━━━━━━━━━━━━━━━━━\n"
                       f"🛡️ MEHRDAD HUNTER")
                try: await client.send_message(MY_CHANNEL, rep)
                except: pass
            
            # شروع روز جدید
            db["daily_stats"] = {"date": j_date, "count": 0, "start_members": current_members}
            with open(DB_FILE, "w") as f: json.dump(db, f, indent=4) # ذخیره فوری

        # شروع حلقه ۵ دقیقه‌ای
        print("⏳ شروع سیکل جستجو (۵ دقیقه)...")
        while time.time() - START_TIME < RUN_DURATION:
            
            # جستجو
            try:
                search = await client(functions.messages.SearchGlobalRequest(
                    q='vless://', filter=types.InputMessagesFilterEmpty(), 
                    min_date=None, max_date=None, offset_id=0, 
                    offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
                ))
            except Exception as e:
                print(f"⚠️ خطای جستجو: {e}")
                await asyncio.sleep(10)
                continue

            for m in search.messages:
                if time.time() - START_TIME > RUN_DURATION: break

                links = re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
                for link in links:
                    if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                    
                    try:
                        # تحلیل لینک
                        proto = link.split("://")[0].upper()
                        if "@" in link: part = link.split("@")[1]
                        else: part = link.split("://")[1]
                        host = part.split(":")[0]
                        
                        # پینگ و کشور
                        ping = check_ping(host)
                        if not ping or ping > 1500: continue # فیلتر کیفیت
                        
                        country, flag = get_geo_info(host)
                        
                        # افزایش شمارنده
                        db["daily_stats"]["count"] += 1
                        count_num = db["daily_stats"]["count"]
                        
                        # متن نهایی
                        text = (
                            f"{flag} **{proto} PREMIUM CONFIG** | {number_to_emoji(count_num)}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📍 Location: {country}\n"
                            f"⚡️ Ping: {ping}ms\n"
                            f"📅 Date: {j_date} | ⏰ {j_time_str}\n"
                            f"🏷 Tag: #{proto.lower()} #{country.replace(' ', '_')}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🔗 Config (Click to Copy):\n\n"
                            f"`{link.strip()}`\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🆔 @favproxy\n"
                            f"📡 @favme"
                        )
                        
                        await client.send_message(MY_CHANNEL, text)
                        print(f"✅ ارسال شد: {proto} | {country}")
                        
                        db["configs_archive"].append({"link": link, "time": now_dt.isoformat()})
                        db["configs_archive"] = db["configs_archive"][-100:] # حفظ حجم دیتابیس
                        
                        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                        await asyncio.sleep(8)

                    except Exception as inner_e:
                        # خطاهای کوچک را رد کن تا برنامه قطع نشود
                        continue

            await asyncio.sleep(5)

    except Exception as e:
        print(f"❌ خطای اصلی: {e}")
    finally:
        await client.disconnect()
        print("💤 پایان عملیات.")

if __name__ == "__main__":
    asyncio.run(main())
