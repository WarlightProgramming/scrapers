from scraper_core import *

class ClanScraper(WLScraper):

    def __init__(self, clanID):
        self.baseURL = "https://www.warlight.net/Clans/?ID="
        self.URL = self.makeURL(clanID)
        self.pageData = list()
        self.playerData = list()

    def makeURL(self, clanID):
        return self.baseURL + str(clanID)

    def getpagedata(func):
        def func_wrapper(self, *args):
            if (len(self.pageData) != 1):
                self.getData()
            return func(self, *args)
        return func_wrapper

    @getpagedata
    def getClanName(self):
        page = self.pageData[0]
        return self.getValueFromBetween(page, "<title>", " -")

    @getpagedata
    def getMemberCount(self):
        page = self.pageData[0]
        marker = "Number of members:</font> "
        return self.getIntegerValue(page, marker)

    @getpagedata
    def getLink(self):
        page = self.pageData[0]
        marker = 'Link:</font> <a rel="nofollow" href="'
        end = '">'
        link = self.getValueFromBetween(page, marker, end)
        if link == "http://": return ""
        return link

    @getpagedata
    def getTagline(self):
        page = self.pageData[0]
        marker = 'Tagline:</font> '
        end = '<br />'
        return self.getValueFromBetween(page, marker, end)

    @getpagedata
    def getCreatedDate(self):
        page = self.pageData[0]
        marker = "Created:</font> "
        end = "<br"
        dateString = self.getValueFromBetween(page, marker, end)
        return self.getDate(dateString)

    @getpagedata
    def getBio(self):
        page = self.pageData[0]
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getpagedata
    def getMembers(self):
        page = self.pageData[0]
        marker = '<table class="dataTable">'
        end = '</table>'
        data = list()
        dataRange = self.getValueFromBetween(page, marker, end)
        dataSet = dataRange.split('<tr>')[2:]
        for dataPoint in dataSet:
            playerID = self.getIntegerValue(dataPoint, "/Profile?p=")
            playerName = self.getValueFromBetween(dataPoint,
                         '">', '</a>')
            titleRange = dataPoint.split("<td>")[-1]
            playerTitle = self.getValueFromBetween(titleRange, "",
                          "</td")
            data.append((playerID, playerName, playerTitle))
        return data
