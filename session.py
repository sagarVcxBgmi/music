from pyrogram import Client

app = Client(
    "my_account",
    api_id=24414171,  # Your API ID
    api_hash="5e4b23697681f45515904ad4c8e1c2b7"  # Your API Hash
)

app.start()
print("Your string session:", app.export_session_string())
app.stop()
