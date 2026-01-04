import os, re, asyncio, socket, time, json, base64, requests
from telethon import TelegramClient, functions, types

# تنظیمات اصلی
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
# اولویت با Secret است، اگر نبود به favproxy می‌فرستد
MY_CHANNEL = os.getenv('MY_CHANNEL', 'favproxy') 

def get_server_address(link):
    try:
        if link.startswith('vmess://'):
            v2_json = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            return v2_json.get('add'), int(v2_json.get('port', 443))
        elif '://' in link:
            # استخراج هاست و پورت برای VLESS, Trojan, SS
            match = re.search(r'@([^:/?#]+):(\d+)', link)
            if match: return match.group(1), int(match.group(2))
            match_no_port = re.search(r'@([^:/?#]+)', link)
            if match_no_port: return match_no_port.group(1), 443
    except: pass
    return None, None

def check_ping(host, port):
    try:
        socket.setdefaulttimeout(1.5) # پینگ سریع برای شکارچی
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
        print("❌ فایل سشن شناسایی نشد!")
        return

    print(f"🕵️‍♂️ شروع عملیات در کانال @{MY_CHANNEL}...")
    keywords = ['vless://', 'vmess://', 'trojan://', 'ss://']
    
    # شروع فایل گزارش HTML
    report_html = f"<html><body style='background:#0f172a; color:#f8fafc; font-family:sans-serif; padding:40px;'>"
    report_html += f"<h1 style='color:#38bdf8;'>🛰 Hunter Bot Dashboard - @{MY_CHANNEL}</h1><hr style='border:0.5px solid #334155;'>"

    for kw in keywords:
        try:
            result = await client(functions.messages.SearchGlobalRequest(
                q=kw, filter=types.InputMessagesFilterEmpty(),
                min_date=None, max_date=None, offset_id=0,
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=25
            ))
            
            for msg in result.messages:
                if hasattr(msg, 'message') and msg.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', msg.message)
                    for link in list(set(links)):
                        host, port = get_server_address(link)
                        if host:
                            ping = check_ping(host, port)
                            if ping: # فقط اگه سالم بود بفرست
                                country, flag = get_geo_info(host)
                                p_type = kw.split('://')[0].upper()
                                
                                # طراحی پست تلگرام
                                beauty_msg = (
                                    f"💎 **{p_type} HIGH SPEED CONFIG**\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🌍 **Location:** {flag} {country}\n"
                                    f"⚡ **Ping:** `{ping}ms` | **Status:** `Stable` ✅\n"
                                    f"🛡 **Verified by Hunter Bot**\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🔗 **Config:**\n\n`{link}`\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"🆔 @{MY_CHANNEL}\n"
                                    f"📡 [t.me/favme](https://t.me/favme)"
                                )
                                
                                try:
                                    await client.send_message(MY_CHANNEL, beauty_msg, link_preview=False)
                                    report_html += f"<div style='background:#1e293b; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #38bdf8;'><b>{flag} {country}</b> | {ping}ms<br><small style='color:#94a3b8;'>{link[:100]}...</small></div>"
                                    await asyncio.sleep(3) # برای جلوگیری از بلاک شدن توسط تلگرام
                                except: pass
        except Exception as e:
            print(f"Error searching {kw}: {e}")

    report_html += "</body></html>"
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(report_html)
    
    await client.disconnect()
    print("✅ شکار این مرحله تمام شد.")

if __name__ == "__main__":
    asyncio.run(hunter_logic())
