import os, re, asyncio, json, time, requests, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = -1003576265638  # آیدی عددی کانال

DB_FILE = "hunter_db.json"
START_TIME = time.time()
RUN_DURATION = 300  # 5 دقیقه به ثانیه

# تبدیل اعداد به ایموجی برای شمارنده
NUM_EMOJI = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def get_jalali_date_time():
    """محاسبه دقیق زمان و تاریخ شمسی ایران"""
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
        data = response.json()
        country = data.get("country", "Unknown")
        code = data.get("countryCode", "XX")
        # تبدیل کد کشور به پرچم
        flag = "".join([chr(ord(c) + 127397) for c in code.upper()]) if code != "XX" else "🌐"
        return country, flag
    except:
        return "Global", "🌐"

def check_ping(host):
    try:
        # استخراج IP یا Host از لینک (ساده‌سازی شده)
        target = host.split(":")[0]
        start = time.time()
        # تلاش برای اتصال TCP (چون پینگ ICMP ممکن است بسته باشد)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((target, 80))
        s.close()
        ping_ms = int((time.time() - start) * 1000)
        return ping_ms
    except:
        return None

def number_to_emoji(n):
    return "".join(NUM_EMOJI[int(d)] for d in str(n))

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        print("🛰️ شکارچی فعال شد (حالت ۵ دقیقه‌ای)...")

        # لود یا ساخت دیتابیس
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: db = json.load(f)
        else:
            db = {
                "configs_archive": [], 
                "sent_messages": [], 
                "daily_stats": {"date": "", "count": 0, "start_members": 0}
            }

        # گرفتن اطلاعات کانال برای آمار اعضا
        try:
            full_channel = await client(functions.channels.GetFullChannelRequest(MY_CHANNEL))
            current_members = full_channel.full_chat.participants_count
        except:
            current_members = 0

        # ریست کردن آمار روزانه اگر روز عوض شده
        j_date, j_time_str, now_dt = get_jalali_date_time()
        if db["daily_stats"]["date"] != j_date:
            # گزارش پایان روز قبل (اگر ارسال نشده باشد و الان ۰۰:۰۰ یا بعدش باشد)
            if db["daily_stats"]["date"]:
                diff = current_members - db["daily_stats"].get("start_members", current_members)
                sign = "+" if diff >= 0 else ""
                report_text = (
                    f"📊 **گزارش عملکرد روزانه**\n"
                    f"📅 تاریخ: {db['daily_stats']['date']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ کانفیگ‌های شکار شده: {db['daily_stats']['count']} عدد\n"
                    f"👥 تغییرات اعضا: {sign}{diff}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🛡️ MEHRDAD HUNTER"
                )
                await client.send_message(MY_CHANNEL, report_text)
            
            # شروع روز جدید
            db["daily_stats"] = {"date": j_date, "count": 0, "start_members": current_members}

        # --- چرخه اصلی (تا ۵ دقیقه ادامه دارد) ---
        while time.time() - START_TIME < RUN_DURATION:
            
            # ۱. پاکسازی پیام‌های قدیمی (فقط اگر پیام جدید اضافه شد در ادامه)
            # (عملیات پاکسازی را در دیتابیس مارک می‌کنیم اما حذف واقعی را مدیریت شده انجام می‌دهیم)
            cutoff_time = now_dt - timedelta(hours=24)
            db["sent_messages"] = [msg for msg in db["sent_messages"] if datetime.fromisoformat(msg["time"]) > cutoff_time]
            # نکته: حذف فیزیکی از تلگرام را جداگانه انجام می‌دهیم تا سرعت گرفته نشود.

            # ۲. جستجو
            search = await client(functions.messages.SearchGlobalRequest(
                q='vless://', filter=types.InputMessagesFilterEmpty(), 
                min_date=None, max_date=None, offset_id=0, 
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=15
            ))

            for m in search.messages:
                # چک کردن زمان باقی‌مانده
                if time.time() - START_TIME > RUN_DURATION: break

                links = re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
                for link in links:
                    if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                    
                    # تحلیل لینک
                    proto = link.split("://")[0].upper()
                    # استخراج هاست برای پینگ و لوکیشن
                    try:
                        if "@" in link: parts = link.split("@")[1]
                        else: parts = link.split("://")[1]
                        host = parts.split(":")[0]
                    except: continue

                    # تست پینگ (فیلتر کیفیت)
                    ping = check_ping(host)
                    if not ping or ping > 1500: continue # پینگ بالای ۱۵۰۰ یا تایم‌اوت رد می‌شود

                    # دریافت اطلاعات مکانی
                    country, flag = get_geo_info(host)

                    # افزایش شمارنده روزانه
                    db["daily_stats"]["count"] += 1
                    daily_count = db["daily_stats"]["count"]

                    # ساخت متن پیام
                    text = (
                        f"{flag} **{proto} PREMIUM CONFIG** | {number_to_emoji(daily_count)}\n"
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

                    try:
                        sent_msg = await client.send_message(MY_CHANNEL, text)
                        print(f"✅ ارسالی شماره {daily_count}: {proto} - {country}")
                        
                        # ذخیره در دیتابیس
                        msg_time_iso = now_dt.isoformat()
                        db["configs_archive"].append({"link": link, "time": msg_time_iso})
                        db["sent_messages"].append({"id": sent_msg.id, "time": msg_time_iso})
                        
                        # ذخیره فوری دیتابیس برای جلوگیری از پریدن اطلاعات
                        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
                        
                        await asyncio.sleep(10) # وقفه بین ارسال‌ها
                    except Exception as e:
                        print(f"⚠️ خطا در ارسال: {e}")

            await asyncio.sleep(5) # وقفه کوتاه قبل از جستجوی مجدد در همین بازه ۵ دقیقه‌ای

    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        # پاکسازی پیام‌های خیلی قدیمی از کانال (در پایان اجرا)
        try:
            cutoff = datetime.now() - timedelta(hours=24)
            # لیست پیام‌هایی که باید پاک شوند (که در دیتابیس نیستند ولی در کانال مانده‌اند)
            # این منطق نیاز به هندلینگ دقیق دارد، فعلاً به لیست sent_messages اعتماد می‌کنیم
            # (در کدهای آینده می‌توان کامل‌تر کرد)
            pass 
        except: pass
        
        await client.disconnect()
        print("💤 پایان عملیات ۵ دقیقه‌ای.")

if __name__ == "__main__":
    asyncio.run(main())
