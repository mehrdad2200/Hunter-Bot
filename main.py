import os, asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def debug_hunter():
    print("🔍 در حال بررسی تنظیمات امنیتی مهرداد...")
    
    # تست وجود متغیرها
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    session = os.getenv('STRING_SESSION')

    if not api_id: print("❌ API_ID یافت نشد!")
    if not api_hash: print("❌ API_HASH یافت نشد!")
    if not session: print("❌ STRING_SESSION یافت نشد!")
    
    if not all([api_id, api_hash, session]):
        print("⚠️ مهرداد جان، برو به بخش Secrets و مطمئن شو اسم‌ها دقیقاً همینا هستن.")
        return

    print("📡 تلاش برای اتصال به تلگرام...")
    client = TelegramClient(StringSession(session), int(api_id), api_hash)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ سشن نامعتبر است! تلگرام اجازه ورود نمی‌دهد.")
        else:
            me = await client.get_me()
            print(f"✅ تبریک مهرداد! متصل شدی به نام: {me.first_name}")
            print("🚀 حالا می‌تونی کد اصلی رو با خیال راحت جایگزین کنی.")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_hunter())
