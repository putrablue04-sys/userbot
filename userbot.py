print("FILE BARU KELOAD")

import asyncio, json, os
from telethon import TelegramClient
from telethon.events import NewMessage

api_id = 33949314
api_hash = '87b0593e2015718c550f04e0e49c2733'

DELAY = 10
MESSAGE_TEXT = ""
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
MESSAGE_TEXT = load_text()


# =====================
# AUTO SEND
# =====================
async def auto_send(client):
    global MESSAGE_TEXT
    while True:
        MESSAGE_TEXT = load_text()

        if not MESSAGE_TEXT.strip():
            await asyncio.sleep(DELAY)
            continue

        for gid in list(TARGET_GROUPS):
            try:
                await client.send_message(gid, MESSAGE_TEXT)
                await asyncio.sleep(1)
            except Exception as e:
                print("Gagal:", e)

        await asyncio.sleep(DELAY)


# =====================
# MAIN
# =====================
async def main():
    global send_task, DELAY

    client = TelegramClient('session', api_id, api_hash)
    await client.start()
    print('🔥 Userbot promosi aktif')

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
        text = "\n".join([str(g) for g in TARGET_GROUPS]) or "Kosong"
        await event.reply(text)

    # ===================== SET TEXT (MULTI LINE)
    @client.on(NewMessage(pattern='/settext'))
    async def set_text(event):
        if not event.is_reply:
            await event.reply("Reply pesan promo dengan /settext")
            return

        msg = await event.get_reply_message()
        save_text(msg.text)
        await event.reply("✅ Text promo disimpan")

    # ===================== START
    @client.on(NewMessage(pattern='/startsend'))
    async def start_send(event):
        global send_task
        if send_task:
            await event.reply('⚠️ Sudah jalan')
            return

        send_task = asyncio.create_task(auto_send(client))
        await event.reply(f'▶️ Auto send mulai\nDelay {DELAY} detik')

    # ===================== STOP
    @client.on(NewMessage(pattern='/stopsend'))
    async def stop_send(event):
        global send_task
        if send_task:
            send_task.cancel()
            send_task = None
            await event.reply('⛔ Dihentikan')

    # ===================== DELAY
    @client.on(NewMessage(pattern=r'^/setdelay'))
    async def set_delay(event):
        global DELAY

        parts = event.raw_text.split()

        if len(parts) < 2:
            await event.reply('Format salah.\nContoh: /setdelay 30')
            return

        try:
            DELAY = int(parts[1])
            await event.reply(f'⏱ Delay diubah ke {DELAY} detik')
        except:
            await event.reply('Angka delay tidak valid')



if __name__ == '__main__':
    asyncio.run(main())
