from player_scraper import *
import requests

def getQualifiedPlayers(playerSet, minRates, maxBoot, minPoints):
    qualifiedPlayers = set()
    count = 0
    existing = 0
    for player in playerSet:
        count += 1
        if (count % 500 == 0): print count, existing
        ps = PlayerScraper(player)
        existence = ps.playerExists()
        if not existence: continue
        existing += 1
        try:
            points = ps.getPoints()
        except:
            print "failure at", player
            points = ps.getPoints()
        bootRate = ps.getBootRate()
        rankedData = ps.getRankedData()[0]
        clanID = ps.getClanID()
        if clanID is not None: continue
        if points < minPoints: continue
        if bootRate > maxBoot: continue
        failure = False
        for rateType in minRates:
            if rateType in rankedData:
                winRate = rankedData[rateType][2]
                minRate = minRates[rateType]
                if winRate < minRate:
                    failure = True
                    break
        if failure:
            continue
        qualifiedPlayers.add(player)
    print "Counted", count, "of which", existing, "existed and", len(qualifiedPlayers), "met criteria"
    print "    "
    print "    "
    print "    "
    return qualifiedPlayers

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    playerSet = xrange(10000000, 10000000000)
    minRates = dict()
    minRates['1v1'] = 50
    minRates['2v2'] = 50
    minRates['3v3'] = 50
    maxBoot = 5
    minPoints = 200000
    qualifiedPlayers = getQualifiedPlayers(playerSet, minRates,
                                           maxBoot, minPoints)
    for player in qualifiedPlayers:
        print ("https://www.warlight.net/Profile?p=" + str(player))
