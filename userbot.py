import asyncio, json, os
from telethon import TelegramClient
from telethon.events import NewMessage

print("🔥 FILE USERBOT KELOAD")

api_id = 33949314
api_hash = '87b0593e2015718c550f04e0e49c2733'

DELAY = 10
GROUP_FILE = 'groups.json'
TEXT_FILE = 'text.txt'

send_task = None


# =====================
# UTIL
# =====================
def load_groups():
    if not os.path.exists(GROUP_FILE):
        return set()
    try:
        with open(GROUP_FILE, 'r') as f:
            return set(json.load(f).get('groups', []))
    except:
        return set()

def save_groups(groups):
    with open(GROUP_FILE, 'w') as f:
        json.dump({"groups": list(groups)}, f)

def load_text():
    if not os.path.exists(TEXT_FILE):
        return ""
    with open(TEXT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def save_text(text):
    with open(TEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(text)


TARGET_GROUPS = load_groups()


# =====================
# AUTO SEND
# =====================
async def auto_send(client):
    print("🚀 AUTO SEND TASK STARTED")

    while True:
        try:
            text = load_text()
            print("📄 Text terbaca:", repr(text))

            if not text.strip():
                print("⚠️ Text kosong, nunggu...")
                await asyncio.sleep(DELAY)
                continue

            if not TARGET_GROUPS:
                print("⚠️ Tidak ada grup target")
                await asyncio.sleep(DELAY)
                continue

            for gid in list(TARGET_GROUPS):
                print(f"➡️ Kirim ke {gid}")
                await client.send_message(gid, text)
                print(f"✅ BERHASIL ke {gid}")
                await asyncio.sleep(1)

            print(f"⏸️ Nunggu {DELAY} detik")
            await asyncio.sleep(DELAY)

        except Exception as e:
            print("💥 AUTO SEND ERROR:", e)
            await asyncio.sleep(5)

    global send_task

    while True:
        text = load_text()

        if not text.strip():
            await asyncio.sleep(DELAY)
            continue

        for gid in list(TARGET_GROUPS):
            try:
                await client.send_message(gid, text)
                await asyncio.sleep(1)
            except Exception as e:
                print("Gagal kirim:", e)

        await asyncio.sleep(DELAY)


# =====================
# MAIN
# =====================
async def main():
    global send_task, DELAY

    client = TelegramClient('railway_session', api_id, api_hash)
    await client.start()
    print("🔥 Userbot promosi AKTIF")

    @client.on(NewMessage(pattern='/ping'))
    async def ping(event):
        await event.reply('✅ USERBOT AKTIF')

    @client.on(NewMessage(pattern='/addgroup'))
    async def add_group(event):
        TARGET_GROUPS.add(event.chat_id)
        save_groups(TARGET_GROUPS)
        await event.reply('✅ Grup ditambahkan')

    @client.on(NewMessage(pattern='/removegroup'))
    async def remove_group(event):
        TARGET_GROUPS.discard(event.chat_id)
        save_groups(TARGET_GROUPS)
        await event.reply('❌ Grup dihapus')

    @client.on(NewMessage(pattern='/listgroup'))
    async def list_group(event):
        await event.reply("\n".join(map(str, TARGET_GROUPS)) or "Kosong")

    @client.on(NewMessage(pattern='/settext'))
    async def set_text(event):
        if not event.is_reply:
            await event.reply("Reply pesan promo dengan /settext")
            return

        msg = await event.get_reply_message()
        save_text(msg.text)
        await event.reply("✅ Text promo disimpan")

    @client.on(NewMessage(pattern='/startsend'))
    async def start_send(event):
        
        global send_task
        if send_task and not send_task.done():
            await event.reply('⚠️ Sudah berjalan')
            return

        send_task = asyncio.create_task(auto_send(client))
        await event.reply('▶️ Auto send dimulai')

            global send_task
            if send_task:
                await event.reply('⚠️ Sudah berjalan')
                return

            send_task = asyncio.create_task(auto_send(client))
            await event.reply(f'▶️ Auto send dimulai\nDelay {DELAY} detik')

    @client.on(NewMessage(pattern='/stopsend'))
    async def stop_send(event):
        global send_task
        if send_task:
            send_task.cancel()
            send_task = None
            await event.reply('⛔ Auto send dihentikan')

    @client.on(NewMessage(pattern=r'^/setdelay'))
    async def set_delay(event):
        global DELAY
        try:
            DELAY = int(event.raw_text.split()[1])
            await event.reply(f'⏱ Delay diubah ke {DELAY} detik')
        except:
            await event.reply('Format: /setdelay 30')

    await client.run_until_disconnected()


# =====================
# ENTRY POINT
# =====================
if __name__ == "__main__":
    asyncio.run(main())
