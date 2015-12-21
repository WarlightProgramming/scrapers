import requests
import string
from decimal import Decimal
import datetime
from BeautifulSoup import BeautifulSoup

def getPageData(func):
    def func_wrapper(self, *args):
        if (not(hasattr(self, 'pageData'))):
            self.getData()
        return func(self, *args)
    return func_wrapper

def reformatHTML(func):
    def func_wrapper(*args):
        output = func(*args)
        if hasattr(output, '__iter__'):
            retoreTuple = False
            if (type(output) == tuple): 
                output = list(output)
                restoreTuple = True
            for x in xrange(len(output)):
                if (type(output[x]) == str or type(output[x]) == unicode):
                    output[x] = BeautifulSoup(output[x],
                                convertEntities=BeautifulSoup.\
                                HTML_ENTITIES)
            if restoreTuple: output = tuple(output)
        elif (type(output) == str or type(output) == unicode):
            output = BeautifulSoup(output, convertEntities=BeautifulSoup.\
                                   HTML_ENTITIES)
        return output
    return func_wrapper

class ContentError(Exception):
    pass

class WLScraper(object):

    def __init__(self, baseURL=None, **kwargs):
        self.baseURL = "https://www.warlight.net/"
        if baseURL is not None:
            self.baseURL = baseURL
        self.URL = self.makeURL(**kwargs)

    def makeURL(self, **kwargs):
        URL = self.baseURL
        appendString = ""
        for kwarg in kwargs:
            appendString += "&"
            appendString += str(kwarg)
            appendString += "="
            appendString += str(kwargs[kwarg])
        URL += appendString[1:]
        return URL

    def getData(self, loop=True):
        stop = False
        while (not stop):
            try:
                r = requests.get(self.URL)
                stop = True
            except:
                if (not loop): stop = True
        self.pageData = r.text

    @staticmethod
    def getValueFromBetween(text, before, after):
        if before is None: before = ""
        if after is None: after = ""
        if (before not in text):
            raise ContentError("Missing 'before' marker: " + before +
                               " in " + text)
        if (after not in text):
            raise ContentError("Missing 'after' marker! " + after +
                               " in " + text)
        beforeLoc = text.find(before) + len(before)
        value = text[beforeLoc:]
        if (after == ""): return value
        afterLoc = value.find(after)
        value = value[:afterLoc]
        return value.encode('ascii', 'ignore')

    @staticmethod
    def getTypedValue(text, marker, typeRange, check=True):
        if marker not in text:
            raise ContentError("Missing marker: " + marker + " in " +
                               text)
        loc = text.find(marker) + len(marker)
        text = text[loc:]
        data = ""
        while text[0] in typeRange:
            data += text[0]
            text = text[1:]
        if (check and (len(data) == 0)):
            raise ContentError("No content in specified range!")
        return data.encode('ascii', 'ignore')

    def getNumericValue(self, text, marker):
        return float(self.getTypedValue(text, marker, 
                                        (string.digits + ".+-")))

    def getIntegerValue(self, text, marker):
        return int(self.getTypedValue(text, marker,
                                      (string.digits + "-+")))

    def getLetterValue(self, text, marker):
        return self.getTypedValue(text, marker, (string.ascii_lowercase
                                  + string.ascii_uppercase))

    @staticmethod
    def timeConvert(timeString):
        timeData = timeString.split(" ")
        count = Decimal(0)
        fieldTimes = dict()
        fieldTimes["year"] = Decimal(24) * Decimal(365.2425)
        fieldTimes["years"] = Decimal(24) * Decimal(365.2425)
        fieldTimes["month"] = Decimal(2) * Decimal(365.2425)
        fieldTimes["months"] = Decimal(2) * Decimal(365.2425)
        fieldTimes["day"] = Decimal(24)
        fieldTimes["days"] = Decimal(24)
        fieldTimes["hour"] = Decimal(1)
        fieldTimes["hours"] = Decimal(1)
        fieldTimes["minute"] = Decimal(1) / Decimal(60)
        fieldTimes["minutes"] = Decimal(1) / Decimal(60)
        fieldTimes["second"] = Decimal(1) / Decimal(3600)
        fieldTimes["seconds"] = Decimal(1) / Decimal(3600)
        fieldData = dict()
        for field in fieldTimes:
            if field not in timeData: continue
            loc = timeData.index(field)
            if (loc == 0): continue
            data = int(timeData[loc-1])
            count += (Decimal(data) * Decimal(fieldTimes[field]))
        return float(count)

    @staticmethod
    def getDate(dateString):
        dateData = dateString.split('/')
        month, day, year = (int(dateData[0]), int(dateData[1]),
                            int(dateData[2]))
        return datetime.date(year=year, month=month, day=day)

    @staticmethod
    def getDateTime(dateTimeString):
        dateString, timeString = dateTimeString.split(" ")
        dateData = dateString.split('/')
        month, day, year = (int(dateData[0]), int(dateData[1]),
                            int(dateData[2]))
        timeData = timeString.split(':')
        hour, minute, second = (int(timeData[0]), int(timeData[1]),
                                int(timeData[2]))
        return datetime.datetime(year=year, month=month, day=day,
                                 hour=hour, minute=minute,
                                 second=second)
