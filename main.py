import os, re, asyncio, json
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types, Button
from telethon.sessions import StringSession

# --- تنظیمات سیستمی ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()

# آیدی کانال مهرداد (عدد منفی برای جلوگیری از تداخل)
MY_CHANNEL = -1003576265638 

DB_FILE = "hunter_db.json"

def get_jalali_date():
    """تبدیل دقیق زمان به شمسی و فرمت درخواستی مهرداد"""
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
    return f"{jy}/{jm:02d}/{jd:02d} {now.strftime('%H:%M')}"

async def main():
    db = {"configs_archive": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: db = json.load(f)
        except: pass

    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    bot = TelegramClient('bot_session', int(API_ID), API_HASH)
    
    try:
        await client.connect()
        await bot.start(bot_token=BOT_TOKEN)
        print(f"✅ اتصال برقرار شد. در حال ارسال به کانال {MY_CHANNEL}")

        j_time = get_jalali_date()
        # جستجو در پیام‌های جهانی تلگرام
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=25
        ))

        sent_count = 0
        for m in search.messages:
            if sent_count >= 10: break # محدودیت ۱۰ ارسال در هر ۱۵ دقیقه
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
            
            for link in links:
                # چک کردن تکراری نبودن
                if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                
                proto = link.split('://')[0].upper()
                text = (f"🚀 **PREMIUM CONFIG FOUND**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🏷 **Type:** #{proto}\n"
                        f"⏰ **Time:** `{j_time}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 **Config:**\n\n"
                        f"`{link.strip()}`\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 @favproxy\n"
                        f"🛡️ MEHRDAD HUNTER 🛰️")
                
                buttons = [[Button.inline("📋 کپی سریع", b"copy"), Button.url("🛰️ کانال ما", "https://t.me/favproxy")]]
                
                try:
                    # ارسال با ربات (دکمه‌دار)
                    await bot.send_message(MY_CHANNEL, text, buttons=buttons)
                    db["configs_archive"].append({"link": link, "proto": proto, "time": j_time})
                    sent_count += 1
                    print(f"🚀 کانفیگ {proto} با موفقیت ارسال شد.")
                    await asyncio.sleep(5) # وقفه برای جلوگیری از فلود
                except Exception as e:
                    print(f"⚠️ خطا در ارسال: {e}")

        # ذخیره ۱۰۰ تای آخر در دیتابیس برای وب‌سایت
        db["configs_archive"] = db["configs_archive"][-100:]
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

    except Exception as e:
        print(f"❌ خطای کلی: {e}")
    finally:
        await client.disconnect()
        await bot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
