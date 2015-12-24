from scraper_core import *

class PlayerScraper(WLScraper):

    def __init__(self, playerID):
        self.baseURL = "https://www.warlight.net/Profile?"
        self.ID = playerID
        self.URL = self.makeURL(p=playerID)

    @getPageData
    def playerExists(self):
        page = self.pageData
        marker = "Sorry, the requested player was not found."
        return (marker not in page)

    @getPageData
    def getClanID(self):
        page = self.pageData
        marker = '<a href="/Clans/?ID='
        if marker not in page: return None
        return self.getIntegerValue(page, marker)

    @getPageData
    def getLocation(self):
        page = self.pageData
        marker = 'title="Plays from '
        end = '"'
        if marker not in page: return ""
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getClanName(self):
        page = self.pageData
        marker = 'border="0" />'
        if marker not in page: return ""
        return self.getLetterValue(page, marker)

    @getPageData
    def getPlayerName(self):
        page = self.pageData
        return self.getValueFromBetween(page, '<title>', ' -')

    @getPageData
    def getMemberStatus(self):
        page = self.pageData
        memberString = 'id="MemberIcon" title="WarLight Member"'
        return (memberString in page)

    @getPageData
    def getLevel(self):
        page = self.pageData
        return self.getIntegerValue(page, '<big><b>Level ')

    @getPageData
    def getPoints(self):
        page = self.pageData
        points = self.getTypedValue(page, 'days:</font> ',
                                    (string.digits + ","))
        return int(points.replace(",",""))

    @getPageData
    def getEmail(self):
        page = self.pageData
        marker = "E-mail:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getLink(self):
        page = self.pageData
        marker = "Player-supplied link:"
        end = "</a>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getValueFromBetween(dataRange, '">', None)

    @getPageData
    def getTagline(self):
        page = self.pageData
        marker = "Tagline:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getBio(self):
        page = self.pageData
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getJoinString(self):
        page = self.pageData
        marker = "Joined WarLight:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)
        
    def getJoinDate(self):
        return self.getDate(self.getJoinString())

    @getPageData
    def getMemberString(self):
        page = self.pageData
        marker = "Member since</font> "
        end = "</font>"
        if marker not in page: return ""
        return self.getValueFromBetween(page, marker, end)

    def getMemberDate(self):
        memberString = self.getMemberString()
        if memberString == "": return None
        return self.getDate(memberString)

    @getPageData
    def getCurrentGames(self):
        page = self.pageData
        dataRange = self.getValueFromBetween(page, 
                    "Currently in</font> ", "games")
        if "multi-day" not in dataRange: return 0
        return self.getIntegerValue(dataRange, "")

    @getPageData
    def getPlayedGames(self):
        page = self.pageData
        return self.getIntegerValue(page, "Played in</font> ")

    @getPageData
    def getPercentRT(self):
        page = self.pageData
        dataRange = self.getValueFromBetween(page, "Played in",
                                             "<br />")
        return self.getNumericValue(dataRange, " (")

    @getPageData
    def getLastSeenString(self):
        page = self.pageData
        marker = "Last seen </font>"
        end = "<font"
        return self.getValueFromBetween(page,
                                        marker, end)

    @getPageData
    def getLastSeen(self):
        return self.timeConvert(self.getLastSeenString())

    @getPageData
    def getBootCount(self):
        page = self.pageData
        if "never been booted" in page: return 0
        marker = "This player has been booted "
        return self.getIntegerValue(page, marker)

    @getPageData
    def getBootRate(self):
        page = self.pageData
        if "never been booted" in page: return 0.0
        marker = "This player has been booted "
        end = "</font>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getNumericValue(dataRange, " (")

    @getPageData
    def getFavoriteGames(self):
        page = self.pageData
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

    @getPageData
    def getSingleStats(self):
        page = self.pageData
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

    @getPageData
    def getTournaments(self):
        page = self.pageData
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

    @getPageData
    def getLadderData(self):
        page = self.pageData
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

    @getPageData
    def getRankedData(self):
        page = self.pageData
        marker = "<h3>Ranked Games</h3>"
        data = dict()
        if marker not in page: return data, 0, 0, 0.0
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        if "No completed ranked games" in dataRange:
            return data, 0, 0, 0.0
        rankedCount = self.getIntegerValue(dataRange,
                      "Completed</font> ")
        if "ranked games (" in dataRange:
            rankedWins = self.getIntegerValue(dataRange,
                         "ranked games (")
        else:
            rankedWins = self.getIntegerValue(dataRange,
                         "ranked game (")
        rankedPercent = Decimal(rankedWins) / Decimal(rankedCount)
        rankedPercent = float(rankedPercent * Decimal(100))
        dataSet = dataRange.split('color="#858585"')[2:]
        for dataPoint in dataSet:
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

    @getPageData
    def getPreviousNames(self):
        page = self.pageData
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

    @getPageData
    def getPlaySpeed(self):
        page = self.pageData
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
            data[typeMarker[:-1]] = avgTime
        return data

    @getPageData
    def getFavoriteMaps(self):
        page = self.pageData
        baseURL = "https://warlight.net"
        marker = "Favorite Maps</h3"
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "</td")
        dataSet = dataRange.split('a href="')[1:]
        for dataPoint in dataSet:
            link = self.getValueFromBetween(dataPoint, '', '">')
            name = self.getValueFromBetween(dataPoint, 
                   "</a> <br>", "<br>")
            author = self.getValueFromBetween(dataPoint, "by ",
                     "</font>")
            data.append((name, author, link))
        return data

    @getPageData
    def getAchievementRate(self):
        page = self.pageData
        marker = "<h3>Achievements"
        if marker not in page: return 0
        dataRange = self.getValueFromBetween(page, marker, 
                    "</font>")
        return self.getIntegerValue(dataRange, "(")
