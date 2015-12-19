import clan_scraper
import player_scraper
import statistics
from decimal import Decimal
import requests

if __name__ == "__main__":
	requests.packages.urllib3.disable_warnings()
	clanSet = clan_scraper.getClans()
	clanData = dict()
	for clan in clanSet:
		clanPcts = list()
		clanCount = 0
		clanGames = 0
		clanWins = 0
		clanPeak = None
		clanTrough = None
		cs = clan_scraper.ClanScraper(clan)
		name = cs.getClanName()
		print "Analyzing", (name + "...")
		members = cs.getMembers()
		memberIDs = [member[0] for member in members]
		for memberID in memberIDs:
			ps = player_scraper.PlayerScraper(memberID)
			rd = ps.getRankedData()[0]
			if '1v1' in rd:
				data1v1 = rd['1v1']
				clanCount += 1
				clanWins += data1v1[0]
				clanGames += data1v1[1]
				clanPcts.append(data1v1[2])
				if clanPeak is None or data1v1[2] > clanPeak:
					clanPeak = data1v1[2]
				if clanTrough is None or data1v1[2] < clanTrough:
					clanTrough = data1v1[2]
		if len(clanPcts) > 0:
			clanAvg = statistics.mean(clanPcts)
			clanMedian = statistics.median(clanPcts)
		else: clanAvg = clanMedian = 0.0
		if clanGames == 0: clanGames = 1
		clanPct = float(Decimal(clanWins) / Decimal(clanGames))
		clanData[name] = (clanCount, clanWins, clanGames,
			              clanPeak, clanTrough, clanAvg,
			              clanMedian, clanPct)
	for clanName in clanData:
		clanInfo = clanData[clanName]
		clanWins = clanInfo[1]
		clanGames = clanInfo[2]
		clanPeak = clanInfo[3]
		clanTrough = clanInfo[4]
		clanAvg = clanInfo[5]
		clanMedian = clanInfo[6]
		clanPct = clanInfo[7]
		clanString = (clanName + ": " + str(clanWins) + " wins across "
			          + str(clanGames) + " games by " + str(clanCount)
			          + " players (best percentage: " + str(clanPeak) +
			          "; worst percentage: " + str(clanTrough) +
			          "; average percentage: " + str(clanAvg) +
			          "; median percentage: " + str(clanMedian) +
			          "; overall percentage: " + str(clanPct)) + ")"
		print clanString
