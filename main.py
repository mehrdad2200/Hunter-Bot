import os, re, asyncio, json
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# تنظیمات
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = -1003576265638 # آیدی عددی کانالت

DB_FILE = "hunter_db.json"

async def main():
    # اتصال فقط با اکانت (بدون نیاز به BOT_TOKEN)
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ ارور: سشن نامعتبر است!")
            return

        print("📡 سرور بیدار شد. در حال شکار کانفیگ...")

        db = {"configs_archive": []}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f: db = json.load(f)
            except: pass

        # جستجوی جهانی
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
        ))

        sent_count = 0
        for m in search.messages:
            if sent_count >= 5: break # ارسال 5 کانفیگ در هر بیداری
            
            links = re.findall(r'vless://[^\s<>"]+', m.message or "")
            for link in links:
                if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                
                # فرمت درخواستی مهرداد
                text = (
                    f"🚀 **VLESS PREMIUM CONFIG**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 Location: 🌐 Global Server\n"
                    f"⚡️ Ping: 109ms (Stable)\n"
                    f"🛰 Status: Online & Verified\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 Config (Click to Copy):\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @favproxy\n\n"
                    f"📡 @favme"
                )
                
                # ارسال مستقیم با اکانت خودت
                await client.send_message(MY_CHANNEL, text)
                
                db["configs_archive"].append({"link": link, "time": str(datetime.now())})
                sent_count += 1
                print(f"✅ کانفیگ ارسال شد.")
                await asyncio.sleep(5)

        # نگهداری آرشیو برای وب‌سایت
        db["configs_archive"] = db["configs_archive"][-100:]
        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await client.disconnect()
        print("💤 سرور خاموش شد تا 15 دقیقه دیگر...")

if __name__ == "__main__":
    asyncio.run(main())
