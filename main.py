import os, re, asyncio, requests, random, time, socket, json, base64
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- دریافت اطلاعات امنیتی از Secrets گیت‌هاب ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

SEARCH_KEYWORDS = ['vless://', 'vmess://', 'trojan://', 'ss://']

def get_server_address(link):
    try:
        if link.startswith('vmess://'):
            v2_json = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            return v2_json.get('add'), int(v2_json.get('port', 443))
        elif '://' in link:
            match = re.search(r'@([^:/?#]+):(\d+)', link)
            if match: return match.group(1), int(match.group(2))
            match_no_port = re.search(r'@([^:/?#]+)', link)
            return match_no_port.group(1), 443
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
    return "Global", "🌐"

async def main():
    if not STRING_SESSION or not API_ID or not API_HASH:
        print("❌ ارور: متغیرهای امنیتی (Secrets) در گیت‌هاب تنظیم نشده‌اند!")
        return

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("🚀 شکارچی در کل تلگرام به دنبال پروکسی‌های سالم می‌گردد...")

        all_found_links = []
        for kw in SEARCH_KEYWORDS:
            result = await client(functions.messages.SearchGlobalRequest(
                q=kw, filter=types.InputMessagesFilterEmpty(),
                min_date=None, max_date=None, offset_id=0,
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=50
            ))
            for message in result.messages:
                if hasattr(message, 'message') and message.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', message.message)
                    all_found_links.extend(links)

        unique_links = list(set(all_found_links))
        random.shuffle(unique_links)
        
        count = 0
        for link in unique_links:
            if count >= 15: break
            
            host, port = get_server_address(link)
            if not host: continue
            
            ping = check_ping(host, port)
            if ping:
                country, flag = get_geo_info(host)
                msg = (
                    f"🚀 **PREMIUM CONFIG FOUND**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 **Location:** {flag} {country}\n"
                    f"⚡ **Ping:** `{ping}ms` (Stable)\n"
                    f"🛰 **Status:** Online & Verified\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 **Config:**\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @{MY_CHANNEL}\n"
                    f"🛡️ {BRAND}"
                )
                await client.send_message(MY_CHANNEL, msg, link_preview=False)
                print(f"✅ شکار سالم ارسال شد: {country}")
                count += 1
                await asyncio.sleep(20)

    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
