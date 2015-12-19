from scraper_core import *
import requests

class ClanScraper(WLScraper):

    def __init__(self, clanID):
        self.baseURL = "https://www.warlight.net/Clans/?"
        self.ID = clanID
        self.URL = self.makeURL(ID=clanID)

    @getPageData
    def getClanName(self):
        page = self.pageData
        return self.getValueFromBetween(page, "<title>", " -")

    @getPageData
    def getMemberCount(self):
        page = self.pageData
        marker = "Number of members:</font> "
        return self.getIntegerValue(page, marker)

    @getPageData
    def getLink(self):
        page = self.pageData
        marker = 'Link:</font> <a rel="nofollow" href="'
        end = '">'
        link = self.getValueFromBetween(page, marker, end)
        if link == "http://": return ""
        return link

    @getPageData
    def getTagline(self):
        page = self.pageData
        marker = 'Tagline:</font> '
        end = '<br />'
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getCreatedDate(self):
        page = self.pageData
        marker = "Created:</font> "
        end = "<br"
        dateString = self.getValueFromBetween(page, marker, end)
        return self.getDate(dateString)

    @getPageData
    def getBio(self):
        page = self.pageData
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @getPageData
    def getMembers(self):
        page = self.pageData
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

def getClans():
    URL = "https://www.warlight.net/Clans/List"
    r = requests.get(URL)
    clanSet = set()
    clanData = r.text.split("/Clans/?ID=")[1:]
    for clan in clanData:
        clanID = ""
        while clan[0] in string.digits:
            clanID += clan[0]
            clan = clan[1:]
        clanSet.add(int(clanID))
    return clanSet