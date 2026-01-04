import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛡️"

SOURCES = [
    "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
    "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt"
]

def create_html(proxies):
    # قالب HTML فوق پیشرفته و خفن
    proxies_html = ""
    for p in proxies[:30]:
        proxies_html += f'''
        <div class="card">
            <div class="config-text">{p[:70]}...</div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{p}')">کپی کن ⚡</button>
        </div>'''

    html_template = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{BRAND}</title>
        <style>
            body {{ background: #0f0f0f; color: #e0e0e0; font-family: 'Segoe UI', Tahoma; text-align: center; margin: 0; padding: 20px; }}
            h1 {{ color: #00ff88; text-shadow: 0 0 15px #00ff88; font-size: 3rem; margin-bottom: 10px; }}
            .container {{ max-width: 900px; margin: auto; }}
            .card {{ background: #1e1e1e; border: 1px solid #333; padding: 20px; margin: 15px 0; border-radius: 15px; display: flex; justify-content: space-between; align-items: center; transition: 0.3s; }}
            .card:hover {{ transform: scale(1.02); border-color: #00ff88; box-shadow: 0 0 20px rgba(0,255,136,0.2); }}
            .config-text {{ font-family: monospace; color: #bbb; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 70%; }}
            .copy-btn {{ background: #00ff88; color: #000; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
            .copy-btn:hover {{ background: #fff; transform: translateY(-2px); }}
            .status {{ color: #888; margin-bottom: 40px; }}
            footer {{ margin-top: 50px; color: #555; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{BRAND}</h1>
            <p class="status">آخرین شکار: {time.strftime('%H:%M:%S')} | وضعیت: <span style="color:#00ff88">عملیاتی ✅</span></p>
            {proxies_html}
            <footer>طراحی شده توسط سیستم هوشمند مهرداد هنتر</footer>
        </div>
    </body>
    </html>'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 اتصال برقرار شد...")

        all_links = []
        for url in SOURCES:
            try:
                res = requests.get(url, timeout=10).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                all_links.extend(links)
            except: continue

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        
        # ساخت سایت با ۳۰ پروکسی
        create_html(unique_proxies)
        print("✅ سایت با کیفیت خفن آپدیت شد.")

        # ارسال فقط ۵ پروکسی برتر به تلگرام (برای جلوگیری از توقف و کرش کردن)
        for p in unique_proxies[:5]:
            msg = (
                f"🛡️ **NEW ELITE CONFIG**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🚀 **Speed:** `Extreme`\n"
                f"🌍 **Region:** `Global` 🌐\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **Config:**\n`{p}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 @{MY_CHANNEL}\n"
                f"💎 **MEHRDAD HUNTER**"
            )
            await client.send_message(MY_CHANNEL, msg)
            await asyncio.sleep(15) # زمان انتظار بیشتر برای امنیت اکانت
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
