from sys import argv
import urllib2
import datetime
import re
from bs4 import BeautifulSoup

numDays = int(argv[1])
tickers = argv[2:]

def parseRow(row, data):

  entry = row.find_all('td')
  dateString = entry[0].string
  date = datetime.datetime.strptime(dateString, "%b %d, %Y").date()
  now = datetime.datetime.now().date()

  if ((now-date).days > numDays):
    return
  else:
    # Name is entry[1].a.string
    # Executive title is entry[1].span.string
    tradeSize = int(re.sub(',', '', entry[2].string.encode('ascii', 'ignore')))
    tradeType = getTradeType(entry[4].string.encode('ascii', 'ignore'))
    try:
      data[tradeType] = data[tradeType] + tradeSize
    except KeyError:
      data[tradeType] = tradeSize

def getTradeType(string):
  pattern = re.compile("(?P<tradeType>.*) at (.*) per share")
  tradeType = pattern.search(string).groupdict()["tradeType"]
  #This will be either sale, purchase or other things
  if(tradeType):
    return tradeType
  else:
    return "Other"

# Main loop
insiderActivity = {}
for ticker in tickers:
  url = "http://finance.yahoo.com/q/it?s=" + ticker + "+Insider+Transactions"

  html = urllib2.urlopen(url).read()
  soup = BeautifulSoup(html, 'lxml')
  table = soup.find_all('table')[14]
  rows = table.find_all('tr')

  trades = {}

  # number of transactions (reduce to increase speed)
  for row in rows[1:]:
    parseRow(row, trades)

  print ticker.upper()
  for trade in trades:
    print trade + " : " + str(trades[trade])
  print "-" * 40

  insiderActivity[ticker] = trades

#print stocks
# http://ichart.finance.yahoo.com/table.csv?s=GE&a=00&b=2&c=1962&d=01&e=2&f=2014&g=d&ignore=.csv