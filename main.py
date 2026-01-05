import os, re, asyncio, requests, json, time, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types, Button
from telethon.sessions import StringSession

# --- تنظیمات (Secrets) ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
MY_CHANNEL = 'favproxy'
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

DB_FILE = "hunter_db.json"

def get_jalali_date():
    # محاسبه ساده برای تبدیل به شمسی (تقریبی و دقیق برای بازه فعلی)
    now = datetime.utcnow() + timedelta(hours=3, minutes=30)
    gy, gm, gd = now.year, now.month, now.day
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = gy - 621
    days = (gy - 1) * 365 + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + g_d_m[gm - 1] + gd
    jy_all_days = days - ((jy + 620) * 365 + (jy + 620) // 4 - (jy + 620) // 100 + (jy + 620) // 400)
    if jy_all_days > 286:
        jy += 1
        jy_all_days -= 286
    else:
        jy_all_days += 79
    if jy_all_days <= 186:
        jm = 1 + (jy_all_days - 1) // 31
        jd = 1 + (jy_all_days - 1) % 31
    else:
        jm = 7 + (jy_all_days - 187) // 30
        jd = 1 + (jy_all_days - 187) % 30
    return f"{jy}/{jm:02d}/{jd:02d} {now.strftime('%H:%M')}"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {"sent_messages": [], "configs_archive": [], "daily_stats": {"count": 0, "last_report": ""}}

def save_db(data):
    # فقط ۱۰۰ تای آخر رو نگه دار
    data["configs_archive"] = data["configs_archive"][-100:]
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def check_ping(host, port):
    try:
        socket.setdefaulttimeout(1.5)
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return int((time.time() - start) * 1000)
    except: return None

def get_geo(host):
    try:
        res = requests.get(f"http://ip-api.com/json/{host}?fields=status,country,countryCode", timeout=2).json()
        if res.get('status') == 'success':
            code = res.get('countryCode').upper()
            flag = "".join(chr(ord(c) + 127397) for c in code)
            return res.get('country'), flag
    except: pass
    return "Global", "🌐"

async def main():
    db = load_db()
    j_time = get_jalali_date()
    
    # هم اکانت هم ربات رو وصل می‌کنیم
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    
    try:
        await client.connect()
        print("🛰️ شکارچی و ربات آماده عملیات...")

        # پاکسازی قدیمی‌ها
        now_dt = datetime.now()
        rem_msgs = []
        for m in db["sent_messages"]:
            if now_dt - datetime.fromisoformat(m["time"]) < timedelta(hours=24): rem_msgs.append(m)
            else: 
                try: await client.delete_messages(MY_CHANNEL, m["id"])
                except: pass
        db["sent_messages"] = rem_msgs

        # شکار
        search = await client(functions.messages.SearchGlobalRequest(q='vless://', filter=types.InputMessagesFilterEmpty(), min_date=None, max_date=None, offset_id=0, offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=40))
        
        count = 0
        for m in search.messages:
            if count >= 10: break
            links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message or "")
            for link in links:
                if any(x['link'] == link for x in db["configs_archive"]): continue
                
                parts = re.split(r'[:@/]', link.replace('vless://', '').replace('vmess://', ''))
                host = parts[1] if len(parts) > 1 else None
                ping = check_ping(host, 443) or check_ping(host, 80)
                
                if ping:
                    country, flag = get_geo(host)
                    proto = link.split('://')[0].upper()
                    
                    text = (
                        f"🚀 **PREMIUM CONFIG FOUND**\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"📍 **Location:** {flag} {country}\n"
                        f"⚡ **Ping:** `{ping}ms` (Stable)\n"
                        f"🏷 **Type:** #{proto}\n"
                        f"⏰ **Time:** `{j_time}`\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 **Config:**\n\n"
                        f"`{link.strip()}`\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 @{MY_CHANNEL}\n"
                        f"🛡️ {BRAND}"
                    )
                    
                    # ارسال با ربات برای داشتن دکمه شیشه‌ای
                    buttons = [
                        [Button.inline("📋 کپی سرور", b"copy"), Button.url("🔍 تست سرعت", "https://t.me/favproxy")],
                        [Button.inline(f"🕒 {j_time}", b"time")]
                    ]
                    
                    sent = await bot.send_message(MY_CHANNEL, text, buttons=buttons, link_preview=False)
                    db["sent_messages"].append({"id": sent.id, "time": now_dt.isoformat()})
                    db["configs_archive"].append({"link": link, "proto": proto, "country": country, "flag": flag, "ping": ping})
                    db["daily_stats"]["count"] += 1
                    count += 1
                    await asyncio.sleep(10)

    except Exception as e: print(f"❌ Error: {e}")
    finally:
        save_db(db)
        await client.disconnect()
        await bot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
