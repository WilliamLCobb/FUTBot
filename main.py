import time
import models
import os
import random
import pickle
import atexit
from FifaBrowser import FifaBrowser

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



class Task(object):
    def __init__(self, function, interval, name):
        self.lastFire = 0
        self.function = function
        self.interval = interval
        self.name = name

    def fire(self):
        if (time.time() - self.lastFire > self.interval):
            print "Executing:", self.name
            self.function()
            self.lastFire = time.time()

class FUTBot(object):
    def __init__(self):
        self.browser = FifaBrowser()

    def login(self, email, password, answer):
        return self.browser.login(email, password, answer)

    def quit(self):
        x = raw_input("Save Cookies?")
        if x == "y":
            self.browser.save_cookies()

    def search_market(self):
        auctions = self.browser.search()
        for auction in auctions:
            # Update player in db
            player = auction['itemData']
            models.Player.update_player(player['assetId'], player['id'], player['rating'], player['teamid'],
                                        player['nation'], player['discardValue'], player['preferredPosition'], player['rareflag'])

            # Add bid sample
            models.Auction_Sample.add_sample(auction['tradeId'], player['assetId'], auction['buyNowPrice'], auction['currentBid'],
                                             auction['startingBid'], auction['offers'])

    def update_players(self):
        pass

    def start_bot(self):
        print "Bot started"

        # Function: second interval wait
        tasks = [Task(self.search_market, 30, "Market Search")]
        while True:
            for task in tasks:
                task.fire()
            time.sleep(1)

    def updatePlayerDatabase(self):
        pass



def cleanup(bot):
    print "Shutting down bot"
    bot.quit()

# Our main function
if __name__ == "__main__":
    bot = FUTBot()
    models.create_tables()
    atexit.register(cleanup, bot)
    #if bot.login("miniroo321@gmail.com", "Llamas123", "Harrison"):
    if bot.login("mellowman@zain.site", "Llamas12", "Harrison"):
        print "Successfully Logged in"
        bot.start_bot()
    else:
        print "Failed to login, stopping bot"



