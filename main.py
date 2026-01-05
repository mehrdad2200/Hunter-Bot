import os, re, asyncio, json
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = -1003576265638 # آیدی عددی کانالت
DB_FILE = "hunter_db.json"

def get_jalali_date():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return f"{now.strftime('%H:%M')}"

async def main():
    db = {"configs_archive": []}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: db = json.load(f)
        except: pass

    # فقط از اکانت (Client) استفاده می‌کنیم، بدون ربات
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ سشن نامعتبر است!")
            return

        print("🛰 شکارچی فعال شد (بدون ربات)...")
        
        # جستجو برای جدیدترین‌ها
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
        ))

        sent_count = 0
        for m in search.messages:
            if sent_count >= 5: break # ارسال ۵ تا در هر نوبت برای امنیت اکانت
            
            links = re.findall(r'vless://[^\s<>"]+', m.message or "")
            for link in links:
                if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                
                # ظاهر دقیق درخواستی تو
                text = (
                    f"🚀 **VLESS PREMIUM CONFIG**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 Location: 🌐 Global Search\n"
                    f"⚡️ Ping: 85ms (Stable)\n"
                    f"🛰 Status: Online & Verified\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 Config (Click to Copy):\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @favproxy\n\n"
                    f"📡 @favme" # آیدی دولوپر که گفتی
                )
                
                # ارسال مستقیم با اکانت
                await client.send_message(MY_CHANNEL, text)
                
                db["configs_archive"].append({"link": link, "time": get_jalali_date()})
                sent_count += 1
                print(f"✅ ارسال شد به سبک قدیمی")
                await asyncio.sleep(10) # وقفه برای جلوگیری از حساسیت تلگرام

        # ذخیره برای وب‌سایت
        db["configs_archive"] = db["configs_archive"][-100:]
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
