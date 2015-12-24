from player_scraper import *
from clan_scraper import *
from ladder_scraper import *
from decimal import Decimal
import requests

def getLadderHistory(teamID, ladderID):
    offset = 0
    go = True
    allGames = list()
    wins = games = 0
    while(go):
        lths = LadderTeamHistoryScraper(ladderID, teamID, offset)
        allGames += lths.getGameHistory()
        if lths.isEmpty:
            go = False
        offset += 50
    for game in allGames:
        winningTeam = game[2]
        finished = game[4]
        if finished:
            games += 1
            if winningTeam == teamID:
                wins += 1
    return wins, games

def getScore(playerScraper):
    bootRate = playerScraper.getBootRate()
    rankedData = playerScraper.getRankedData()[0]
    ladderData = playerScraper.getLadderData()
    if len(rankedData) == 0 or len(ladderData) == 0:
        return None
    if '1v1' in rankedData:
        WinRate1v1 = rankedData['1v1'][2]
    else: WinRate1v1 = 0.0
    if '2v2' in rankedData:
        WinRate2v2 = rankedData['2v2'][2]
    else: WinRate2v2 = 0.0
    if '3v3' in rankedData:
        WinRate3v3 = rankedData['3v3'][2]
    else: WinRate3v3 = 0.0
    if '1 v 1 ladder' in ladderData:
        teamID1v1 = ladderData['1 v 1 ladder'][0]
        peak1v1 = ladderData['1 v 1 ladder'][4]
        wins1v1, games1v1 = getLadderHistory(teamID1v1, ladderID=0)
    else:
        peak1v1 = 0
        wins1v1 = 0
        games1v1 = 0
    if '2 v 2 ladder' in ladderData:
        teamID2v2 = ladderData['2 v 2 ladder'][0]
        wins2v2, games2v2 = getLadderHistory(teamID2v2, ladderID=1)
    else:
        wins2v2 = 0
        games2v2 = 0
    if '3 v 3 ladder' in ladderData:
        teamID3v3 = ladderData['3 v 3 ladder'][0]
        wins3v3, games3v3 = getLadderHistory(teamID3v3, ladderID=4)
    else:
        wins3v3 = 0
        games3v3 = 0
    if (wins1v1 + wins2v2 + wins3v3) == 0:
        winRate = Decimal(0)
    else:
        winRate = (Decimal(wins1v1 + wins2v2 + wins3v3) /
                   Decimal(games1v1 + games2v2 + games3v3)) * Decimal(100)
    score = (((((Decimal(wins1v1) * Decimal(4))
            + (Decimal(wins2v2) * Decimal(5))
            + (Decimal(wins3v3) * Decimal(6)))
            * Decimal(10) * Decimal(winRate)) +
            ((Decimal(WinRate1v1) +
              Decimal(WinRate2v2) +
              Decimal(WinRate3v3)) * Decimal(10)) +
            (Decimal(peak1v1) / Decimal(10))) /
            (Decimal(bootRate) + Decimal(10)))
    score = int(round(float(score)))
    return score

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
               str(dataPoint[1]) + " points")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    clanSet = getClans()
    clanData = dict()
    for clan in clanSet:
        clanScraper = ClanScraper(clan)
        clanName = clanScraper.getClanName()
        print "Analyzing", (clanName + "...")
        players = [member[0] for member in clanScraper.getMembers()]
        playerData = list()
        for player in players:
            playerScraper = PlayerScraper(player)
            name = playerScraper.getPlayerName()
            score = getScore(playerScraper)
            if score is not None:
                playerData.append((name, score))
        playerDataList = (sorted(playerData, key=lambda x: x[1]))
        playerDataList.reverse()
        clanData[clanName] = playerDataList
    for clanName in clanData:
        data = clanData[clanName]
        length = len(data)
        print ("Ranked " + str(length) + " members in " + unicode(clanName))
        print "   "
        printRanked(data)
        print "============"
        print "   "
