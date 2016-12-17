import time
import random
import models
from threading import Thread
import playsound
from config import *

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

# All bot logic should go here
class FUTBot(Thread):
    def __init__(self, browser):
        Thread.__init__(self)
        self.browser = browser
        self.running = True

    def login(self, email, password, answer):
        return self.browser.login(email, password, answer)

    def search_market(self):
        auctions = self.browser.start_scan()
        if not auctions:
            print "No auction data"
            return
        for i in range(random.randint(25, 30)):
            if not self.running:
                return
            if not auctions:
                print "Auctions was null!"
                return
            for i, auction in enumerate(auctions):
                # Update player in db
                player = auction['itemData']
                models.Player.update_player(player['assetId'], player['id'], player['rating'], player['teamid'],
                                            player['nation'], player['discardValue'], player['preferredPosition'], player['rareflag'])

                # Add bid sample
                models.Auction_Sample.add_sample(auction['tradeId'], player['assetId'], auction['buyNowPrice'], auction['currentBid'],
                                                 auction['startingBid'], auction['offers'])

                # Last 6 hours
                short_range = models.Auction_Sample.player_price(player['assetId'], 3600 * 12) # Market price last 12 hours
                short_average = self.minimal_average(short_range, 4, 10)
                # Last 3 days
                long_range =  models.Auction_Sample.player_price(player['assetId'], 3600 * 24 * 3)
                long_average = self.minimal_average(long_range, 6, 25)

                bid = auction['currentBid']
                if bid == 0:
                    bid = auction['startingBid']

                # print "Player:", player['assetId']
                # print "Short Range Price:", short_average
                # print "Long Range Price:", long_average
                if (i <= 12 and (long_average and bid < long_average * 0.85) or (short_average and bid < short_average  * 0.85)):
                    print "Short Range Price:", short_average
                    print "Long Range Price:", long_average
                    print "You should bid on", models.AssetName.name_for_id(player['assetId'])
                    print "Current bid", bid
                    print short_range
                    print long_range
                    print
                    self.browser.bid_card(i)
                    playsound.playsound(root_path+"/resources/chime.mp3")
                    time.sleep(60)

            auctions = self.browser.next_page()

    def minimal_average(self, l, n ,m):
        # Not enough here to get a solid reading
        if (len(l) < m):
            return None
        m = sorted(l)[:n]
        return sum(m) / len(m)

    # Threading
    def stop(self):
        self.running = False

    def run(self):
        print "Bot started"

        while self.running:
            self.search_market()
            if self.running:
                time.sleep(60)
        # Function: second interval wait
        # tasks = [Task(self.search_market, 3000, "Market Search")]
        # while True:
        #     for task in tasks:
        #         task.fire()
        #     time.sleep(1)