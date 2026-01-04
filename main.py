import os, re, asyncio, requests, random, time
from telethon import TelegramClient
from telethon.sessions import StringSession

# --- تنظیمات مهرداد هنتر ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛡️"

COUNTRY_MAP = {
    'tr': '🇹🇷 TURKEY', 'us': '🇺🇸 USA', 'de': '🇩🇪 GERMANY',
    'ir': '🇮🇷 IRAN', 'nl': '🇳🇱 NETHERLANDS', 'gb': '🇬🇧 UK',
    'fr': '🇫🇷 FRANCE', 'fi': '🇫🇮 FINLAND', 'sg': '🇸🇬 SINGAPORE',
    'jp': '🇯🇵 JAPAN', 'ca': '🇨🇦 CANADA', 'ae': '🇦🇪 UAE'
}

def get_location(url):
    name_part = url.split('#')[-1].lower() if '#' in url else ''
    for code, info in COUNTRY_MAP.items():
        if code in name_part: return info
    return "🌐 GLOBAL"

def create_html(proxies):
    proxies_html = ""
    for p in proxies[:40]:
        loc = get_location(p)
        name = p.split('#')[-1] if '#' in p else "High-Speed"
        proxies_html += f'''
        <div class="card">
            <div class="info"><span class="tag">{loc}</span><div class="name">{name[:20]}</div></div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('{p}');alert('کپی شد ✅')">COPY</button>
        </div>'''
    
    html_template = f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{BRAND}</title>
        <style>
            body {{ background: #0a0a0a; color: white; font-family: sans-serif; text-align: center; }}
            .card {{ background: #1a1a1a; border: 1px solid #00ff88; padding: 15px; margin: 10px auto; border-radius: 10px; max-width: 500px; display: flex; justify-content: space-between; align-items: center; }}
            .tag {{ background: #00ff88; color: black; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem; margin-left: 10px; }}
            .copy-btn {{ background: #00ff88; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1 style="color:#00ff88">{BRAND}</h1>
        <p>Update: {time.strftime('%H:%M:%S')}</p>
        {proxies_html}
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
            "https://raw.githubusercontent.com/barry-far/V2RAY-CONFIGS/main/All_Configs_Sub.txt"
        ]

        all_links = []
        for url in sources:
            try:
                res = requests.get(url, timeout=10).text
                all_links.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', res))
            except: continue

        unique_proxies = list(set(all_links))
        random.shuffle(unique_proxies)
        create_html(unique_proxies)
        
        selection = unique_proxies[:15]
        for i, p in enumerate(selection, 1):
            loc = get_location(p)
            msg = f"{BRAND}\n━━━━━━━━━━━━\n📍 **Server {i}/15:** {loc}\n⚡ **Status:** `Active`\n━━━━━━━━━━━━\n🔗 **Config:**\n`{p}`\n━━━━━━━━━━━━\n🆔 @{MY_CHANNEL}"
            await client.send_message(MY_CHANNEL, msg)
            if i < 15: await asyncio.sleep(20) # ایجاد فاصله برای ۵ دقیقه بیداری

    except Exception as e: print(f"❌ Error: {e}")
    finally: await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
