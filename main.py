import os, re, asyncio, json, time, requests, socket, base64
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'  # آیدی کانال بدون @
DB_FILE = "hunter_db.json"
START_TIME = time.time()
LIMIT_TIME = 450  # 9 دقیقه فعالیت

# منابع گیت‌هاب برای شکار بیشتر
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity"
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
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        print("✅ شکارچی متصل شد...")

        # مدیریت دیتابیس برای جلوگیری از تکرار و پاکسازی
        db = {"archive": [], "sent_msgs": [], "daily_count": 0}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f: db.update(json.load(f))
            except: pass

        j_date, j_time, now_dt = get_jalali_now()

        while time.time() - START_TIME < LIMIT_TIME:
            links_pool = []
            
            # ۱. استخراج از گیت‌هاب
            for url in GITHUB_SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    links_pool.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            # ۲. استخراج از تلگرام
            for kw in ['vless://', 'trojan://', 'vmess://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(
                        q=kw, filter=types.InputMessagesFilterEmpty(),
                        min_date=None, max_date=None, offset_rate=0,
                        offset_peer=types.InputPeerEmpty(), offset_id=0, limit=40
                    ))
                    for m in res.messages:
                        if m.message: links_pool.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message))
                except: continue

            # حذف تکراری‌ها
            unique_links = list(set(links_pool))
            random_links = random.sample(unique_links, min(len(unique_links), 50))

            for link in random_links:
                if time.time() - START_TIME > LIMIT_TIME: break
                if link in db["archive"]: continue

                host, port = get_server_address(link)
                ping = check_ping(host, port) if host else False

                if ping:
                    db["daily_count"] += 1
                    proto = link.split('://')[0].upper()
                    
                    text = (
                        f"🛡️ **{proto} HUNTER** | #{db['daily_count']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡️ Ping: {ping}ms (Online)\n"
                        f"📅 {j_date} | ⏰ {j_time}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 **Config:**\n`{link.strip()}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 @{MY_CHANNEL} | 🛰️ @favme"
                    )

                    sent = await client.send_message(MY_CHANNEL, text)
                    db["archive"].append(link)
                    db["sent_msgs"].append({"id": sent.id, "time": now_dt.isoformat()})
                    
                    # پاکسازی ۲۴ ساعته
                    cutoff = now_dt - timedelta(hours=24)
                    for msg in db["sent_msgs"][:]:
                        if datetime.fromisoformat(msg["time"]) < cutoff:
                            try:
                                await client.delete_messages(MY_CHANNEL, [msg["id"]])
                                db["sent_msgs"].remove(msg)
                            except: pass

                    with open(DB_FILE, "w") as f: json.dump(db, f)
                    print(f"✅ ارسال شد: {proto} (Ping: {ping})")
                    await asyncio.sleep(12) # فاصله برای جلوگیری از اسپم

            await asyncio.sleep(10) # انتظار برای دیتای جدید

    finally:
        await client.disconnect()

if __name__ == "__main__":
    import random
    asyncio.run(main())
