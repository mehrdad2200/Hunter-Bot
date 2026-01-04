import os, re, asyncio
from telethon import TelegramClient, functions, types

# تنظیمات شکارچی از Secrets
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
MY_CHANNEL = os.getenv('MY_CHANNEL', 'favme')

async def hunter_logic():
    client = TelegramClient('fav_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Hunter Bot: فایل سشن نامعتبر است!")
        return

    print("📡 Hunter Bot فعال شد. در حال شکار کانفیگ...")
    # کلمات کلیدی برای جستجو
    targets = ['vless://', 'vmess://', 'trojan://', 'ss://']
    
    for target in targets:
        result = await client(functions.messages.SearchGlobalRequest(
            q=target, filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0,
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=10
        ))
        
        for msg in result.messages:
            if hasattr(msg, 'message') and msg.message:
                found_links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                for link in found_links:
                    try:
                        # ارسال به کانال تو t.me/favme
                        await client.send_message(MY_CHANNEL, f"🚀 **Hunter Bot Result**\n\n`{link}`\n\n🆔 @{MY_CHANNEL}")
                        await asyncio.sleep(1) 
                    except: pass
    
    await client.disconnect()
    print("✅ شکار به پایان رسید.")

if __name__ == "__main__":
    asyncio.run(hunter_logic())
