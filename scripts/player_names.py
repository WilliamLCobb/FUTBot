import models
import urllib2
import json

data = urllib2.urlopen("https://fifa17.content.easports.com/fifa/fltOnlineAssets/CC8267B6-0817-4842-BB6A-A20F88B05418/2017/fut/items/web/players.json").read()

jdata = json.loads(data)

players = jdata['Players']

#print jdata['LegendsPlayers']

print len(players)

for player in players:
    id = player['id']
    if "c" in player:
        name = player['c']
    else:
        name = player['f'] + " " + player['l']
    print id, name

    # Search FUTBIN
    futbin_search = urllib2.urlopen('https://www.futbin.com/search?year=17&term='+name.replace(' ', '+') + '&_=1481924519669')
    futbin_data = json.loads(futbin_search)
    print name
    print futbin_data
    models.AssetName.add_name(name, id)

