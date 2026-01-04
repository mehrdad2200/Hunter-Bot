import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.connect()
    # ارسال پیام تست به خودت (Saved Messages)
    await client.send_message('me', 'سلام مهرداد! ربات با موفقیت به تلگرام وصل شد 🚀')
    # ارسال به کانال
    await client.send_message('favproxy', 'تست ارسال به کانال ✅')
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
