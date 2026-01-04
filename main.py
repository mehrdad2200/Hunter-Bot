import os, re, asyncio, socket, time, json, base64, requests
from telethon import TelegramClient, functions, types

# تنظیمات از Secrets
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
MY_CHANNEL = os.getenv('MY_CHANNEL', 'favproxy')

extracted_links = []

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
        socket.setdefaulttimeout(2)
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
    return "Unknown", "🌐"

async def hunter_logic():
    client = TelegramClient('fav_session', API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized(): return

    print("🕵️‍♂️ Hunter Bot در حال جستجوی حرفه‌ای...")
    keywords = ['vless://', 'vmess://', 'trojan://', 'ss://']
    
    html_content = "<html><body style='font-family:tahoma; background:#1a1a1a; color:white; padding:20px;'>"
    html_content += f"<h1 style='color:#00d4ff;'>🛰 Hunter Bot Live Logs - @{MY_CHANNEL}</h1><hr>"

    for kw in keywords:
        result = await client(functions.messages.SearchGlobalRequest(
            q=kw, filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0,
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=20
        ))
        
        for msg in result.messages:
            if hasattr(msg, 'message') and msg.message:
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                for link in list(set(links)):
                    host, port = get_server_address(link)
                    if host:
                        ping = check_ping(host, port)
                        if ping and ping < 1500: # فقط پینگ‌های زیر ۱.۵ ثانیه
                            country, flag = get_geo_info(host)
                            
                            # قالب‌بندی زیبا برای تلگرام
                            beauty_msg = (
                                f"🚀 **PREMIUM CONFIG DETECTED**\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"📍 **Country:** {flag} {country}\n"
                                f"⚡ **Ping:** `{ping}ms` | **Status:** ✅\n"
                                f"🛠 **Type:** `{kw.split('://')[0].upper()}`\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"🔗 **Config:**\n\n`{link}`\n\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 @{MY_CHANNEL} | 📡 [t.me/favme](https://t.me/favme)"
                            )
                            
                            await client.send_message(MY_CHANNEL, beauty_msg, link_preview=False)
                            html_content += f"<div style='border:1px solid #333; margin:10px; padding:10px;'><b>{flag} {country}</b> - {ping}ms<br><code style='font-size:10px;'>{link}</code></div>"
                            await asyncio.sleep(2)

    html_content += "</body></html>"
    with open("report.html", "w", encoding="utf-8") as f: f.write(html_content)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(hunter_logic())
