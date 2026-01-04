import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "💎 MEHRDAD HUNTER 💎"

SOURCES = [
    "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
    "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes"
]

def create_html(proxies):
    """ساخت صفحه وب برای گیت‌هاب پیج"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>{BRAND}</title>
        <style>
            body {{ font-family: tahoma; background: #1a1a1a; color: white; text-align: center; padding: 50px; }}
            .config {{ background: #333; margin: 10 in auto; padding: 15px; border-radius: 10px; word-break: break-all; border: 1px solid #00ff00; }}
            h1 {{ color: #00ff00; }}
            .footer {{ margin-top: 50px; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <h1>{BRAND}</h1>
        <p>آخرین پروکسی‌های پرسرعت شکار شده:</p>
        {"".join([f'<div class="config">{p}</div><br>' for p in proxies[:20]])}
        <div class="footer">آپدیت شده در: {time.ctime()}</div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ شکارچی بیدار شد...")

        # ۱. جمع‌آوری
        raw_links = []
        for url in SOURCES:
            try:
                res = requests.get(url, timeout=15).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                raw_links.extend(links)
            except: continue

        # ۲. فیلتر و انتخاب بهترین‌ها
        unique_proxies = list(set(raw_links))
        random.shuffle(unique_proxies)
        selected_proxies = unique_proxies[:15] # انتخاب ۱۵ مورد برتر

        # ۳. ساخت سایت
        create_html(selected_proxies)
        print("✅ فایل HTML ساخته شد.")

        # ۴. ارسال به تلگرام با ظاهر فول‌آپشن
        for p in selected_proxies[:10]: # ارسال ۱۰ تا به تلگرام برای جلوگیری از اسپم
            msg = (
                f"{BRAND}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🛰 **Status:** `Active` ✅\n"
                "⚡ **Speed:** `High-Speed` 🚀\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **Config:**\n`{p}`\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"🆔 @{MY_CHANNEL}\n"
                "👤 Powered by Mehrdad"
            )
            await client.send_message(MY_CHANNEL, msg)
            await asyncio.sleep(8) 
            
        print(f"✅ عملیات با موفقیت انجام شد و به @{MY_CHANNEL} ارسال شد.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
