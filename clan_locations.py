from clan_scraper import *
from player_scraper import *
import requests

def printRanked(data, index=1):
    counter = 0
    offset = 0
    previous = None
    for dataPoint in data:
        if dataPoint[index] == previous:
            offset += 1
        else:
            counter += offset + 1
            offset = 0
            previous = dataPoint[index]
        print (str(counter) + ". " +
               unicode(dataPoint[0]) + ": " +
               str(dataPoint[1]) + " players in clan (" +
               str(dataPoint[2]) + "%)")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    clanSet = getClans()
    clanData = dict()
    for clan in clanSet:
        cs = ClanScraper(clan)
        name = cs.getClanName()
        size = cs.getMemberCount()
        print "Analyzing", (unicode(name) + "...")
        players = [member[0] for member in cs.getMembers()]
        locData = dict()
        for player in players:
            playerScraper = PlayerScraper(player)
            location = playerScraper.getLocation()
            if "United States" in location:
                if "United States" not in locData:
                    locData["United States"] = 0
                locData["United States"] += 1
            if location not in locData:
                locData[location] = 0
            locData[location] += 1
        locList = list()
        for location in locData:
            percentVal = (Decimal(locData[location]) / Decimal(size)
                          * Decimal(100))
            percentVal = round(float(percentVal), 2)
            locList.append((location, locData[location], percentVal))
        locList = sorted(locList, key=lambda x: x[1])
        locList.reverse()
        clanData[name] = locList
    for clan in clanData:
        print ("[b]" + clan + "[/b]")
        print "========"
        printRanked(clanData[clan])
        print "    "
