import os, re, asyncio, socket, time, json, base64, requests
from telethon import TelegramClient, functions, types

# تنظیمات
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
MY_CHANNEL = os.getenv('MY_CHANNEL', 'favproxy')

def get_server_address(link):
    try:
        if link.startswith('vmess://'):
            v2_json = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            return v2_json.get('add'), int(v2_json.get('port', 443))
        elif '://' in link:
            match = re.search(r'@([^:/?#]+):(\d+)', link)
            if match: return match.group(1), int(match.group(2))
            match_no_port = re.search(r'@([^:/?#]+)', link)
            if match_no_port: return match_no_port.group(1), 443
    except: pass
    return None, None

def check_ping(host, port):
    try:
        socket.setdefaulttimeout(1.5)
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return int((time.time() - start) * 1000)
    except: return False

def get_geo_info(host):
    try:
        res = requests.get(f"http://ip-api.com/json/{host}?fields=status,country,countryCode", timeout=2).json()
        if res.get('status') == 'success':
            code = res.get('countryCode').upper()
            flag = "".join(chr(ord(c) + 127397) for c in code)
            return res.get('country'), flag
    except: pass
    return "Global", "🌐"

async def hunter_logic():
    client = TelegramClient('fav_session', API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Session Error")
        return

    keywords = ['vless://', 'vmess://', 'trojan://', 'ss://']
    cards_html = ""
    
    print(f"🔎 Hunting for @{MY_CHANNEL}...")

    for kw in keywords:
        try:
            result = await client(functions.messages.SearchGlobalRequest(
                q=kw, filter=types.InputMessagesFilterEmpty(),
                min_date=None, max_date=None, offset_id=0,
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=30
            ))
            
            for msg in result.messages:
                if hasattr(msg, 'message') and msg.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                    for link in list(set(links)):
                        host, port = get_server_address(link)
                        if host:
                            ping = check_ping(host, port)
                            if ping and ping < 1200:
                                country, flag = get_geo_info(host)
                                p_type = kw.split('://')[0].upper()
                                
                                # ارسال به تلگرام
                                beauty_msg = (
                                    f"💎 **{p_type} PREMIUM CONFIG**\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🌍 **Country:** {flag} {country}\n"
                                    f"⚡ **Ping:** `{ping}ms` | **Status:** `Stable` ✅\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🔗 **Config:**\n\n`{link}`\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🆔 @{MY_CHANNEL}\n"
                                    f"📡 [Developer](https://t.me/favme)"
                                )
                                try:
                                    await client.send_message(MY_CHANNEL, beauty_msg, link_preview=False)
                                    # ساخت کارت برای HTML
                                    cards_html += f"""
                                    <div class="card">
                                        <span class="ping">{ping}ms</span>
                                        <span class="flag">{flag}</span>
                                        <b>{country} - {p_type}</b>
                                        <code class="config">{link}</code>
                                    </div>"""
                                    await asyncio.sleep(2)
                                except: pass
        except: pass

    # ساخت فایل نهایی index.html
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Hunter Bot Live Panel</title>
        <style>
            body {{ background: #0f172a; color: white; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .card {{ background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-right: 5px solid #38bdf8; }}
            .ping {{ color: #4ade80; font-weight: bold; float: left; }}
            .config {{ background: #0f172a; padding: 8px; border-radius: 5px; font-size: 10px; display: block; margin-top: 10px; color: #94a3b8; overflow-x: auto; }}
            h1 {{ color: #38bdf8; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛰 مانیتورینگ زنده @{MY_CHANNEL}</h1>
            <p style="text-align:center">بروزرسانی: {time.strftime('%H:%M:%S')}</p>
            {cards_html}
        </div>
    </body>
    </html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(hunter_logic())
