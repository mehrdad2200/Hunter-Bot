import os, re, asyncio, requests, random, time, socket, json, base64
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# دریافت اطلاعات از Secrets گیت‌هاب
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

async def main():
    if not STRING_SESSION:
        print("❌ STRING_SESSION یافت نشد!")
        return

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ اتصال موفقیت‌آمیز بود. در حال شکار پروکسی...")

        all_links = []
        for kw in SEARCH_KEYWORDS:
            result = await client(functions.messages.SearchGlobalRequest(
                q=kw, filter=types.InputMessagesFilterEmpty(),
                min_date=None, max_date=None, offset_id=0,
                offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=50
            ))
            for message in result.messages:
                if hasattr(message, 'message') and message.message:
                    links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', message.message)
                    all_links.extend(links)

        unique_links = list(set(all_links))
        random.shuffle(unique_links)
        
        count = 0
        for link in unique_links:
            if count >= 15: break
            host, port = get_server_address(link)
            if host and check_ping(host, port):
                msg = f"🚀 **NEW CONFIG FOUND**\n━━━━━━━━━━━━\n🔗 **Config:**\n`{link.strip()}`\n━━━━━━━━━━━━\n🆔 @{MY_CHANNEL}\n🛡️ {BRAND}"
                await client.send_message(MY_CHANNEL, msg, link_preview=False)
                count += 1
                await asyncio.sleep(20)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
