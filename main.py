import os, re, asyncio, requests, random
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError

# --- تنظیمات مهرداد هنتر ---
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')
MY_CHANNEL = 'favproxy'

async def main():
    # چک کردن خالی نبودن مقادیر
    if not API_ID or not STRING_SESSION:
        print("❌ خطا: متغیرهای API_ID یا STRING_SESSION در Secrets تعریف نشده‌اند!")
        return

    client = TelegramClient(StringSession(STRING_SESSION.strip()), int(API_ID), API_HASH)
    
    try:
        print("📡 در حال تلاش برای اتصال به تلگرام...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ خطا: سشن معتبر نیست یا منقضی شده است!")
            return

        print("🚀 اتصال موفق! در حال جمع‌آوری و ارسال...")
        
        # کد جمع‌آوری پروکسی
        res = requests.get("https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless", timeout=10).text
        proxies = re.findall(r'vless://[^\s<>"]+', res)
        
        for i, p in enumerate(proxies[:15], 1):
            await client.send_message(MY_CHANNEL, f"🛡️ MEHRDAD HUNTER\n\n`{p}`\n\n@{MY_CHANNEL}")
            print(f"✅ ارسال شد {i}/15")
            await asyncio.sleep(20)

    except Exception as e:
        print(f"❌ خطای سیستمی: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
