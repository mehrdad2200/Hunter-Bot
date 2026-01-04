import os, re, asyncio, requests, random
from telethon import TelegramClient
from telethon.sessions import StringSession

# دریافت اطلاعات از Secrets گیت‌هاب
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'

async def main():
    # لاگین با استفاده از کد متنی (بدون نیاز به فایل سشن)
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ کد STRING_SESSION باطل شده یا اشتباه است!")
            return

        print("✅ اتصال موفق! در حال جمع‌آوری پروکسی...")

        # لیست سورس‌های پروکسی
        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt"
        ]

        all_links = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                all_links.extend(links)
            except: pass

        # انتخاب ۵ پروکسی تصادفی و ارسال به کانال
        random.shuffle(all_links)
        for link in all_links[:5]:
            msg = f"💎 **New Config Found**\n\n`{link}`\n\n🆔 @{MY_CHANNEL}"
            await client.send_message(MY_CHANNEL, msg)
            print(f"🚀 Sent to @{MY_CHANNEL}")
            await asyncio.sleep(5) # فاصله بین ارسال‌ها

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
