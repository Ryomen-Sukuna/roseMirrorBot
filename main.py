from config import *

bot.start(bot_token=TOKEN)
load_modules()

if __name__ == "__main__":
    bot.run_until_disconnected()
