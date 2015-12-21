from player_scraper import *
from clan_scraper import *
from ladder_scraper import *
from decimal import Decimal
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
               unicode(dataPoint[0]) + ": " + "last seen " +
               str(dataPoint[2]) + " ago (" +
               str(dataPoint[3]) +")")

def noWhitespace(string):
    while string[0] == " " or string[0] == "\n":
        string = string[1:]
    while string[len(string)-1] == " " or string[len(string)-1] == "\n":
        string = string[:len(string)-1]
    return string

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    clanSet = getClans()
    clanData = dict()
    for clan in clanSet:
        clanScraper = ClanScraper(clan)
        clanName = clanScraper.getClanName()
        print "Analyzing", (clanName + "...")
        players = [member[0] for member in clanScraper.getMembers()]
        size = clanScraper.getMemberCount()
        inactives14 = 0
        inactives30 = 0
        playerData = list()
        for player in players:
            playerScraper = PlayerScraper(player)
            name = playerScraper.getPlayerName()
            lastSeen = playerScraper.getLastSeen()
            lsString = playerScraper.getLastSeenString()
            lsString = noWhitespace(lsString)
            URL = playerScraper.URL
            if lastSeen >= (14 * 24):
                inactives14 += 1
                if lastSeen >= (30 * 24):
                    inactives30 += 1
                playerData.append((name, lastSeen, lsString, URL))
        playerDataList = (sorted(playerData, key=lambda x: x[1]))
        playerDataList.reverse()
        percent14 = round(float(Decimal(100) * Decimal(inactives14)
                                / Decimal(size)), 2)
        percent30 = round(float(Decimal(100) * Decimal(inactives30)
                                / Decimal(size)), 2)
        clanData[clanName] = (playerDataList, percent14, percent30, inactives14,
                              inactives30)
    for clanName in clanData:
        data = clanData[clanName][0]
        percent14 = clanData[clanName][1]
        percent30 = clanData[clanName][2]
        inactives14 = clanData[clanName][3]
        inactives30 = clanData[clanName][4]
        length = len(data)
        print ("Ranked " + str(length) + " inactive members in " +
               unicode(clanName))
        print (str(inactives14) + "players (" + str(percent14) +
               "%) inactive for 14+ days; " + str(inactives30) + "players (" +
               str(percent30) + "%) "
               "inactive for 30+ days")
        print "   "
        if length == 0: continue
        print "============"
        printRanked(data)
        print "   "
