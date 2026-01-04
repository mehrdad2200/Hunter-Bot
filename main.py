import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛰️ MEHRDAD HUNTER 🛰️"

# دیتابیس شناسایی کشورها و پرچم‌ها
COUNTRY_MAP = {
    'tr': ('Turkey', '🇹🇷'), 'us': ('USA', '🇺🇸'), 'de': ('Germany', '🇩🇪'),
    'ir': ('Iran', '🇮🇷'), 'nl': ('Netherlands', '🇳🇱'), 'gb': ('UK', '🇬🇧'),
    'fr': ('France', '🇫🇷'), 'fi': ('Finland', '🇫🇮'), 'sg': ('Singapore', '🇸🇬'),
    'jp': ('Japan', '🇯🇵'), 'ca': ('Canada', '🇨🇦'), 'ae': ('UAE', '🇦🇪'),
    'ru': ('Russia', '🇷🇺'), 'in': ('India', '🇮🇳'), 'kr': ('Korea', '🇰🇷')
}

def get_location_info(url):
    """تشخیص کشور و ایموجی از روی متن پروکسی"""
    name_part = url.split('#')[-1].lower() if '#' in url else ''
    for code, (name, emoji) in COUNTRY_MAP.items():
        if code in name_part or name.lower() in name_part:
            return f"{emoji} {name.upper()}"
    return "🌐 GLOBAL"

def create_html(proxies):
    proxies_html = ""
    for p in proxies[:40]:
        loc = get_location_info(p)
        name = p.split('#')[-1] if '#' in p else "High-Speed"
        proxies_html += f'''
        <div class="card">
            <div class="info">
                <span class="loc-tag">{loc}</span>
                <div class="name">{name[:25]}</div>
            </div>
            <div class="config-val">{p[:40]}...</div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{p}');alert('کپی شد ✅')">کپی</button>
        </div>'''

    html_template = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{BRAND}</title>
        <style>
            :root {{ --neon: #00ff88; --bg: #0d0d0d; --card: #1a1a1a; }}
            body {{ background: var(--bg); color: #fff; font-family: 'Segoe UI', Tahoma; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
            h1 {{ color: var(--neon); text-shadow: 0 0 15px var(--neon); }}
            .card {{ background: var(--card); border: 1px solid #333; width: 100%; max-width: 550px; padding: 15px; margin: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; transition: 0.3s; }}
            .card:hover {{ border-color: var(--neon); transform: translateY(-3px); }}
            .loc-tag {{ background: #333; color: var(--neon); padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; margin-left: 10px; border: 1px solid var(--neon); }}
            .name {{ font-weight: bold; font-size: 0.9rem; }}
            .copy-btn {{ background: var(--neon); color: #000; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
            .footer {{ margin-top: 30px; color: #555; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <h1>{BRAND}</h1>
        <p>بروزرسانی: {time.strftime('%H:%M:%S')}</p>
        {proxies_html}
        <div class="footer">Next update in 15 minutes...</div>
    </body>
    </html>'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 شکارچی بیدار شد...")

        sources = [
            "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
            "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt"
        ]

        all_links = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res)
                all_links.extend(links)
            except: continue

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        
        # ساخت سایت
        create_html(unique_proxies)
        print("✅ سایت آپدیت شد.")

        # ارسال به تلگرام (۳ مورد برتر برای هر ۱۵ دقیقه)
        for p in unique_proxies[:3]:
            loc_info = get_location_info(p)
            msg = (
                f"{BRAND}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📍 **Server:** {loc_info}\n"
                f"⚡ **Status:** `Excellent`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **Config:**\n`{p}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 @{MY_CHANNEL}"
            )
            await client.send_message(MY_CHANNEL, msg)
            await asyncio.sleep(10)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
