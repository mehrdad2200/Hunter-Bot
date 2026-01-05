async def fetch_telegram_proxies():
    if not STRING_SESSION: 
        print("❌ ارور: STRING_SESSION خالی است!")
        return []
    
    found = []
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    print("📡 در حال تلاش برای نفوذ به تلگرام...")
    
    try:
        await asyncio.wait_for(client.connect(), timeout=20)
        
        if not await client.is_user_authorized():
            print("⚠️ ارور حساس: تلگرام سشن را رد کرد! (باید سشن جدید بسازی)")
            return []
            
        print("✅ ایول! تلگرام متصل شد. در حال جمع‌آوری...")
        # ... بقیه کد جستجو
        
    except asyncio.TimeoutError:
        print("⏳ ارور تایم‌اوت: آی‌پی گیت‌هاب توسط تلگرام مسدود شده یا اینترنت ضعیف است.")
    except Exception as e:
        print(f"❌ خطای غیرمنتظره تلگرام: {str(e)}")
    finally:
        await client.disconnect()
    return found
