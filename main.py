import os, re, asyncio, requests, json, time
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types, Button
from telethon.sessions import StringSession

# --- استخراج سکرت‌ها و بررسی سلامت آن‌ها ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
MY_CHANNEL = 'favproxy'
DB_FILE = "hunter_db.json"

async def debug_check():
    print("🔍 در حال بررسی تنظیمات ورودی...")
    if not API_ID or not API_HASH:
        print("❌ خطا: API_ID یا API_HASH در Secrets تعریف نشده است!")
        return False
    if not STRING_SESSION:
        print("❌ خطا: STRING_SESSION یافت نشد! سکرت‌ها را چک کنید.")
        return False
    if not BOT_TOKEN:
        print("❌ خطا: BOT_TOKEN یافت نشد! مطمئن شوید نام سکرت BOT_TOKEN است.")
        return False
    print("✅ تمام Secrets یافت شدند. شروع اتصال...")
    return True

def get_jalali_date():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    # فرمت درخواستی: ۱۴۰۴/۱۰/۱۵ ۱۲:۴۸
    # این یک مبدل ساده برای نمایش فرمت است
    return f"1404/10/15 {now.strftime('%H:%M')}" # در نسخه نهایی تابع تبدیل کامل قرار می‌گیرد

async def main():
    if not await debug_check(): return

    db = {"sent_messages": [], "configs_archive": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: db = json.load(f)
        except: print("⚠️ دیتابیس قبلی یافت نشد، یکی جدید ساخته می‌شود.")

    # تعریف کلاینت‌ها با مدیریت خطا
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    bot = TelegramClient('bot_session', int(API_ID), API_HASH)
    
    try:
        print("📡 در حال اتصال اکانت شکارچی...")
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ خطا: STRING_SESSION منقضی شده یا اشتباه است!")
            return

        print("🤖 در حال فعال‌سازی ربات (Bot API)...")
        await bot.start(bot_token=BOT_TOKEN)
        
        print("🚀 هر دو متصل شدند! شروع عملیات شکار...")
        
        j_time = get_jalali_date()
        # جستجو (محدود به ۲۰ مورد برای سرعت)
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
        ))

        sent_count = 0
        for m in search.messages:
            if sent_count >= 5: break
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
            for link in links:
                if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                
                proto = link.split('://')[0].upper()
                text = (f"🚀 **PREMIUM CONFIG**\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"🏷 Type: #{proto}\n"
                        f"⏰ Time: `{j_time}`\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"`{link.strip()}`\n\n"
                        f"🆔 @{MY_CHANNEL}")
                
                buttons = [[Button.inline("📋 کپی سریع", b"copy"), Button.url("🛰️ ورود به کانال", f"https://t.me/{MY_CHANNEL}")]]
                
                try:
                    sent = await bot.send_message(MY_CHANNEL, text, buttons=buttons)
                    db["configs_archive"].append({"link": link, "proto": proto, "time": j_time})
                    sent_count += 1
                    print(f"✅ یک کانفیگ {proto} ارسال شد.")
                    await asyncio.sleep(3)
                except Exception as e:
                    print(f"⚠️ ارور در ارسال به کانال: {e} (آیا ربات ادمین است؟)")

        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
        print("💾 دیتابیس بروزرسانی شد.")

    except Exception as e:
        print(f"❌ خطای کلی در سیستم: {str(e)}")
    finally:
        await client.disconnect()
        await bot.disconnect()
        print("🔌 قطع اتصال ایمن.")

if __name__ == "__main__":
    asyncio.run(main())
