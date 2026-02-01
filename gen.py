from telethon.sync import TelegramClient

api_id = 33949314
api_hash = '87b0593e2015718c550f04e0e49c2733'

with TelegramClient('railway_session', api_id, api_hash) as client:
    print("Session berhasil dibuat!")
