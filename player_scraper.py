from scraper_core import *

class PlayerScraper(WLScraper):

    def __init__(self, playerID):
        self.baseURL = "https://www.warlight.net/Profile?p="
        self.URL = self.makeURL(playerID)
        self.pageData = list()
        self.playerData = dict()

    def makeURL(self, playerID):
        return self.baseURL + str(playerID)

    def getpagedata(func):
        def func_wrapper(self, *args):
            if (len(self.pageData) != 1):
                self.getData()
            return func(self, *args)
        return func_wrapper

    @getpagedata
    def getClanID(self):
        page = self.pageData[0]
        return self.getIntegerValue(page, '<a href="/Clans/?ID=')

    @getpagedata
    def getClanName(self):
        page = self.pageData[0]
        return self.getLetterValue(page, 'border="0" />')

    @getpagedata
    def getPlayerName(self):
        page = self.pageData[0]
        return self.getLetterValue(page, '<title>')

    @getpagedata
    def getMemberStatus(self):
        page = self.pageData[0]
        memberString = 'id="MemberIcon" title="WarLight Member"'
        return (memberString in page)

    @getpagedata
    def getLevel(self):
        page = self.pageData[0]
        return self.getIntegerValue(page, '<big><b>Level ')

    @getpagedata
    def getPoints(self):
        page = self.pageData[0]
        points = self.getTypedValue(page, 'days:</font> ',
                                    (string.digits + ","))
        return int(points.replace(",",""))

    @getpagedata
    def getEmail(self):
        page = self.pageData[0]
        marker = "E-mail:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getpagedata
    def getLink(self):
        page = self.pageData[0]
        marker = "Player-supplied link:"
        end = "</a>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getValueFromBetween(dataRange, '">', None)

    @getpagedata
    def getTagline(self):
        page = self.pageData[0]
        marker = "Tagline:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getpagedata
    def getBio(self):
        page = self.pageData[0]
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getpagedata
    def getJoinString(self):
        page = self.pageData[0]
        marker = "Joined WarLight:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)
        
    def getJoinDate(self):
        return self.getDate(self.getJoinString())

    @getpagedata
    def getMemberString(self):
        page = self.pageData[0]
        marker = "Member since</font> "
        end = "</font>"
        if marker not in page: return ""
        return self.getValueFromBetween(page, marker, end)

    def getMemberDate(self):
        memberString = self.getMemberString()
        if memberString == "": return None
        return self.getDate(memberString)

    @getpagedata
    def getCurrentGames(self):
        page = self.pageData[0]
        dataRange = self.getValueFromBetween(page, 
                    "Currently in</font> ", "games")
        if "multi-day" not in dataRange: return 0
        return self.getIntegerValue(dataRange, "")

    @getpagedata
    def getPlayedGames(self):
        page = self.pageData[0]
        return self.getIntegerValue(page, "Played in</font> ")

    @getpagedata
    def getPercentRT(self):
        page = self.pageData[0]
        dataRange = self.getValueFromBetween(page, "Played in",
                                             "<br />")
        return self.getNumericValue(dataRange, " (")

    @getpagedata
    def getLastSeen(self):
        page = self.pageData[0]
        marker = "Last seen </font>"
        end = "<font"
        return self.timeConvert(self.getValueFromBetween(page,
                                marker, end))

    @getpagedata
    def getBootCount(self):
        page = self.pageData[0]
        if "never been booted" in page: return 0
        marker = "This player has been booted "
        return self.getIntegerValue(page, marker)

    @getpagedata
    def getBootRate(self):
        page = self.pageData[0]
        marker = "This player has been booted "
        end = "</font>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getNumericValue(dataRange, " (")

    @getpagedata
    def getFavoriteGames(self):
        page = self.pageData[0]
        data = list()
        marker = "<h3>Favorite Games</h3>"
        if marker not in page: return data
        end = "<h3>"
        dataRange = self.getValueFromBetween(page, marker, end)
        dataSet = dataRange.split("GameID=")[1:]
        for dataPoint in dataSet:
            gameID = self.getIntegerValue(dataPoint, "")
            gameName = self.getValueFromBetween(dataPoint,
                       '">', "</a>")
            gameData = (gameID, gameName)
            data.append(gameData)
        return data

    @getpagedata
    def getSingleStats(self):
        page = self.pageData[0]
        marker = "<h3>Single-player stats</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split('color="#858585')[1:]
        for dataPoint in dataSet:
            levelName = self.getValueFromBetween(dataPoint, '">',
                        ':</font>')
            levelTurns = self.getIntegerValue(dataPoint, "Won in ")
            data[levelName] = levelTurns
        return data

    @getpagedata
    def getTournaments(self):
        page = self.pageData[0]
        marker = "<h3>Tournaments</h3>"
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split("- ")[1:]
        for dataPoint in dataSet:
            rank = self.getIntegerValue(dataPoint, "")
            tourneyID = self.getIntegerValue(dataPoint,
                        "TournamentID=")
            tourneyName = self.getValueFromBetween(dataPoint, '">',
                          "</a>")
            data.append((tourneyID, tourneyName, rank))
        return data

    @getpagedata
    def getLadderData(self):
        page = self.pageData[0]
        marker = "<h3>Ladder Statistics</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split("a href=")[1:]
        for dataPoint in dataSet:
            teamID = self.getIntegerValue(dataPoint, "TeamID=")
            ladderName = self.getValueFromBetween(dataPoint, '">',
                         "</a>")
            if ("Not Ranked" in dataPoint):
                rank = 0
            else: rank = self.getIntegerValue(dataPoint, "Ranked ")
            rating = self.getIntegerValue(dataPoint, "rating of ")
            if ("Best rating ever:" not in dataPoint):
                peakRating = 0
            else: peakRating = self.getIntegerValue(dataPoint,
                               "Best rating ever: ")
            if ("best rank ever: " not in dataPoint):
                peakRank = 0
            else: peakRank = self.getIntegerValue(dataPoint,
                             "best rank ever: ")
            data[ladderName] = (teamID, rank, rating, 
                                peakRank, peakRating)
        return data

    @getpagedata
    def getRankedData(self):
        page = self.pageData[0]
        marker = "<h3>Ranked Games</h3>"
        data = dict()
        if marker not in page: return data, 0, 0, 0.0
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        rankedCount = self.getIntegerValue(dataRange,
                      "Completed</font> ")
        rankedWins = self.getIntegerValue(dataRange,
                     "ranked games (")
        rankedPercent = Decimal(rankedWins) / Decimal(rankedCount)
        rankedPercent = float(rankedPercent * Decimal(100))
        dataSet = dataRange.split('color="#858585"')[2:]
        for dataPoint in dataSet:
            print dataPoint
            gameType = self.getValueFromBetween(dataPoint,
                       '>', ':</font')
            gamesWon = self.getIntegerValue(dataPoint,
                       "</font> ")
            gamesPlayed = self.getIntegerValue(dataPoint,
                          " / ")
            winPercent = Decimal(gamesWon) / Decimal(gamesPlayed)
            winPercent = float(winPercent * Decimal(100))
            data[gameType] = (gamesWon, gamesPlayed, winPercent)
        return data, rankedWins, rankedCount, rankedPercent

    @getpagedata
    def getPreviousNames(self):
        page = self.pageData[0]
        marker = "<h3>Previously known as..."
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split('&nbsp;&nbsp;&nbsp;')[1:]
        for dataPoint in dataSet:
            name = self.getValueFromBetween(dataPoint, None, " <font")
            untilString = self.getValueFromBetween(dataPoint,
                          '"gray">(', ")")
            until = self.getDate(untilString)
            data.append((name, until))
        return data

    @getpagedata
    def getPlaySpeed(self):
        page = self.pageData[0]
        marker = "<h3>Play Speed</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        typeMarkers = ["Multi-Day Games:", "Real-Time Games:"]
        for typeMarker in typeMarkers:
            markedRange = self.getValueFromBetween(dataRange,
                          typeMarker, "<h5")
            avgString = self.getValueFromBetween(markedRange,
                        "Average:</font> ", "<br />")
            avgTime = self.timeConvert(avgString)
            data[typeMarker] = avgTime
        return data

    @getpagedata
    def getFavoriteMaps(self):
        page = self.pageData[0]
        baseURL = "https://warlight.net"
        marker = "Favorite Maps</h3"
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "</td")
        dataSet = dataRange.split('a href="')[1:]
        for dataPoint in dataSet:
            print dataPoint
            link = self.getValueFromBetween(dataPoint, '', '">')
            name = self.getValueFromBetween(dataPoint, 
                   "</a> <br>", "<br>")
            author = self.getValueFromBetween(dataPoint, "by ",
                     "</font>")
            data.append((name, author, link))
        return data

    @getpagedata
    def getAchievementRate(self):
        page = self.pageData[0]
        marker = "<h3>Achievements"
        if marker not in page: return 0
        dataRange = self.getValueFromBetween(page, marker, 
                    "</font>")
        return self.getIntegerValue(dataRange, "(")
