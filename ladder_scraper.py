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
            dataList = dataPoint.split("<a ")
            currentClanID, currentClanName = None, ""
            clanIDMarker = '"/Clans/?ID='
            clanNameMarker = '" title="'
            clanNameEnd = '">'
            nameMarker = teamIDString + '">'
            nameEnd = '</a'
            for dataUnit in dataList:
                if clanIDMarker in dataUnit and clanNameMarker in dataUnit:
                    currentClanID = self.getIntegerValue(dataUnit, clanIDMarker)
                    currentClanName = self.getValueFromBetween(dataUnit,
                                      clanNameMarker, clanNameEnd)
                elif nameMarker in dataUnit and nameEnd in dataUnit:
                    playerName = self.getValueFromBetween(dataUnit,
                                 nameMarker, nameEnd)
                    players.append((playerName,
                                    (currentClanID, currentClanName)))
                    currentClanID = None
                    currentClanName = ""
                else: continue
            ratingRange = dataPoint.split("<td>")[-1]
            if len(ratingRange) < 1 or type(ratingRange[0]) != int:
                teamRating = 0
            else:
                teamRating = self.getIntegerValue(ratingRange, "")
            teams.append((teamID, teamRank, rankShift, teamRating,
                          players))
        return teams

class LadderHistoryScraper(WLScraper):

    def __init__(self, ladderID, offset):
        self.baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(ID=ladderID, Offset=offset)
        self.isEmpty = False
        self.earliestTime = None
        self.gameMarker = '<tr style="background-color: inherit">'

    @getPageData
    def getGameHistory(self):
        page = self.pageData
        games = list()
        marker = "</thead>"
        end = '<div class="LadderGamesPager'
        dataRange = self.getValueFromBetween(page, marker, end)
        gameMarker = self.gameMarker
        if gameMarker not in dataRange: 
            self.isEmpty = True
            return games
        dataSet = dataRange.split(gameMarker)[1:]
        for dataPoint in dataSet:
            multiMarker = 'MultiPlayer?GameID='
            gameID = self.getIntegerValue(dataPoint,
                                          multiMarker)
            gameTime = self.getValueFromBetween(dataPoint,
                       'style="white-space: nowrap">',
                       '</td>')
            if gameTime == "": gameTime = None
            else: gameTime = self.getDateTime(gameTime)
            if "defeated" in dataPoint:
                alphaData, betaData = dataPoint.split("defeated")
                finished = True
            else:
                alphaData, betaData = dataPoint.split(" vs ")
                finished = False
            alphaTeam = self.getIntegerValue(alphaData,
                        '?LadderTeamID=')
            betaTeam = self.getIntegerValue(betaData,
                       '?LadderTeamID=')
            games.append((gameID, gameTime, alphaTeam, betaTeam, finished))
            self.earliestTime = gameTime
        return games

class LadderTeamHistoryScraper(LadderHistoryScraper):

    def __init__(self, ladderID, teamID, offset):
        self.baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(ID=ladderID, LadderTeamID=teamID, Offset=offset)
        self.isEmpty = False
        self.earliestTime = None
        self.gameMarker = '<tr style="background-color: '
