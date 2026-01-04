import os, re, asyncio, socket, time, json, base64, requests, random
from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError

# تنظیمات جدید
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
MY_CHANNEL = 'favproxy' # کانال جدید

GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"
]

async def main():
    # استفاده از نام فایل ثابت برای سشن
    client = TelegramClient('fav_session', API_ID, API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ ERROR: Not Logged In! You must run this locally once to create fav_session.session")
            return # جلوگیری از کرش و توقف Workflow
            
        print("✅ Logged in to Telegram successfully!")
        
        all_proxies = []
        # جمع‌آوری از گیت‌هاب
        for url in GITHUB_SOURCES:
            try:
                res = requests.get(url, timeout=10).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                for l in links[:20]: all_proxies.append({"link": l, "src": "GitHub 🐙"})
            except: pass

        # جستجو در تلگرام
        keywords = ['vless://', 'vmess://']
        for kw in keywords:
            try:
                res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), min_date=None, max_date=None, offset_id=0, offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=10))
                for msg in res.messages:
                    found = re.findall(r'(?:vless|vmess)://[^\s<>"]+', msg.message or "")
                    for f in found: all_proxies.append({"link": f, "src": "Hunt 🔎"})
            except: pass

        random.shuffle(all_proxies)
        valid_data = []
        for item in all_proxies[:5]: # ارسال تعداد محدود برای امنیت
            msg = f"💎 **NEW CONFIG**\n📍 Src: `{item['src']}`\n\n`{item['link']}`\n\n🆔 @{MY_CHANNEL}"
            await client.send_message(MY_CHANNEL, msg, link_preview=False)
            valid_data.append(item)
            await asyncio.sleep(random.randint(30, 60))

        # ساخت HTML
        html_content = f"<html><body style='background:#000;color:#fff;font-family:sans-serif;text-align:center;'><h1>FAV PROXY</h1>"
        for p in valid_data:
            html_content += f"<div style='border:1px solid #333;margin:10px;padding:10px;'><code>{p['link']}</code></div>"
        html_content += "</body></html>"
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
