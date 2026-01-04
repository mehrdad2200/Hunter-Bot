import os, re, asyncio, socket, time, json, base64, requests, random
from telethon import TelegramClient, functions, types

# تنظیمات اصلی
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
MY_CHANNEL = os.getenv('MY_CHANNEL', 'favproxy')

# سورس‌های خارجی گیت‌هاب
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/MahdiKharyab/v2ray-collector/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Iranian_Proxies_Collector/Main/main/sub/all.txt",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"
]

def get_server_info(link):
    try:
        host, port = None, 443
        if link.startswith('vmess://'):
            v2_json = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            host, port = v2_json.get('add'), int(v2_json.get('port', 443))
        elif '://' in link:
            match = re.search(r'@([^:/?#]+):(\d+)', link)
            if match: host, port = match.group(1), int(match.group(2))
        
        if host:
            # تست پینگ سریع
            socket.setdefaulttimeout(1)
            start = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
            ping = int((time.time() - start) * 1000)
            
            # دریافت لوکیشن
            geo = requests.get(f"http://ip-api.com/json/{host}?fields=countryCode", timeout=2).json()
            code = geo.get('countryCode', 'US').upper()
            flag = "".join(chr(ord(c) + 127397) for c in code)
            return ping, flag
    except: pass
    return None, None

async def hunter_logic():
    client = TelegramClient('fav_session', API_ID, API_HASH)
    await client.connect()
    
    all_proxies = []
    
    # ۱. جمع‌آوری از گیت‌هاب
    for url in GITHUB_SOURCES:
        try:
            res = requests.get(url, timeout=10).text
            # اگر بیس۶۴ بود دیکود کن
            try: content = base64.b64decode(res).decode('utf-8')
            except: content = res
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', content)
            for l in links[:20]: # از هر سورس ۲۰ تا برتر
                all_proxies.append({"link": l, "src": "GitHub Source 🐙"})
        except: pass

    # ۲. جمع‌آوری از تلگرام (با احتیاط)
    keywords = ['vless://', 'vmess://']
    for kw in keywords:
        try:
            res = await client(functions.messages.SearchGlobalRequest(q=kw, filter=types.InputMessagesFilterEmpty(), min_date=None, max_date=None, offset_id=0, offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=15))
            for msg in res.messages:
                found = re.findall(r'(?:vless|vmess)://[^\s<>"]+', msg.message or "")
                for f in found: all_proxies.append({"link": f, "src": "Telegram Hunt 🔎"})
        except: await asyncio.sleep(10)

    # ۳. فیلتر، تست و ارسال رندوم (جلوگیری از بلاک)
    random.shuffle(all_proxies)
    valid_count = 0
    final_data = []

    for item in all_proxies:
        if valid_count >= 10: break # در هر بار اجرا کلاً ۱۰ تا بفرست که بلاک نشی
        
        ping, flag = get_server_info(item['link'])
        if ping and ping < 900:
            valid_count += 1
            item.update({"ping": ping, "flag": flag, "time": time.strftime('%H:%M')})
            final_data.append(item)
            
            # ارسال به تلگرام با وقفه رندوم
            msg = f"💎 **PREMIUM CONFIG**\n━━━━━━━━━━\n📍 Source: `{item['src']}`\n🌍 Country: {flag}\n⚡ Ping: `{ping}ms`\n━━━━━━━━━━\n`{item['link']}`\n━━━━━━━━━━\n🆔 @{MY_CHANNEL}"
            try:
                await client.send_message(MY_CHANNEL, msg, link_preview=False)
                wait_time = random.randint(45, 90) # بین ۴۵ تا ۹۰ ثانیه صبر برای هر پست
                print(f"✅ Sent {valid_count}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            except: break

    # ۴. ساخت صفحه HTML مینیمال و مدرن
    cards_html = ""
    for p in final_data:
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge">{p['src']}</span>
                <span class="ping">{p['ping']}ms</span>
            </div>
            <div class="card-body">
                <div class="geo">{p['flag']} Connected via Secure Server</div>
                <code onclick="navigator.clipboard.writeText('{p['link']}')">{p['link']}</code>
            </div>
        </div>"""

    full_html = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hunter Panel</title>
        <style>
            :root {{ --bg: #050505; --card: #121212; --accent: #007aff; --text: #ffffff; }}
            body {{ background: var(--bg); color: var(--text); font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: auto; }}
            h1 {{ font-weight: 800; letter-spacing: -1px; text-align: center; color: var(--accent); }}
            .card {{ background: var(--card); border: 1px solid #222; border-radius: 16px; padding: 16px; margin-bottom: 16px; transition: 0.3s; }}
            .card:hover {{ border-color: var(--accent); }}
            .card-header {{ display: flex; justify-content: space-between; margin-bottom: 12px; }}
            .badge {{ background: #222; font-size: 10px; padding: 4px 8px; border-radius: 20px; color: #888; }}
            .ping {{ color: #34c759; font-weight: bold; font-size: 13px; }}
            code {{ display: block; background: #000; padding: 12px; border-radius: 8px; font-size: 10px; color: #007aff; word-break: break-all; cursor: pointer; }}
            .geo {{ margin-bottom: 8px; font-size: 14px; opacity: 0.9; }}
            .footer {{ text-align: center; font-size: 12px; color: #444; margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>HUNTER<span>BOT</span></h1>
            <p style="text-align:center; opacity:0.5; font-size:12px;">Live Dashboard @{MY_CHANNEL}</p>
            {cards_html}
            <div class="footer">Updated at {time.strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    </body>
    </html>"""
    
    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)
    await client.disconnect()

if __name__ == "__main__": asyncio.run(hunter_logic())
