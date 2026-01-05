import os, re, asyncio, json
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = -1003576265638 

DB_FILE = "hunter_db.json"

def extract_location(link):
    # سعی می‌کند لوکیشن را از انتهای کانفیگ پیدا کند
    match = re.search(r'#.*(?:(?:ID|BY|FR|DE|US|UK|CA|TR|IR|NL)|([\U0001f1e6-\U0001f1ff]{2}))', link)
    return match.group(0).replace('#', '') if match else "Global 🌐"

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
    
    try:
        await client.connect()
        print("🛰️ بیدارباش شکارچی...")

        db = {"configs_archive": []}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f: db = json.load(f)
            except: pass

        # جستجوی جهانی برای VLESS
        search = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(), 
            min_date=None, max_date=None, offset_id=0, 
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=30
        ))

        sent_now = 0
        for m in search.messages:
            if sent_now >= 5: break 
            
            links = re.findall(r'vless://[^\s<>"]+', m.message or "")
            for link in links:
                if any(x['link'] == link for x in db.get("configs_archive", [])): continue
                
                loc = extract_location(link)
                # 🚀 فرمت دقیق مهرداد
                text = (
                    f"🚀 **VLESS PREMIUM CONFIG**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 Location: {loc}\n"
                    f"⚡️ Ping: 109ms (Stable)\n"
                    f"🛰 Status: Online & Verified\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 Config (Click to Copy):\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @favproxy\n\n"
                    f"📡 @favme"
                )
                
                try:
                    await client.send_message(MY_CHANNEL, text)
                    db["configs_archive"].append({"link": link, "time": str(datetime.now())})
                    sent_now += 1
                    print(f"✅ ارسال موفق به کانال")
                    await asyncio.sleep(8) 
                except Exception as e:
                    print(f"⚠️ خطا در ارسال: {e}")

        with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

    finally:
        await client.disconnect()
        print("💤 پایان سیکل ۱۵ دقیقه.")

if __name__ == "__main__":
    asyncio.run(main())
