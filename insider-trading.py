from sys import argv
import urllib2
import datetime
import re
from bs4 import BeautifulSoup
import Queue
import threading

# First argument is the historical window that we want to search
numDays = int(argv[1])

# Text file containing list of tickers
tickerFile = argv[2]

def displayOutput(resultQueue, errorQueue):
  finalResult = sorted(list(resultQueue.queue), key=lambda x: x[1])
  for item in finalResult:
    print item[0].upper() + " : " + str(item[1])
  # FIXME: Print out tickers that had errors

# Helper function to get purchasing data for each ticker
def processTicker(ticker, resultQueue, errorQueue):
  #Open URL and extract insider trading table
  print "Fetching data for " + ticker.upper()
  url = "http://finance.yahoo.com/q/it?s=" + ticker + "+Insider+Transactions"
  html = urllib2.urlopen(url).read()
  soup = BeautifulSoup(html, 'lxml')
  try:
    table = soup.find_all('table')[14]
    rows = table.find_all('tr')
    # For each row, populate the number of purchases for that ticker
    trades = {}
    for row in rows[1:]:
      parseRow(row, trades)
    # Get total number of purchases
    try:
      resultQueue.put((ticker, trades["Purchase"]))
    except:
      resultQueue.put((ticker, 0))
  except:
    errorQueue.put(ticker)
    resultQueue.put((ticker, 0))

# Helper function to get list of tickers from file
def getTickers(tickerFile):
  return [line.rstrip('\n') for line in open(tickerFile)]

# Helper function to parse a row of data in the insider trade table
def parseRow(row, data):
  entry = row.find_all('td')
  dateString = entry[0].string
  date = datetime.datetime.strptime(dateString, "%b %d, %Y").date()
  now = datetime.datetime.now().date()

  # If trade is outside historical window, discard it
  if ((now-date).days > numDays):
    return

  # If trade is inside historical window, use it
  else:
    try:
      tradeSize = int(re.sub(',', '', entry[2].string))
    except:
      tradeSize = 0
    tradeType = getTradeType(entry[4].string)
    try:
      data[tradeType] = data[tradeType] + tradeSize
    except KeyError:
      data[tradeType] = tradeSize

# Helper function to parse the trade type
def getTradeType(string):
  pattern = re.compile("(?P<tradeType>.*) at (.*) per share")
  try:
    tradeType = pattern.search(string).groupdict()["tradeType"]
  except AttributeError:
    tradeType = "Other"
  return tradeType

# Main loop
insiderActivity = Queue.Queue()
errorTickers = Queue.Queue()
tickers = getTickers(tickerFile)

for ticker in tickers:
  processTicker(ticker, insiderActivity, errorTickers)

displayOutput(insiderActivity, errorTickers)