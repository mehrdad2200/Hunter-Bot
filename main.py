import os, re, asyncio, requests, json, time, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types, Button
from telethon.sessions import StringSession

# --- تنظیمات (Secrets) ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

DB_FILE = "hunter_db.json"

def get_jalali_date():
    """محاسبه دقیق تاریخ شمسی و زمان تهران"""
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    gy, gm, gd = now.year, now.month, now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = gy - 621
    days = (gy - 1) * 365 + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + g_d_m[gm - 1] + gd
    jy_all_days = days - ((jy + 620) * 365 + (jy + 620) // 4 - (jy + 620) // 100 + (jy + 620) // 400)
    if jy_all_days > 286:
        jy += 1
        jy_all_days -= 286
    else:
        jy_all_days += 79
    if jy_all_days <= 186:
        jm = 1 + (jy_all_days - 1) // 31
        jd = 1 + (jy_all_days - 1) % 31
    else:
        jm = 7 + (jy_all_days - 187) // 30
        jd = 1 + (jy_all_days - 187) % 30
    return f"{jy}/{jm:02d}/{jd:02d} {now.strftime('%H:%M')}"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {"sent_messages": [], "configs_archive": [], "daily_stats": {"count": 0, "last_report": ""}}

def save_db(data):
    # نگهداری ۱۰۰ کانفیگ آخر در آرشیو
    data["configs_archive"] = data["configs_archive"][-100:]
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

async def main():
    db = load_db()
    j_time = get_jalali_date()
    
    # تعریف کلاینت‌ها
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    
    try:
        await client.connect()
        # رفع ارور قبلی با اضافه کردن await
        await bot.start(bot_token=BOT_TOKEN) 
        
        print("🛰️ شکارچی و ربات با موفقیت فعال شدند...")

        # ۱. پاکسازی پیام‌های قدیمی کانال (بیش از ۲۴ ساعت)
        now_dt = datetime.now()
        rem_msgs = []
        for m in db["sent_messages"]:
            if now_dt - datetime.fromisoformat(m["time"]) < timedelta(hours=24):
                rem_msgs.append(m)
            else: 
                try: await client.delete_messages(MY_CHANNEL, m["id"])
                except: pass
        db["sent_messages"] = rem_msgs

        # ۲. جستجو برای کانفیگ‌های جدید
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=40
        ))
        
        count = 0
        for m in search.messages:
            if count >= 10: break # محدودیت ارسال در هر بار اجرا
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
            
            for link in links:
                if any(x['link'] == link for x in db["configs_archive"]): continue
                
                proto = link.split('://')[0].upper()
                text = (
                    f"🚀 **PREMIUM CONFIG FOUND**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏷 **Type:** #{proto}\n"
                    f"⏰ **Time:** `{j_time}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 **Config:**\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @{MY_CHANNEL}\n"
                    f"🛡️ {BRAND}"
                )
                
                # دکمه‌های شیشه‌ای
                buttons = [
                    [Button.inline("📋 کپی سرور", b"copy"), Button.url("🔍 تست سرعت", f"https://t.me/{MY_CHANNEL}")],
                    [Button.inline(f"🕒 {j_time}", b"time")]
                ]
                
                # ارسال توسط ربات
                sent = await bot.send_message(MY_CHANNEL, text, buttons=buttons, link_preview=False)
                
                # ذخیره در دیتابیس
                db["sent_messages"].append({"id": sent.id, "time": now_dt.isoformat()})
                db["configs_archive"].append({
                    "link": link, 
                    "proto": proto, 
                    "time": j_time, 
                    "country": "Global", # برای نسخه ساده
                    "flag": "🌐"
                })
                db["daily_stats"]["count"] += 1
                count += 1
                await asyncio.sleep(5)

    except Exception as e:
        print(f"❌ خطای اجرا: {e}")
    finally:
        save_db(db)
        await client.disconnect()
        await bot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
