from player_scraper import *
from clan_scraper import *
from ladder_scraper import *
from decimal import Decimal
import requests

def printRanked(data, minutes=False, index=1):
    counter = 0
    offset = 0
    previous = None
    timeString = " hours per turn ("
    if minutes: timeString = " minutes per turn ("
    for dataPoint in data:
        if dataPoint[index] == previous:
            offset += 1
        else:
            counter += offset + 1
            offset = 0
            previous = dataPoint[index]
        print (str(counter) + ". " +
               unicode(dataPoint[0]) + ": " + "averages " +
               str(round(dataPoint[1], 2)) + timeString +
               str(dataPoint[2]) +")")

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
        clanURL = clanScraper.URL
        print "Analyzing", (clanName + "...")
        players = [member[0] for member in clanScraper.getMembers()]
        mdCount = 0
        rtCount = 0
        mdSum = 0
        rtSum = 0
        mdDataList = list()
        rtDataList = list()
        for player in players:
            playerScraper = PlayerScraper(player)
            name = playerScraper.getPlayerName().encode('ascii', 'ignore')
            playSpeed = playerScraper.getPlaySpeed()
            mdMarker = 'Multi-Day Games'
            rtMarker = 'Real-Time Games'
            URL = playerScraper.URL
            if mdMarker in playSpeed and playSpeed[mdMarker] > 0:
                mdSpeed = round(float(playSpeed[mdMarker]), 2)
                mdSum += mdSpeed
                mdCount += 1
                mdDataList.append((name, mdSpeed, URL))
            if rtMarker in playSpeed and playSpeed[rtMarker] > 0:
                rtSpeed = round(float(Decimal(playSpeed[rtMarker])
                                      * Decimal(60)), 2)
                rtSum += rtSpeed
                rtCount += 1
                rtDataList.append((name, rtSpeed, URL))
        mdDataList = sorted(mdDataList, key=lambda x: x[1])
        rtDataList = sorted(rtDataList, key=lambda x: x[1])
        mdDataList.reverse()
        rtDataList.reverse()
        if mdCount != 0:
            mdAvg = round(float(Decimal(mdSum) / Decimal(mdCount)), 2)
        else: mdAvg = 0
        if rtCount != 0:
            rtAvg = round(float(Decimal(rtSum) / Decimal(rtCount)), 2)
        else: rtAvg = 0
        clanData[clanName] = (mdDataList, mdAvg, rtDataList, rtAvg, clanURL)
    clanDataList = list()
    for clanName in clanData:
        clanDataList.append((clanName, clanData[clanName]))
    clanDataList = sorted(clanDataList, key=lambda x: x[1][1])
    clanDataList.reverse()
    counter = 0
    offset = 0
    previous = None
    for clan in clanDataList:
        if clan[1][1] == previous:
            offset += 1
        else:
            counter += offset + 1
            offset = 0
            previous = clan[1][1]
        clanName = clan[0]
        clanInfo = clan[1]
        mdDataList = clanInfo[0]
        mdAvg = clanInfo[1]
        URL = clanInfo[4]
        sizeString = " players in "
        if len(mdDataList) == 1: sizeString = " player in "
        print ("#" + str(counter) + ":"),
        print ("Ranked " + str(len(mdDataList)) + sizeString + unicode(clanName))
        print ("Average multi-day play speed: " + str(mdAvg) + " hours")
        print ("(" + str(URL) + ")")
        if(len(mdDataList) == 0):
            print "    "
            continue
        print "========"
        printRanked(mdDataList)
        print "    "
    counter = 0
    offset = 0
    previous = None
    clanDataList = sorted(clanDataList, key=lambda x: x[1][3])
    clanDataList.reverse()
    for clan in clanDataList:
        if clan[1][3] == previous:
            offset += 1
        else:
            counter += offset + 1
            offset = 0
            previous = clan[1][3]
        clanName = clan[0]
        clanInfo = clan[1]
        rtDataList = clanInfo[2]
        rtAvg = clanInfo[3]
        URL = clanInfo[4]
        sizeString = " players in "
        if len(rtDataList) == 1: sizeString = " player in "
        print ("#" + str(counter) + ":"),
        print ("Ranked " + str(len(rtDataList)) + sizeString + unicode(clanName))
        print ("Average real-time play speed: " + str(rtAvg) + " minutes")
        print ("(" + str(URL) + ")")
        if(len(rtDataList) == 0):
            print "    "
            continue
        print "========"
        printRanked(rtDataList, minutes=True)
        print "    "
