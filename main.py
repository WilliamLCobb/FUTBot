import sys
import FUTBot
from FUTBot import FUTBot

import atexit
from FifaBrowser import FifaBrowser
import models
import playsound
from config import *

# Useful items
# Player list: https://fifa17.content.easports.com/fifa/fltOnlineAssets/CC8267B6-0817-4842-BB6A-A20F88B05418/2017/fut/items/web/players.json
# New Cards? https://utas.external.s2.fut.ea.com/ut/game/fifa17/club/stats/newcards
# user Info: https://utas.external.s2.fut.ea.com/ut/game/fifa17/tradepile
# Player Lookup: https://www.easports.com/uk/fifa/ultimate-team/fut/database/player/20801

# REMEMBER
# Make sure selenium is running with: java -jar selenium-server-standalone-2.53.1.jar
# Make sure browsermob-proxy is running with: java -jar browsermob-dist-2.1.2.jar
# Eventually this will need to be automatic in the startup script

# Windows
# "C:\Program Files (x86)\Java\jre1.8.0_111\bin\java.exe" -jar D:\Dropbox\Python\PyCharm\FUTBot\selenium\selenium-server-standalone-2.53.1.jar
# "C:\Program Files (x86)\Java\jre1.8.0_111\bin\java.exe" -jar D:\Dropbox\Python\PyCharm\FUTBot\selenium\browsermob-dist-2.1.2.jar



def cleanup(bot):
    print "Shutting down bot"
    bot.stop()

# Reload the bot without having to restart browser
def reload_bot():
    print "Reloading"
    #del sys.modules['FUTBot']
    import FUTBot
    reload(FUTBot)
    from FUTBot import FUTBot

# Our main function
if __name__ == "__main__":
    browser = FifaBrowser()
    bot = FUTBot(browser)

    models.create_tables()
    atexit.register(cleanup, bot)

    #if bot.login("miniroo321@gmail.com", "Llamas123", "Harrison"):
    if bot.login("mellowman@zain.site", "Llamas12", "Harrison"):
        print "Successfully Logged in"
        bot.start()
    else:
        print "Failed to login, stopping bot"

    while True:
        command = raw_input("> ")
        if command == 'r':
            print "Reloading Bot"
            print sys.modules
            bot.stop()
            bot.join()
            reload_bot()
            bot = FUTBot(browser)
            bot.start()
        elif command == 'stop':
            print "Stopping"
            bot.stop()
            bot.join()
        elif command == 'start':
            print "Starting"
            reload_bot()
            bot = FUTBot(browser)
            bot.start()
        else:
            print "Invalid Input"
            continue
        print "Done"




