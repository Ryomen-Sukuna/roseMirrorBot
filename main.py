from config import *

bot.start(bot_token=TOKEN)
load_modules()

try:
    db.list_database_names()
except Exception as e:
    print(e)
    print("Database not found. Creating...")
    db.create_database("bot")

if __name__ == "__main__":
    bot.run_until_disconnected()
