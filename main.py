import os, re, asyncio, requests, random
from telethon import TelegramClient
from telethon.sessions import StringSession

# تنظیمات اصلی
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = -1003576265638  # آیدی عددی کانال تو

async def main():
    client = TelegramClient(StringSession(STRING_SESSION.strip()), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 متصل شد!")

        # دریافت پروکسی‌ها (سورس‌های معتبر)
        sources = [
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/barry-far/V2RAY-CONFIGS/main/All_Configs_Sub.txt"
        ]
        
        all_proxies = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                all_proxies.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res))
            except: continue

        # حذف تکراری‌ها و مخلوط کردن
        unique_proxies = list(set(all_proxies))
        random.shuffle(unique_proxies)

        # ارسال ۱۵ تا پروکسی با فاصله کوتاه
        for i, p in enumerate(unique_proxies[:15], 1):
            msg = f"🛡️ MEHRDAD HUNTER\n━━━━━━━━━━━━\n📍 Config {i}/15\n⚡ Status: Active ✅\n━━━━━━━━━━━━\n`{p}`\n━━━━━━━━━━━━\n🆔 @favproxy"
            await client.send_message(MY_CHANNEL, msg)
            print(f"✅ ارسال موفق {i}")
            await asyncio.sleep(5) # فاصله رو کم کردم که سریع‌تر تموم بشه

    except Exception as e:
        print(f"❌ خطای اجرا: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
