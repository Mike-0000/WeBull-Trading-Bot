from webull import webull  # for paper trading, import 'paper_webull'
from datetime import datetime
import time
import config.userconfig as cfg

wb = webull()
# print(wb.get_mfa(cfg.wb_email))
# print(wb.get_security(cfg.wb_email))
ASTR_BUY = 4.35
ASTR_SELL = 4.65
UPDATE_INTERVAL = 3
ASTR_symbol = 'ASTR'

data = wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER)
                # 6 digits MFA, Security Question ID, Question Answer.

wb.get_trade_token(cfg.TRADE_TOKEN)

print(data)

counter = 0
ASTRLevel = 1


def getPositions(ticker):
    positions1 = wb.get_positions()
    for symbols in positions1:
        if str(symbols['ticker']['symbol']) == ticker:
            return float(symbols['position'])


def getAnalysis(ticker):
    return wb.get_analysis(ticker)


def getAsk(ticker):
    min1 = 999999
    asks = getBidsAsks(ticker, "ask")
    for price in asks:
        if float(price["price"]) < min1:  # FIND MIN CURRENT ASK
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


def placeOrder(ticker, num, ask, mode):
    wb.place_order(stock=ticker, price=ask, action=mode, orderType='LMT', enforce='GTC',
                   quant=num)
    print(mode + ": " + str(num) + " for $" + str(ask))

while 0 < 1:
    try:
        now = datetime.now()
        current_time = now.hour

        if current_time >= 4 and current_time <= 21:  # Is Market Open??

            numOfASTR = getPositions(ASTR_symbol)

            ASTRprice = getPrice(ASTR_symbol)  # Get price from analysis

            ASTRask = getAsk(ASTR_symbol)

            ASTRbid = getBid(ASTR_symbol)

            ###   ASTR LOGIC

            if counter % UPDATE_INTERVAL == 0:
                print("Bid: " + str(ASTRbid) + " Ask: " + str(ASTRask))

            if ASTRLevel == 2:
                print("triggered")
                time.sleep(100)

                ### BUYING ASTR

            if ASTRask <= ASTR_BUY and ASTRLevel == 2:  # BUYING
                placeOrder(ASTR_symbol, int(getPositions(ASTR_symbol)+7), ASTRask, "BUY")
                ASTRLevel = ASTRLevel - 1

                ### SELLING ASTR

            if ASTRbid >= ASTR_SELL and ASTRLevel == 1:  # SELLING
                print("SOLD: " + ASTRbid)
                placeOrder(ASTR_symbol, int(getPositions(ASTR_symbol)/2), ASTRbid, "SELL")
                ASTRLevel = ASTRLevel + 1

        ###  Misc Logic
        else:
            # print(current_time)
            time.sleep(180)
            print("Market Closed")
            counter = counter + 1
            if counter % 8 == 0:
                print(wb.refresh_login())


        time.sleep(1)
        counter = counter + 1
        if counter > 400:
            print(wb.refresh_login())  # Login Refresh
            wb.get_trade_token(cfg.TRADE_TOKEN)
            counter = 0  # RESET COUNTER


    except:
        while True:
            try:
                print("Broken: Continuing")
                wb.logout()
                time.sleep(10)
                print(wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER))
                # 6 digits MFA, Security Question ID, Question Answer.
                time.sleep(1)
                break
            except:
                continue
        continue
