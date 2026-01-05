import os, re, asyncio, json, time, requests, random
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy' 
START_TIME = time.time()
LIMIT_TIME = 300 

SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

async def main():
    # استفاده از هویت ثابت برای کاهش حساسیت تلگرام
    client = TelegramClient(
        StringSession(STRING_SESSION), 
        API_ID, 
        API_HASH,
        device_model="Mehrdad-Hunter",
        system_version="Linux-Runner",
        app_version="1.0"
    )
    
    try:
        await client.connect()
        
        # چک کردن اعتبار سشن
        if not await client.is_user_authorized():
            print("❌ سشن باطل شده! مهرداد جان، باید سشن جدید بگیری و در Secrets بذاری.")
            return

        print("✅ متصل شد. شروع شکار...")
        sent_count = 0

        while time.time() - START_TIME < LIMIT_TIME:
            links = []
            # ۱. گیت‌هاب
            for url in SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    links.extend(re.findall(r'(?:vless|trojan|ss|vmess)://[^\s<>"]+', r.text))
                except: continue

            # ۲. تلگرام
            for kw in ['vless://', 'trojan://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(
                        q=kw, filter=types.InputMessagesFilterEmpty(),
                        min_date=None, max_date=None, offset_rate=0,
                        offset_peer=types.InputPeerEmpty(), offset_id=0, limit=50
                    ))
                    for m in res.messages:
                        if m.message:
                            links.extend(re.findall(r'(?:vless|trojan|ss|vmess)://[^\s<>"]+', m.message))
                except: continue

            unique_links = list(set(links))
            random.shuffle(unique_links)

            for link in unique_links:
                if time.time() - START_TIME > LIMIT_TIME or sent_count >= 100: break
                
                sent_count += 1
                proto = link.split('://')[0].upper()
                # تاریخ و ساعت ایران
                t_now = (datetime.utcnow() + timedelta(hours=3, minutes=30)).strftime('%H:%M')
                
                msg = (
                    f"🛡️ <b>{proto} HUNTER</b> | <code>#{sent_count}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📅 1404/10/16 | ⏰ {t_now}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 <b>Config:</b>\n"
                    f"<code>{link.strip()}</code>\n\n"
                    f"🆔 @{MY_CHANNEL}"
                )

                try:
                    await client.send_message(MY_CHANNEL, msg, parse_mode='html', link_preview=False)
                    print(f"✅ ارسال شد: {proto} #{sent_count}")
                    await asyncio.sleep(5) # سرعت بالا برای ۱۰۰ شکار
                except Exception as e:
                    print(f"❌ خطا در ارسال: {e}")
                    if "FLOOD" in str(e).upper():
                        print("⚠️ تلگرام محدود کرد. صبر می‌کنیم...")
                        await asyncio.sleep(120)
                    break
            
            await asyncio.sleep(15)

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
