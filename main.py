from webull import webull  # for paper trading, import 'paper_webull'
from datetime import datetime
import time
import config.userconfig as cfg

wb = webull()
# print(wb.get_mfa(cfg.wb_email))
# print(wb.get_security(cfg.wb_email))
BUY_PRICE = 4.35
SELL_PRICE = 4.65
UPDATE_INTERVAL = 1
TICKER = 'ASTR'

data = wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER) # 6 digits MFA, Security Question ID, Question Answer.
wb.get_trade_token(cfg.TRADE_TOKEN)

print(data)

counter = 0
ASTRLevel = 1

def getPositions(num):
    positions1 = wb.get_positions()
    positions2 = positions1[num]
    return positions2['position']

def getAnalysis(ticker):
    return wb.get_analysis(ticker)

def getAsk(ticker):
    min1 = 99999
    asks = getBidsAsks(ticker, "ask")
    for price in asks:
        if float(price["price"]) < min1:  # FIND MAX CURRENT BID
            min1 = float(price["price"])
    return float(min1)

def getBid(ticker):
    max1 = 0
    bids = getBidsAsks(ticker, "bid")
    for price in bids:
        if float(price["price"]) > max1:  # FIND MAX CURRENT BID
            max1 = float(price["price"])
    return float(max1)

def getBidsAsks(ticker, mode):
    quote = wb.get_quote(ticker)
    askbidlist = quote['depth']
    asks = askbidlist['ntvAggAskList']
    bids = askbidlist['ntvAggBidList']
    if mode == 'bid':
        return bids
    else:
        return asks

def getPrice(ticker):
    stock = getAnalysis(ticker)
    return stock['targetPrice']['current']

while 0 < 1:
    try:
        now = datetime.now()
        current_time = now.hour
        if current_time >= 4 or current_time <= 4:     #    Is Market Open??

            numOfASTR = getPositions(0)

            price = getPrice(TICKER)  #  Get price from analysis

            ask = getAsk(TICKER)

            bid = getBid(TICKER)

            if counter % UPDATE_INTERVAL == 0:
                print("Bid: " + str(bid) + " Ask: " + str(ask))

            if ASTRLevel == 2:
                print("triggered")
                time.sleep(100)

            if ask <= BUY_PRICE and ASTRLevel == 2:     # BUYING
                print("Bought: " + ask)
                wb.place_order(stock=TICKER, price=ask, action='BUY', orderType='LMT', enforce='GTC', quant=numOfASTR+7)
                ASTRLevel = ASTRLevel - 1

            if bid >= SELL_PRICE and ASTRLevel == 1:    # SELLING
                print("SOLD: " + bid)
                wb.place_order(stock=TICKER, price=bid, action='SELL', orderType='LMT', enforce='GTC', quant=numOfASTR/2)
                ASTRLevel = ASTRLevel + 1

        else:
            #print(current_time)
            time.sleep(180)
            print("Market Closed")
            counter = counter + 1
            if counter % 8 == 6:
                print(wb.refresh_login())
        time.sleep(1)
        counter = counter + 1
        if counter > 400:
            print(wb.refresh_login()) # Login Refresh
            wb.get_trade_token(cfg.TRADE_TOKEN)
            counter = 0  # RESET COUNTER


    except:
        while True:
            try:
                print("Broken: Continuing")
                wb.logout()
                time.sleep(10)
                print(wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER))  # 6 digits MFA, Security Question ID, Question Answer.
                time.sleep(1)
                break
            except:
                continue
        continue
