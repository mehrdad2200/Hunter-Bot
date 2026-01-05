import os, re, asyncio, json, time, requests, socket, base64, random
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy' 
START_TIME = time.time()
LIMIT_TIME = 600 # 10 دقیقه بیدار ماندن

GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt"
]

def get_jalali_now():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return "1404/10/16", now.strftime('%H:%M'), now

def get_server_address(link):
    try:
        if link.startswith('vmess://'):
            v2_json = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            return v2_json.get('add'), int(v2_json.get('port', 443))
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

async def main():
    if not STRING_SESSION:
        print("❌ STRING_SESSION یافت نشد!")
        return

    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ اتصال برقرار شد. شروع شکار...")

        # حافظه موقت برای جلوگیری از تکرار در یک اجرا
        sent_in_this_run = set()
        j_date, _, _ = get_jalali_now()

        while time.time() - START_TIME < LIMIT_TIME:
            links_pool = []
            
            # ۱. گیت‌هاب
            for url in GITHUB_SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    links_pool.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            # ۲. تلگرام با پارامترهای کامل HTML
            for kw in ['vless://', 'trojan://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(
                        q=kw, filter=types.InputMessagesFilterEmpty(),
                        min_date=None, max_date=None, offset_rate=0,
                        offset_peer=types.InputPeerEmpty(), offset_id=0, limit=40
                    ))
                    for m in res.messages:
                        if m.message: links_pool.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message))
                except: continue

            unique_links = list(set(links_pool))
            random.shuffle(unique_links)

            for link in unique_links:
                if time.time() - START_TIME > LIMIT_TIME: break
                if link in sent_in_this_run: continue

                host, port = get_server_address(link)
                ping = check_ping(host, port) if host else False

                if ping:
                    _, j_time, _ = get_jalali_now()
                    proto = link.split('://')[0].upper()
                    
                    # --- چیدمان HTML (کد مونو-اسپیس برای کپی راحت) ---
                    text = (
                        f"🛡️ <b>{proto} HUNTER</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡️ <b>Ping:</b> <code>{ping}ms</code> (Online)\n"
                        f"📅 {j_date} | ⏰ {j_time}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 <b>Config (Click to Copy):</b>\n"
                        f"<code>{link.strip()}</code>\n\n"
                        f"🆔 @{MY_CHANNEL} | 🛰️ @favme"
                    )

                    try:
                        await client.send_message(MY_CHANNEL, text, parse_mode='html', link_preview=False)
                        sent_in_this_run.add(link)
                        print(f"✅ ارسال شد: {proto}")
                        await asyncio.sleep(12) 
                    except Exception as e:
                        print(f"❌ خطا در ارسال: {e}")
                        await asyncio.sleep(30)

            await asyncio.sleep(20) # انتظار برای دور بعدی جستجو

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
