from clan_scraper import *
from player_scraper import *
from ladder_scraper import *
import requests

def getPlayersOnTeam(teamID):
    players = list()
    baseURL = "https://www.warlight.net/LadderTeam?"
    teamScraper = WLScraper(baseURL, LadderTeamID=teamID)
    profileMarker = "Profile?p="
    teamScraper.getData()
    page = teamScraper.pageData
    while profileMarker in page:
        players.append(teamScraper.getIntegerValue(page, 
                       profileMarker))
        loc = page.find(profileMarker) + len(profileMarker)
        page = page[loc:]
    return players

def getAllPlayers():
    playerIDs = set()
    for clanID in getClans():
        clan = ClanScraper(clanID)
        for member in clan.getMembers():
            playerIDs.add(member[0])
    ladders = [0, 1, 3, 4] + range(4000, 4022)
    for ladderID in ladders:
        ladder = LadderScraper(ladderID)
        teams = ladder.getTeams()
        for teamData in teams:
            teamID = teamData[0]
            for player in getPlayersOnTeam(teamID):
                playerIDs.add(player)
    return playerIDs

def getQualifiedPlayers(minRates, maxBoot, minPoints):
    playerSet = getAllPlayers()
    qualifiedPlayers = set()
    for player in playerSet:
        ps = PlayerScraper(player)
        points = ps.getPoints()
        bootRate = ps.getBootRate()
        rankedData = ps.getRankedData()[0]
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
        if failure: continue
        playerSet.add(player)
    return playerSet

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    minRates = dict()
    minRates['1v1'] = 65
    minRates['2v2'] = 60
    minRates['3v3'] = 60
    players = getQualifiedPlayers(minRates, 8, 200000)
    for player in players:
        print ("https://www.warlight.net/Profile?p=" + str(player))
