import mechanize
import requests
import json
import time
import cookielib
import copy

# Not sure what this number does, doesnt change
# It is EASW_ID in the js file
# --Found out it comes from a json file here: https://gateway.ea.com/proxy/identity/pids/me
# --Seems to be the same per EA account
NUCLEUS_ID = '2289478796'

# Harrison is encrypted into eb1c02fa2004619388466f3b0b8707ff
# Still reversing... looks to be some type of hash
SECURITY_ANSWER_HASH = 'eb1c02fa2004619388466f3b0b8707ff'

# Useful items
# Player list: https://fifa17.content.easports.com/fifa/fltOnlineAssets/CC8267B6-0817-4842-BB6A-A20F88B05418/2017/fut/items/web/players.json
# New Cards? https://utas.external.s2.fut.ea.com/ut/game/fifa17/club/stats/newcards
# user Info: https://utas.external.s2.fut.ea.com/ut/game/fifa17/tradepile

class FifaBrowser(object):
    def __init__(self):
        self.br = mechanize.Browser()
        self.iframebr = mechanize.Browser()
        self.cj = cookielib.LWPCookieJar("cookies.txt")
        # try:
        #     self.cj.load()
        # except:
        #     pass

        self.br.set_cookiejar(self.cj)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36')]
        self.iframebr.set_cookiejar(self.cj)
        self.iframeHeaders = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                              'X-Requested-With': 'XMLHttpRequest',
                              'X-UT-Embed-Error': 'true',
                              'Easw-Session-Data-Nucleus-Id': NUCLEUS_ID,
                              'Origin': 'https://www.easports.com'}

        self.isLoggedIn = False
        self.accessToken = ""
        self.personaId = ""
        self.name = ""
        self.phishingToken = ""

    def iframeHeaderList(self):
        return [(key, self.iframeHeaders[key]) for key in self.iframeHeaders]

    def saveCookies(self):
        self.cj.save()

    def search(self, reauth=True, min_price = None, max_price = None, min_buy = None, max_buy = None, quality = None, id = 0):
        # type:              [player,
        # num:  num results (int = 16)
        # minb: Min Buyout  (int)
        # maxb: Max Buyout  (int)
        # micr: Min price   (int)
        # macr: Max price   (int)
        # lev: quality      [gold,
        # start: offset     (int =  multiple of num)
        # maskedDefId: item filter (int) Exmaple: Ronaldo = 20801
        print "Searching"

        params = {"num": 16,
                  "type": "player"}

        # Add search constraints
        url = "https://utas.external.s2.fut.ea.com/ut/game/fifa17/transfermarket"
        # Add search params
        if len(params) > 0:
            url += "?"

        for p in params.keys():
            url += p + "=" + str(params[p]) + "&"
        url = url[:-1] # Remove the last &

        print url
        self.iframeHeaders['X-Requested-With'] = "ShockwaveFlash/23.0.0.207"
        self.iframebr.addheaders = self.iframeHeaderList()

        r = self.iframebr.open(url).read()
        market_data = json.loads(r)
        if "reason" in market_data:
            print "Need to auth"
            self.auth()
            self.search(reauth=False)
        print market_data


    # Utilities
    def currentTime(self):
        return int(time.time() * 1000) - 4234

    def checkLogin(self):
        r = self.br.open("https://www.easports.com/fifa/api/isUserLoggedIn").read()
        response = json.loads(r)
        if "isLoggedIn" in response and response["isLoggedIn"]:
            return True
        return False

    def login(self, username, password, answer):

        r = self.br.open("https://www.easports.com/fifa/ultimate-team/web-app")
        url = self.br.geturl()
        if not url.find("https://signin.ea.com") == 0:
            print "Already logged in"
            return True
        self.br.select_form(nr = 0)
        self.br.form['email'] = username
        self.br.form['password'] = password
        self.br.submit()
        url = self.br.geturl()

        #Second Step
        code = raw_input("Enter Access Code: ")
        self.br.select_form(nr = 0)
        try:
            self.br.form['twofactorCode'] = code
            #self.br.form['trustThisDevice'] = "on"  # Fix this later
        except:
            print "Invalid email or password"
            print self.br.form
            return False
        self.br.submit()

        url = self.br.geturl()
        if (url.find("https://signin.ea.com") == 0):
            print "Invalid Code"
            print url
            print
        else:
            self.isLoggedIn = True
            return True

    def auth(self):
        # in order to send JSON data, we'll use requests
        headers = copy.copy(self.iframeHeaders)

        #proxy for debugging
        proxies = {
          'http': 'http://192.168.1.82:8080',
          'https': 'https://192.168.1.82:8080',
        }

        post_data = { "isReadOnly": False, "sku": "FUT17WEB", "clientVersion": 1, "nucleusPersonaId": str(self.personaId), "nucleusPersonaDisplayName": self.name, "gameSku": "FFA17PS4", "nucleusPersonaPlatform": "ps3", "locale": "en-US", "method": "authcode", "priorityLevel":4, "identification": { "authCode": "" } }

        r = requests.post("https://www.easports.com/iframe/fut17/p/ut/auth", json=post_data, headers=self.iframeHeaders, cookies=self.cj, proxies=proxies)
        response = json.loads(r.text)
        self.iframeHeaders['X-UT-SID'] = response['sid']
        self.iframebr.addheaders = self.iframeHeaderList()

    def afterLoginSequence(self):
        # This performs the same set of loads as the browser does. It should greatly reduce chance of being caught

        # After Login sequence

        # https://www.easports.com/iframe/fut17/?locale=en_US&baseShowoffUrl=https%3A%2F%2Fwww.easports.com%2Ffifa%2Fultimate-team%2Fweb-app%2Fshow-off&guest_app_uri=http%3A%2F%2Fwww.easports.com%2Ffifa%2Fultimate-team%2Fweb-app
        #
        # https://www.easports.com/fifa/api/isUserLoggedIn :
        # {"isLoggedIn":true}
        #
        # https://accounts.ea.com/connect/auth?response_type=token&redirect_uri=nucleus%3Arest&prompt=none&client_id=ORIGIN_JS_SDK :
        # {"expires_in":"3599","token_type":"Bearer","access_token":"QVQwOjEuMDozLjA6NTk6NUZhekp6eHo3aEZkenZQaXkwbDgwb1NkUkdKdVlnd3RWamE6Nzg3OTY6bmhiYnI"}
        #
        # https://www.easports.com/iframe/fut17/p/ut/game/fifa17/user/accountinfo?filterConsoleLogin=true&sku=FUT17WEB&returningUserGameYear=2016&_=1481156863419:
        # {"debug":"","string":"","code":"465","reason":""}
        #
        # https://www.easports.com/iframe/fut17/p/ut/game/fifa17/user/accountinfo?filterConsoleLogin=true&sku=FUT17WEB&returningUserGameYear=2016&_=1481156863420:
        # {"userAccountInfo":{"personas":[{"personaId":1817802704,"personaName":"SteveCobbs","returningUser":0,"trial":false,"userState":null,"userClubList":[{"year":"2017","assetId":112476,"teamId":112476,"lastAccessTime":1481156866,"platform":"ps3","clubName":"Countdabula","clubAbbr":"Dab","established":1480469694,"divisionOnline":1,"badgeId":6000329,"skuAccessList":{"FFA17PS4":1481156866}}]}]}}
        #
        # https://www.easports.com/iframe/fut17/p/ut/game/fifa17/user/accountinfo?filterConsoleLogin=true&sku=FUT17WEB&returningUserGameYear=2016&_=1481156863421:
        # {"debug":"","string":"","code":"465","reason":""}
        #
        # https://www.easports.com/iframe/fut17/p/ut/auth : { "isReadOnly": false, "sku": "FUT17WEB", "clientVersion": 1, "nucleusPersonaId": 1817802704, "nucleusPersonaDisplayName": "SteveCobbs", "gameSku": "FFA17PS4", "nucleusPersonaPlatform": "ps3", "locale": "en-US", "method": "authcode", "priorityLevel":4, "identification": { "authCode": "" } }
        # {"protocol":"https","ipPort":"utas.external.s2.fut.ea.com:443","serverTime":"2016-12-08T00:27:48+0000","lastOnlineTime":"2016-12-08T00:27:48+0000","sid":"83cf8945-5aec-4434-bf93-b2a178b14d1f"}

        # https://www.easports.com/iframe/fut17/p/ut/game/fifa17/phishing/question?_=1481156863422:
        # {"question":1,"attempts":5,"recoverAttempts":20}
        #
        # https://www.easports.com/iframe/fut17/p/ut/game/fifa17/phishing/validate: answer=eb1c02fa2004619388466f3b0b8707ff
        # {"debug":"Answer is correct.","string":"OK","code":"200","reason":"Answer is correct.","token":"6926682274143938654"}

        # This might be unecessary
        self.br.open("https://www.easports.com/iframe/fut17/?locale=en_US&baseShowoffUrl=https%3A%2F%2Fwww.easports.com%2Ffifa%2Fultimate-team%2Fweb-app%2Fshow-off&guest_app_uri=http%3A%2F%2Fwww.easports.com%2Ffifa%2Fultimate-team%2Fweb-app").read()

        if not self.checkLogin():
            print "Not logged in"
            return False

        r = self.br.open("https://accounts.ea.com/connect/auth?response_type=token&redirect_uri=nucleus%3Arest&prompt=none&client_id=ORIGIN_JS_SDK").read()
        response = json.loads(r)
        if 'access_token' in response:
            self.accessToken = response['access_token']
            print "Got Access Token:", self.accessToken
        else:
            print "Unable to get access token"
            print response
            return False

        nonce = self.currentTime()
        # Not sure what these are but we have to try them until 1 works
        routes = ['https://utas.external.fut.ea.com:443', 'https://utas.external.s2.fut.ea.com:443', 'https://utas.external.s3.fut.ea.com:443']
        routeFound = False
        for route in routes:
            # Changes X-UT-Route
            self.iframeHeaders['X-UT-Route'] = route
            self.iframebr.addheaders = self.iframeHeaderList()
            r = self.iframebr.open("https://www.easports.com/iframe/fut17/p/ut/game/fifa17/user/accountinfo?filterConsoleLogin=true&sku=FUT17WEB&returningUserGameYear=2016&_="+str(nonce)).read()
            print r
            response = json.loads(r)
            if 'userAccountInfo' in response:
                self.personaId = response['userAccountInfo']['personas'][0]["personaId"]
                self.name = response['userAccountInfo']['personas'][0]["personaName"]
                print "ID", self.personaId
                print "Name", self.name
                routeFound = True
                break
            nonce += 1

        if not routeFound:
            print "Error, all routes down"
            return False

        self.auth()

        nonce += 1
        r = self.iframebr.open("https://www.easports.com/iframe/fut17/p/ut/game/fifa17/phishing/question?_="+str(nonce))
        response = json.loads(r.read())
        print response

        if 'question' in response:
            # Need to answer question
            print "Answering Question"
            r = self.iframebr.open("https://www.easports.com/iframe/fut17/p/ut/game/fifa17/phishing/validate", "answer="+SECURITY_ANSWER_HASH).read()
            response = json.loads(r)
            if ("code" in response and response["code"] == "200"):
                self.phishingToken = response["token"]
                self.iframeHeaders["X-UT-PHISHING-TOKEN"] = self.phishingToken
            return True
        else:
            print "Question already answered"
            return True


class FUTBot(object):
    def __init__(self):
        self.browser = FifaBrowser()

    def login(self, email, password, answer):
        print "Logging in"
        if (self.browser.login(email, password, answer)):
            self.browser.saveCookies()
            print "Logged in"
            if (self.browser.afterLoginSequence()):
                return True
        else:
            print "Failed to log in"

        return False

    def search(self):
        self.browser.search()


bot = FUTBot()
if bot.login("miniroo321@gmail.com", "Llamas123", "Harrison"):
    print "Successfully Logged in"
    print "Bot started"
    bot.search()
else:
    print "Failed to login, stopping bot"

# Test Response:
#'{"errorState":null,"credits":0,"auctionInfo":[{"tradeId":177710337601,"itemData":{"id":263528884337,"timestamp":1481134753,"formation":"f4321","untradeable":false,"assetId":225193,"rating":76,"itemType":"player","resourceId":-1878822999,"owners":2,"discardValue":304,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":400,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"CM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":66,"index":0},{"value":63,"index":1},{"value":73,"index":2},{"value":74,"index":3},{"value":68,"index":4},{"value":72,"index":5}],"teamid":22,"rareflag":0,"playStyle":250,"leagueId":19,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":45},"tradeState":"active","buyNowPrice":600,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":550,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337601"},{"tradeId":177710337603,"itemData":{"id":263529358626,"timestamp":1481135086,"formation":"f3412","untradeable":false,"assetId":2196,"rating":78,"itemType":"player","resourceId":-1879045996,"owners":2,"discardValue":312,"itemState":"forSale","cardsubtypeid":0,"lastSalePrice":400,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"GK","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":76,"index":0},{"value":81,"index":1},{"value":53,"index":2},{"value":77,"index":3},{"value":20,"index":4},{"value":81,"index":5}],"teamid":22,"rareflag":0,"playStyle":273,"leagueId":19,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":21},"tradeState":"active","buyNowPrice":500,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":450,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337603"},{"tradeId":177710337605,"itemData":{"id":262876620900,"timestamp":1480220568,"formation":"f4411","untradeable":false,"assetId":164835,"rating":80,"itemType":"player","resourceId":-1878883357,"owners":2,"discardValue":640,"itemState":"forSale","cardsubtypeid":0,"lastSalePrice":700,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"GK","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":77,"index":0},{"value":84,"index":1},{"value":73,"index":2},{"value":84,"index":3},{"value":50,"index":4},{"value":78,"index":5}],"teamid":1960,"rareflag":1,"playStyle":273,"leagueId":13,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":37},"tradeState":"active","buyNowPrice":1200,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1100,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337605"},{"tradeId":177710337612,"itemData":{"id":259651166690,"timestamp":1476474246,"formation":"f3421","untradeable":false,"assetId":203299,"rating":80,"itemType":"player","resourceId":-1878844893,"owners":2,"discardValue":640,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":850,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"RM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":91,"index":0},{"value":76,"index":1},{"value":74,"index":2},{"value":82,"index":3},{"value":32,"index":4},{"value":68,"index":5}],"teamid":234,"rareflag":1,"playStyle":250,"leagueId":308,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":59},"tradeState":"active","buyNowPrice":1800,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1700,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337612"},{"tradeId":177710337613,"itemData":{"id":263387825828,"timestamp":1480912999,"formation":"f352","untradeable":false,"assetId":186745,"rating":75,"itemType":"player","resourceId":-1878861447,"owners":2,"discardValue":300,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":1300,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"CAM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":81,"index":0},{"value":64,"index":1},{"value":74,"index":2},{"value":80,"index":3},{"value":25,"index":4},{"value":60,"index":5}],"teamid":112606,"rareflag":0,"playStyle":250,"leagueId":39,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":52},"tradeState":"active","buyNowPrice":1500,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1400,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337613"},{"tradeId":177710337626,"itemData":{"id":262682528374,"timestamp":1480067141,"formation":"f4231","untradeable":false,"assetId":184999,"rating":78,"itemType":"player","resourceId":-1878863193,"owners":2,"discardValue":624,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":750,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"CDM","statsList":[{"value":5,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":5,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":2,"suspension":0,"attributeList":[{"value":74,"index":0},{"value":73,"index":1},{"value":76,"index":2},{"value":77,"index":3},{"value":75,"index":4},{"value":72,"index":5}],"teamid":100769,"rareflag":1,"playStyle":250,"leagueId":67,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":54},"tradeState":"active","buyNowPrice":700,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":650,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337626"},{"tradeId":177710337638,"itemData":{"id":258438695314,"timestamp":1475525052,"formation":"f41212","untradeable":false,"assetId":142784,"rating":82,"itemType":"player","resourceId":-1878905408,"owners":5,"discardValue":656,"itemState":"forSale","cardsubtypeid":1,"lastSalePrice":1500,"morale":50,"fitness":83,"injuryType":"none","injuryGames":0,"preferredPosition":"RB","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":77,"index":0},{"value":2,"index":1},{"value":2,"index":2},{"value":1,"index":3},{"value":1,"index":4}],"training":0,"contract":3,"suspension":0,"attributeList":[{"value":68,"index":0},{"value":56,"index":1},{"value":70,"index":2},{"value":74,"index":3},{"value":84,"index":4},{"value":83,"index":5}],"teamid":10,"rareflag":1,"playStyle":264,"leagueId":13,"assists":0,"lifetimeAssists":2,"loyaltyBonus":0,"pile":5,"nation":52},"tradeState":"active","buyNowPrice":1700,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1600,"confidenceValue":100,"expires":45,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337638"},{"tradeId":177710337640,"itemData":{"id":261804014625,"timestamp":1478865016,"formation":"f3421","untradeable":false,"assetId":183332,"rating":75,"itemType":"player","resourceId":-1878864860,"owners":2,"discardValue":300,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":350,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"RM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":82,"index":0},{"value":68,"index":1},{"value":68,"index":2},{"value":79,"index":3},{"value":41,"index":4},{"value":64,"index":5}],"teamid":38,"rareflag":0,"playStyle":250,"leagueId":19,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":21},"tradeState":"active","buyNowPrice":650,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":450,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710337640"},{"tradeId":177710340828,"itemData":{"id":263247081794,"timestamp":1480722187,"formation":"f4231","untradeable":false,"assetId":170783,"rating":78,"itemType":"player","resourceId":-1878877409,"owners":2,"discardValue":624,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":650,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"CDM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":68,"index":0},{"value":57,"index":1},{"value":66,"index":2},{"value":71,"index":3},{"value":77,"index":4},{"value":88,"index":5}],"teamid":13,"rareflag":1,"playStyle":250,"leagueId":14,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":108},"tradeState":"active","buyNowPrice":1400,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":700,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340828"},{"tradeId":177710340829,"itemData":{"id":263210387772,"timestamp":1480688956,"formation":"f3421","untradeable":false,"assetId":213135,"rating":78,"itemType":"player","resourceId":-1878835057,"owners":2,"discardValue":624,"itemState":"forSale","cardsubtypeid":3,"lastSalePrice":650,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"ST","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":85,"index":0},{"value":74,"index":1},{"value":68,"index":2},{"value":76,"index":3},{"value":31,"index":4},{"value":73,"index":5}],"teamid":9,"rareflag":1,"playStyle":250,"leagueId":13,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":7},"tradeState":"active","buyNowPrice":1600,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1500,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340829"},{"tradeId":177710340834,"itemData":{"id":257931936724,"timestamp":1475269215,"formation":"f3412","untradeable":false,"assetId":212125,"rating":78,"itemType":"player","resourceId":-1878836067,"owners":3,"discardValue":624,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":650,"morale":50,"fitness":94,"injuryType":"foot","injuryGames":0,"preferredPosition":"RM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":144,"index":0},{"value":6,"index":1},{"value":2,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":19,"suspension":0,"attributeList":[{"value":92,"index":0},{"value":66,"index":1},{"value":71,"index":2},{"value":83,"index":3},{"value":40,"index":4},{"value":56,"index":5}],"teamid":237,"rareflag":1,"playStyle":250,"leagueId":308,"assists":0,"lifetimeAssists":16,"loyaltyBonus":0,"pile":5,"nation":51},"tradeState":"active","buyNowPrice":850,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":800,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340834"},{"tradeId":177710340837,"itemData":{"id":262859359075,"timestamp":1480196843,"formation":"f442","untradeable":false,"assetId":216547,"rating":80,"itemType":"player","resourceId":-1878831645,"owners":2,"discardValue":640,"itemState":"forSale","cardsubtypeid":2,"lastSalePrice":650,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"LM","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":92,"index":0},{"value":67,"index":1},{"value":73,"index":2},{"value":84,"index":3},{"value":36,"index":4},{"value":45,"index":5}],"teamid":234,"rareflag":1,"playStyle":250,"leagueId":308,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":38},"tradeState":"active","buyNowPrice":1800,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1700,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340837"},{"tradeId":177710340842,"itemData":{"id":263517939688,"timestamp":1481124200,"formation":"f451","untradeable":false,"assetId":219932,"rating":78,"itemType":"player","resourceId":-1878828260,"owners":2,"discardValue":312,"itemState":"forSale","cardsubtypeid":3,"lastSalePrice":400,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"ST","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":77,"index":0},{"value":75,"index":1},{"value":66,"index":2},{"value":81,"index":3},{"value":25,"index":4},{"value":66,"index":5}],"teamid":449,"rareflag":0,"playStyle":250,"leagueId":53,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":58},"tradeState":"active","buyNowPrice":550,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":500,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340842"},{"tradeId":177710340844,"itemData":{"id":260410441206,"timestamp":1477187461,"formation":"f3412","untradeable":false,"assetId":183574,"rating":80,"itemType":"player","resourceId":-1878864618,"owners":1,"discardValue":640,"itemState":"forSale","cardsubtypeid":3,"lastSalePrice":0,"morale":50,"fitness":93,"injuryType":"none","injuryGames":0,"preferredPosition":"CF","statsList":[{"value":3,"index":0},{"value":2,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":3,"index":0},{"value":2,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":4,"suspension":0,"attributeList":[{"value":74,"index":0},{"value":79,"index":1},{"value":79,"index":2},{"value":81,"index":3},{"value":38,"index":4},{"value":71,"index":5}],"teamid":38,"rareflag":1,"playStyle":250,"leagueId":19,"assists":0,"lifetimeAssists":0,"loyaltyBonus":1,"pile":5,"nation":21},"tradeState":"active","buyNowPrice":900,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":650,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710340844"},{"tradeId":177710343986,"itemData":{"id":262914479783,"timestamp":1480269997,"formation":"f451","untradeable":false,"assetId":194138,"rating":75,"itemType":"player","resourceId":-1878854054,"owners":2,"discardValue":600,"itemState":"forSale","cardsubtypeid":3,"lastSalePrice":700,"morale":50,"fitness":99,"injuryType":"none","injuryGames":0,"preferredPosition":"ST","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":7,"suspension":0,"attributeList":[{"value":91,"index":0},{"value":74,"index":1},{"value":60,"index":2},{"value":70,"index":3},{"value":23,"index":4},{"value":75,"index":5}],"teamid":1796,"rareflag":1,"playStyle":250,"leagueId":13,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":14},"tradeState":"active","buyNowPrice":1400,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1300,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710343986"},{"tradeId":177710343991,"itemData":{"id":263117049149,"timestamp":1480548063,"formation":"f343","untradeable":false,"assetId":192448,"rating":83,"itemType":"player","resourceId":-1878855744,"owners":6,"discardValue":664,"itemState":"forSale","cardsubtypeid":0,"lastSalePrice":1000,"morale":50,"fitness":98,"injuryType":"none","injuryGames":0,"preferredPosition":"GK","statsList":[{"value":0,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"lifetimeStats":[{"value":6,"index":0},{"value":0,"index":1},{"value":0,"index":2},{"value":0,"index":3},{"value":0,"index":4}],"training":0,"contract":1,"suspension":0,"attributeList":[{"value":84,"index":0},{"value":81,"index":1},{"value":83,"index":2},{"value":85,"index":3},{"value":38,"index":4},{"value":78,"index":5}],"teamid":241,"rareflag":1,"playStyle":273,"leagueId":53,"assists":0,"lifetimeAssists":0,"loyaltyBonus":0,"pile":5,"nation":21},"tradeState":"active","buyNowPrice":1500,"currentBid":0,"offers":0,"watched":null,"bidState":"none","startingBid":1400,"confidenceValue":100,"expires":44,"sellerName":"FIFA UT","sellerEstablished":0,"sellerId":0,"tradeOwner":false,"tradeIdStr":"177710343991"}],"duplicateItemIdList":null,"bidTokens":{}}'
