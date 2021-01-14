import pandas as pd
import pandas_datareader as web
import datetime
from bs4 import BeautifulSoup
import requests
import re
import smtplib
import time
from apscheduler.schedulers.blocking import BlockingScheduler


def symbolToTicker(ticker):
    output = ''
    for i in ticker:
        if i == "(":
            break
        else:
            output += i
    return output


def tickerToName(ticker):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == ticker:
            return x['name']


def tickerToCIK(ticker):
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
    f = requests.get(URL.format(ticker), stream=True)
    results = CIK_RE.findall(f.text)
    if len(results) > 0:
        return results[0]
    else:
        print('CIK not found for ticker {}.'.format(ticker))
        return -1


def getS4Date(ticker):
    endpoint = r'http://www.sec.gov/cgi-bin/browse-edgar'
    param_dict = {'action': 'getcompany',
                  'type': 'S-4',
                  'CIK': tickerToCIK(ticker),
                  'owner': 'exclude',
                  'output': 'atom'}

    response = requests.get(url=endpoint, params=param_dict)
    soup = BeautifulSoup(response.content, 'lxml')
    entries = soup.find_all('entry')
    if len(entries) > 0:
        return entries[0].find('filing-date').text
    else:
        return None


def toDateTime(date):
    year = int(date[0] + date[1] + date[2] + date[3])
    month = int(date[5] + date[6])
    day = int(date[8] + date[9])
    return datetime.datetime(year, month, day)


def getWarrantPrice(ticker):
    return 0


def getReturnSinceS4(ticker, date):
    start = toDateTime(date)
    if datetime.datetime.now().hour < 16:
        end = datetime.datetime.today() - datetime.timedelta(days=1)
    else:
        end = datetime.datetime.today()
    try:
        data = web.DataReader(ticker, "yahoo", start, end)
    except:
        print("No data fetched for symbol {}.".format(ticker))
        return None
    first = data['Adj Close'][0] # first
    last = data.tail(1)['Adj Close'][0] # last
    return round(100 * (last - first) / first, 2)


def getDaysSinceS4(ticker, date):
    start = toDateTime(date)
    end = datetime.datetime.today()
    return (end - start).days


# def buildDf(): # SPAC Track
#     df = pd.read_csv('spacTrack1.csv')
#     tickers = df['SPAC Ticker']
#     CIKs = []
#     s4Dates = []
#     returnSinceS4 = []
#     daysSinceS4 = []
#     for i in range(0, len(tickers)):
#         CIKs.append(tickerToCIK(tickers[i]))
#         if CIKs[i] == -1:
#             s4Dates.append(None)
#         else:
#             s4Dates.append(getS4Date(tickers[i]))
#         if s4Dates[i] is None:
#             returnSinceS4.append(None)
#             daysSinceS4.append(None)
#         else:
#             returnSinceS4.append(getReturnSinceS4(tickers[i], s4Dates[i]))
#             daysSinceS4.append(getDaysSinceS4(tickers[i], s4Dates[i]))
#
#     df['CIK'] = CIKs
#     df['S-4 Filing Date'] = s4Dates
#     df['Returns Since S-4'] = returnSinceS4
#     df['Days Since S-4'] = daysSinceS4
#     return df
#
#
# dataframe = buildDf()
# dataframe.to_csv('spacTrack.csv')


def buildDf(): # SPAC Hero
    df = pd.read_html("https://www.spachero.com/")[3]
    symbols = df['Symbol']
    tickers = []
    CIKs = []
    s4Dates = []
    returnSinceS4 = []
    daysSinceS4 = []
    for i in range(0, len(symbols)):
        tickers.append(symbolToTicker(symbols[i]))
        CIKs.append(tickerToCIK(tickers[i]))
        if CIKs[i] == -1:
            s4Dates.append(None)
        else:
            s4Dates.append(getS4Date(tickers[i]))
        if s4Dates[i] is None:
            returnSinceS4.append(None)
            daysSinceS4.append(None)
        else:
            returnSinceS4.append(getReturnSinceS4(tickers[i], s4Dates[i]))
            daysSinceS4.append(getDaysSinceS4(tickers[i], s4Dates[i]))

    df['Symbol'] = tickers
    df['CIK'] = CIKs
    df['S-4 Filing Date'] = s4Dates
    df['Returns Since S-4'] = returnSinceS4
    df['Days Since S-4'] = daysSinceS4
    return df


def sendEmail(to, _from, message):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("username", "password")
    s.sendmail(_from, to, message)
    s.quit()


def findNewS4():
    df = pd.read_csv('spacHero.csv')
    filingDates = df['S-4 Filing Date']

    for i in range(0, len(filingDates)):
        if getS4Date(df['Symbol'][i]) is None and str(filingDates[i]) == 'nan' \
                or getS4Date(df['Symbol'][i]) == filingDates[i]:
            continue
        else:
            print('New S-4 Filing for {0} at {1}.'.format(df['Symbol'][i]), datetime.datetime.now())
            sendEmail("sender", "receiver", message="""\

Subject: Email Notification Testing

Ticker {0} has a new S-4 Filing as of {1}""".format(df['Symbol'][i], datetime.datetime.today()))
    print('S-4 Filings have been updated as of {}'.format(datetime.datetime.now()))
    dataframe = buildDf()
    dataframe.to_csv('spacHero.csv')


sched = BlockingScheduler()
sched.add_job(findNewS4, 'cron', day_of_week='mon-fri', hour=9)
sched.start()
