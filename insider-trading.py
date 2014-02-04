from sys import argv
import urllib2
import datetime
import re
from bs4 import BeautifulSoup

stocks = {}
numDays = int(argv[1])
tickers = argv[2:]

def parseRow(row, data):
  transaction = {}
  entry = row.find_all('td')

  dateString = entry[0].string
  date = datetime.datetime.strptime(dateString, "%b %d, %Y").date()
  now = datetime.datetime.now().date()

  if ((now-date).days > numDays):
    return
  else:
    transaction["Date"] = entry[0].string
    transaction["Name"] = entry[1].a.string
    transaction["Title"] = entry[1].span.string
    transaction["Shares"] = entry[2].string
    transaction["Direction"] = parseTrade(entry[4].string)

    for key in transaction:
      print key + " : " + transaction[key]

    print "-" * 40

    transaction["Date"] = 5
    transaction["Position"] = row.td.next_sibling.span.string
    data.append(transaction)

# FIXME: make buy, sell or null
def parseTrade(string):
  pattern = re.compile("(?P<tradeType>.*) at (.*) per share")
  tradeType = pattern.search(string).groupdict()["tradeType"]
  #This will be either sale, purchase or other things
  if(tradeType):
    return tradeType
  else:
    return "Other"

for ticker in tickers:
  url = "http://finance.yahoo.com/q/it?s=" + ticker + "+Insider+Transactions"

  html = urllib2.urlopen(url).read()
  soup = BeautifulSoup(html, 'lxml')
  table = soup.find_all('table')[14]
  rows = table.find_all('tr')

  data = []

  # number of transactions (reduce to increase speed)
  for row in rows[1:]:
    parseRow(row, data)

  stocks[ticker] = data

#print stocks
# http://ichart.finance.yahoo.com/table.csv?s=GE&a=00&b=2&c=1962&d=01&e=2&f=2014&g=d&ignore=.csv