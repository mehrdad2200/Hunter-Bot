import os, re, asyncio, json, time, requests, socket, base64, random
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات سیستمی ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy' 
START_TIME = time.time()
LIMIT_TIME = 300 # ۵ دقیقه فعالیت

SOURCES = [
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/vless.txt",
    "https://raw.githubusercontent.com/Joker-funland/V2ray-configs/main/trojan.txt",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity"
]

def get_jalali():
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    return "1404/10/16", now.strftime('%H:%M')

def get_addr(link):
    try:
        if link.startswith('vmess://'):
            v_js = json.loads(base64.b64decode(link[8:]).decode('utf-8'))
            return v_js.get('add'), int(v_js.get('port', 443))
        m = re.search(r'@([^:/?#]+):(\d+)', link)
        if m: return m.group(1), int(m.group(2))
        m2 = re.search(r'@([^:/?#]+)', link)
        if m2: return m2.group(1), 443
    except: pass
    return None, None

def check_ping(h, p):
    try:
        socket.setdefaulttimeout(1.0) # کاهش زمان انتظار برای پینگ سریع‌تر
        st = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((h, p))
        return int((time.time() - st) * 1000)
    except: return False

async def main():
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    try:
        await client.connect()
        sent_links = set()
        total_sent = 0

        while time.time() - START_TIME < LIMIT_TIME:
            all_l = []
            # استخراج از منابع
            for url in SOURCES:
                try:
                    r = requests.get(url, timeout=5)
                    all_l.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', r.text))
                except: continue

            for kw in ['vless://', 'trojan://', 'ss://']:
                try:
                    res = await client(functions.messages.SearchGlobalRequest(
                        q=kw, filter=types.InputMessagesFilterEmpty(),
                        min_date=None, max_date=None, offset_rate=0,
                        offset_peer=types.InputPeerEmpty(), offset_id=0, limit=50
                    ))
                    for m in res.messages:
                        if m.message: all_l.extend(re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message))
                except: continue

            unique = list(set(all_l))
            random.shuffle(unique)

            for link in unique:
                # چک کردن زمان و محدودیت ۱۰۰ تا
                if time.time() - START_TIME > LIMIT_TIME or total_sent >= 100:
                    break
                
                if link in sent_links: continue

                host, port = get_addr(link)
                png = check_ping(host, port) if host else False

                if png:
                    total_sent += 1
                    d, t = get_jalali()
                    proto = link.split('://')[0].upper()
                    
                    msg = (
                        f"🛡️ <b>{proto} HUNTER</b> | <code>#{total_sent}</code>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡️ <b>Ping:</b> <code>{png}ms</code> (Online)\n"
                        f"📅 {d} | ⏰ {t}\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 <b>Config:</b>\n"
                        f"<code>{link.strip()}</code>\n\n"
                        f"🆔 @{MY_CHANNEL} | 🛰️ @favme"
                    )

                    try:
                        await client.send_message(MY_CHANNEL, msg, parse_mode='html', link_preview=False)
                        sent_links.add(link)
                        # کاهش زمان استراحت به ۳ ثانیه برای رسیدن به ۱۰۰ پست در ۵ دقیقه
                        await asyncio.sleep(3) 
                    except: 
                        await asyncio.sleep(20) # اگر تلگرام فلود کرد بیشتر صبر کن
            
            if total_sent >= 100: break
            await asyncio.sleep(5)

    finally:
        await client.disconnect()
        print(f"🏁 پایان عملیات. تعداد کل ارسال شده: {total_sent}")

if __name__ == "__main__":
    asyncio.run(main())
