import os, re, asyncio, requests, json, time, socket
from datetime import datetime, timedelta
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

# --- تنظیمات اصلی (از Secrets) ---
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
STRING_SESSION = os.getenv('STRING_SESSION', '')
MY_CHANNEL = 'favproxy'  # آیدی کانال خودت بدون @
BRAND = "🛡️ MEHRDAD HUNTER 🛰️"

# فایل‌های دیتابیس (برای ذخیره در گیت‌هاب)
DB_FILE = "hunter_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"sent_messages": [], "daily_stats": {"count": 0, "last_report": ""}, "start_members": 0}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def check_ping(host, port, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
        return int((time.time() - start) * 1000)
    except: return None

def get_geo(host):
    try:
        res = requests.get(f"http://ip-api.com/json/{host}?fields=status,country,countryCode", timeout=3).json()
        if res.get('status') == 'success':
            code = res.get('countryCode').upper()
            flag = "".join(chr(ord(c) + 127397) for c in code)
            return res.get('country'), flag
    except: pass
    return "Unknown", "🌐"

async def main():
    db = load_db()
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ سشن نامعتبر است!")
            return

        # --- ۱. پاکسازی پیام‌های قدیمی (بیش از ۲۴ ساعت) ---
        now = datetime.now()
        remaining_msgs = []
        for msg in db["sent_messages"]:
            msg_time = datetime.fromisoformat(msg["time"])
            if now - msg_time > timedelta(hours=24):
                try: await client.delete_messages(MY_CHANNEL, msg["id"])
                except: pass
            else:
                remaining_msgs.append(msg)
        db["sent_messages"] = remaining_msgs

        # --- ۲. دریافت تعداد اعضا برای گزارش ---
        full_channel = await client(functions.channels.GetFullChannelRequest(MY_CHANNEL))
        current_members = full_channel.full_chat.participants_count
        if db["start_members"] == 0: db["start_members"] = current_members

        # --- ۳. جستجو و ارسال کانفیگ‌ها ---
        search_results = await client(functions.messages.SearchGlobalRequest(
            q='vless://', filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0,
            offset_peer=types.InputPeerEmpty(), offset_rate=0, limit=50
        ))

        all_links = []
        for m in search_results.messages:
            if hasattr(m, 'message') and m.message:
                links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s<>"]+', m.message)
                all_links.extend(links)

        for link in list(set(all_links))[:10]: # محدودیت برای هر اجرا
            # استخراج هاست و پورت (ساده شده)
            parts = re.split(r'[:@/]', link.replace('vless://', '').replace('vmess://', ''))
            host = parts[1] if len(parts) > 1 else None
            
            ping = check_ping(host, 443) or check_ping(host, 80)
            if ping and ping < 1000: # سقف پینگ
                country, flag = get_geo(host)
                proto = link.split('://')[0].upper()
                
                text = (
                    f"🚀 **PREMIUM CONFIG FOUND**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📍 **Location:** {flag} {country}\n"
                    f"⚡ **Ping:** `{ping}ms` (Stable)\n"
                    f"🏷 **Type:** #{proto}\n"
                    f"⏰ **Time:** {now.strftime('%H:%M')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔗 **Config:**\n\n"
                    f"`{link.strip()}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🆔 @{MY_CHANNEL}\n"
                    f"🛡️ {BRAND}"
                )
                
                sent_msg = await client.send_message(MY_CHANNEL, text, link_preview=False)
                db["sent_messages"].append({"id": sent_msg.id, "time": now.isoformat()})
                db["daily_stats"]["count"] += 1
                await asyncio.sleep(15)

        # --- ۴. گزارش عملکرد ۲۴ ساعته (رأس ساعت ۰۰:۰۰ یا نزدیک به آن) ---
        if now.hour == 0 and db["daily_stats"]["last_report"] != now.strftime("%Y-%m-%d"):
            new_members = current_members - db["start_members"]
            report = (
                f"📊 **گزارش عملکرد ۲۴ ساعت گذشته**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ تعداد کل سرورهای شکار شده: `{db['daily_stats']['count']}`\n"
                f"👥 اعضای جدید پیوسته: `{new_members if new_members > 0 else 0}`\n"
                f"🗑 پیام‌های قدیمی با موفقیت پاکسازی شدند.\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ {BRAND}"
            )
            await client.send_message(MY_CHANNEL, report)
            db["daily_stats"]["count"] = 0
            db["daily_stats"]["last_report"] = now.strftime("%Y-%m-%d")
            db["start_members"] = current_members

    except Exception as e: print(f"❌ Error: {e}")
    finally:
        save_db(db)
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
