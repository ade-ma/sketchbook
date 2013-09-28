import requests as r
import BeautifulSoup as bs

bosLoganURL = "http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2010/hourly/siteonthefly.cgi?id=725090"

page = bs.BeautifulSoup(r.get(bosLoganURL).text)

urls = filter(lambda url: url.find("csv") != -1,
	map(lambda x: 'http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2010/data/' + x['href'],
		page.findAll("a", {"class":"hide"})))

for url in urls:
	open(url.split('/')[-1], 'w').write(r.get(url).text)
