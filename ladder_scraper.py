from scraper_core import *

class LadderScraper(WLScraper):

    def __init__(self, ladderID):
        self.baseURL = "https://www.warlight.net/LadderSeason?"
        self.ID = ladderID
        self.URL = self.makeURL(ID=ladderID)

    @getPageData
    def getSize(self):
        page = self.pageData
        marker = "<td>There are currently "
        return self.getIntegerValue(page, marker)

    @staticmethod
    def trimUnranked(teams):
        trimmedTeams = [team for team in teams if team[1] != 0]
        return trimmedTeams

    def getTeams(self, rankedOnly=False):
        offset = 0
        stop = False
        allTeams = list()
        while(not stop):
            rankScraper = LadderRankingScraper(self.ID, offset)
            allTeams += rankScraper.getLadderTeams()
            if ((rankScraper.isEmpty) or 
                (rankedOnly and rankScraper.hasUnranked)):
                stop = True
            offset += 50
        if rankedOnly: 
            allTeams = self.trimUnranked(allTeams)
        self.allTeams = allTeams
        return allTeams

class LadderRankingScraper(WLScraper):

    def __init__(self, ladderID, offset):
        self.baseURL = "https://www.warlight.net/LadderTeams?"
        self.URL = self.makeURL(ID=ladderID, Offset=offset)

    @staticmethod
    def getClan(player):
        clanMarker = "/Clans/?ID="
        if clanMarker not in player:
            return None, ""
        clanID = self.getIntegerValue(player, clanMarker)
        clanName = self.getValueFromBetween(player, '" title=',
                                            '">')
        self.hasUnranked = False
        self.isEmpty = False

    @getPageData
    def getLadderTeams(self):
        page = self.pageData
        marker = '</thead>'
        end = '<table class="LadderTeamsPager">'
        dataRange = self.getValueFromBetween(page, marker, end)
        teams = list()
        if ("<tr >" not in dataRange): 
            self.isEmpty = True
            return teams
        dataSet = dataRange.split("<tr >")[1:]
        upArrow = 'img src="/Images/UpArrow.png"'
        downArrow = 'img src="/Images/DownArrow.png"'
        for dataPoint in dataSet:
            if ("<td>Not Ranked </td>" in dataPoint):
                teamRank = 0
                self.hasUnranked = True
            else:
                teamRank = self.getIntegerValue(dataPoint, "<td>")
            rankShift = (dataPoint.count(upArrow) - 
                         dataPoint.count(downArrow))
            teamMarker = 'LadderTeam?LadderTeamID='
            teamID = self.getIntegerValue(dataPoint, teamMarker)
            teamIDString = teamMarker + str(teamID)
            players = list()
            playerList = dataPoint.split(" and ")
            for player in playerList:
                clanID, clanName = self.getClan(player)
                nameMarker = teamIDString + '">'
                playerName = self.getValueFromBetween(nameMarker,
                             "</a>")
                players.append(playerName, (clanID, clanName))
            ratingRange = dataPoint.split("<td>")[-1]
            teamRating = self.getIntegerValue(rankingRange, "")
            teams.append((teamID, teamRank, rankShift, teamRating,
                          players))
        return teams

class LadderHistoryScraper(WLScraper):

    def __init__(self, ladderID, offset):
        self.baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(ID=ladderID, Offset=offset)
        self.isEmpty = False
        self.earliestTime = None

    @getPageData
    def getGameHistory(self):
        page = self.pageData
        games = list()
        marker = "</thead>"
        end = "</table>"
        dataRange = self.getValueFromBetween(page, marker, end)
        gameMarker = '<tr style="background-color: inherit">'
        if gameMarker not in dataRange: 
            self.isEmpty = True
            return games
        dataSet = dataRange.split(gameMarker)[1:]
        for dataPoint in dataSet:
            gameID = self.getIntegerValue(dataPoint,
                     'href="MultiPlayer?GameID=')
            gameTime = self.getValueFromBetween(dataPoint,
                       'style="white-space: nowrap">',
                       '</td>')
            gameTime = self.getDateTime(gameTime)
            winnerData, loserData = dataPoint.split("defeated")
            winningTeam = self.getIntegerValue(winnerData,
                          '?LadderTeamID=')
            losingTeam = self.getIntegerValue(loserData,
                         '?LadderTeamID=')
            games.append((gameID, gameTime, winningTeam, losingTeam))
            self.earliestTime = gameTime
        return games