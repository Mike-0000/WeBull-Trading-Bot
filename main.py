from webull import webull  # for paper trading, import 'paper_webull'
from datetime import datetime
import time
import config.userconfig as cfg

wb = webull()
# print(wb.get_mfa(cfg.wb_email))
# print(wb.get_security(cfg.wb_email))

DOGE_BUY = 0.1172
DOGE_SELL = 0.125
ASTR_BUY = 4.15
ASTR_SELLS = [4.5, 4.75]
# ASTR_SELL2 = 4.7
UPDATE_INTERVAL = 60
ASTR_symbol = 'ASTR'
DOGE_SYMBOL = 'DOGEUSD'

global SELL_DATA

data = wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER)
# 6 digits MFA, Security Question ID, Question Answer.

wb.get_trade_token(cfg.TRADE_TOKEN)

counter = 0
ASTRLevel = 0


def getPriceWeight(setPrice, currentPrice):
    difference = currentPrice / setPrice
    percentage = 1 - difference
    if percentage < 0:
        percentage = -percentage
    return percentage


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

def getCryptoAsk(ticker):
    ask = getCryptoBidsAsks(ticker, "ask")
    return float(ask)


def getCryptoBid(ticker):
    bid = getCryptoBidsAsks(ticker, "bid")
    return float(bid)


def getBidsAsks(ticker, mode):
    quote = wb.get_quote(ticker)
    #print(quote)
    askbidlist = quote['depth']
    asks = askbidlist['ntvAggAskList']
    bids = askbidlist['ntvAggBidList']
    if mode == 'bid':
        return bids
    else:
        return asks

def getCryptoBidsAsks(ticker, mode):
        quote = wb.get_quote(ticker)
        asks = quote["askList"][0]['price']
        bids = quote["bidList"][0]['price']
        if mode == 'bid':
            return bids
        else:
            return asks

def placeCryptoOrder(ticker, num, ask, mode):
    d = wb.place_order_crypto(stock=ticker, action=mode, orderType='MKT', quant=num, enforce="IOC", entrust_type='QTY')
    print(mode + ": " + str(num) + " for $" + str(ask))
    print(d)
    return d


def placeOrder(ticker, num, ask, mode):
    d = wb.place_order(stock=ticker, price=ask, action=mode, orderType='LMT', enforce='GTC', quant=num)
    print(mode + ": " + str(num) + " for $" + str(ask))
    return d


while 0 < 1:
    # try:
        now = datetime.now()
        current_time = now.hour








        #  US Stock Market

        if current_time >= 7 and current_time <= 19:  # Is Market Open??

            ### Collect position information
            numOfASTR = getPositions(ASTR_symbol)

            if numOfASTR >= 120 and ASTRLevel != 0:
                ASTRLevel = 0
                print("Setting level to 0")
            if numOfASTR < 120 and numOfASTR > 40 and ASTRLevel != 1:
                ASTRLevel = 1
                print("Setting level to 1")
            if numOfASTR <= 40 and ASTRLevel != 2:
                ASTRLevel = 2
                print("Setting level to 2")

            # Get current price from analysis

            # Get current bid and ask

            ASTRask = getAsk(ASTR_symbol)  ### ASTR
            ASTRbid = getBid(ASTR_symbol)

            ###   ASTR LOGIC
            ### Checking If Order Filled Logic
            if ASTRLevel == 1 and numOfASTR > 150:  ### Check if Order is filled
                time.sleep(60)  ### If not, allow time for order to be filled
                if numOfASTR > 150:  ### If Order still not filled, cancel order and reset level.
                    print(wb.cancel_all_orders())
                    ASTRLevel = 0
                    continue

            if counter % UPDATE_INTERVAL == 0:
                print("ASTR Bid: " + str(ASTRbid) + " Ask: " + str(ASTRask))
                print("Level: " + str(ASTRLevel) + " Position: " + str(numOfASTR))
                print("Buy at: " + str(ASTR_BUY) + " Sell At: " + str(ASTR_SELLS[ASTRLevel]))

            sell_astr = getPriceWeight(ASTR_SELLS[ASTRLevel], ASTRbid)  ### ASTR
            buy_astr = getPriceWeight(ASTR_BUY, ASTRask)

            if sell_astr < 0.01:
                placeOrder(ASTR_symbol, 1, ASTRbid, "SELL")
                time.sleep(1000 * sell_astr)  # print("SELL 1 @ " + str(ASTRbid))

            if buy_astr < 0.01:
                placeOrder(ASTR_symbol, 1, ASTRask, "BUY")
                time.sleep(1000 * buy_astr)  # print("SELL 1 @ " + str(ASTRask))

            ### BUYING ASTR

            # if ASTRask <= ASTR_BUY and ASTRLevel >= 1:  # BUYING  #     placeOrder(ASTR_symbol, int(getPositions(ASTR_symbol)+5), ASTRask+0.02, "BUY")  #     ASTRLevel = ASTRLevel - 1  #  # ### SELLING ASTR  #  # if ASTRbid >= ASTR_SELLS[0] and ASTRLevel == 0:  # SELLING  #     SELL_DATA = placeOrder(ASTR_symbol, int(getPositions(ASTR_symbol)/2), ASTRbid-0.02, "SELL")  #     ASTRLevel = ASTRLevel + 1  #  # if ASTRbid >= ASTR_SELLS[1] and ASTRLevel == 1:  # SELLING Level 2  #     SELL_DATA2 = placeOrder(ASTR_symbol, int(getPositions(ASTR_symbol)/2), ASTRbid-0.02, "SELL")  #     ASTRLevel = ASTRLevel + 1



        else:
            # print(current_time)
            #counter = counter + 1
            if counter % 100 == 0:
                print(wb.refresh_login())

        ###  Misc Logic

        time.sleep(1)
        counter = counter + 1
        if counter > 400:
            print(wb.refresh_login())  # Login Refresh
            wb.get_trade_token(cfg.TRADE_TOKEN)
            counter = 0  # RESET COUNTER




        ###  Crypto Logic

        numOfDOGE = getPositions(DOGE_SYMBOL)
        DOGEbid = getCryptoBid(DOGE_SYMBOL)  ### DOGE
        DOGEask = getCryptoAsk(DOGE_SYMBOL)

        sell_doge = getPriceWeight(DOGE_SELL, DOGEbid)  ### DOGE
        buy_doge = getPriceWeight(DOGE_BUY, DOGEask)

        if counter % UPDATE_INTERVAL == 1:
            print("Buy Percentage: " + str(buy_doge*100) + " Sell Percentage: " + str(sell_doge*100))
            print("DOGE Bid: " + str(DOGEbid) + " Ask: " + str(DOGEask))
            print("DOGE Position: " + str(numOfDOGE))
            print("Buy at: " + str(DOGE_BUY) + " Sell At: " + str(DOGE_SELL))

        if counter % 20 == 0:
            wb.refresh_login()
            time.sleep(1)

        num = 1.1 / DOGEbid  # Calculate number of shares to equal 1.1 dollars


        if sell_doge < 0.0085:
            if numOfDOGE * DOGEbid < 1:
                continue
            placeCryptoOrder(DOGE_SYMBOL, int(num), DOGEbid, "SELL")
            time.sleep(20000 * sell_doge)
            continue

        if buy_doge < 0.0085:
            placeCryptoOrder(DOGE_SYMBOL, int(num), DOGEask, "BUY")
            time.sleep(80000 * buy_doge)
            continue





    # except:
    #     while True:
    #         try:
    #             print("Broken: Continuing")
    #             wb.logout()
    #             time.sleep(10)
    #             print(wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER))
    #             # 6 digits MFA, Security Question ID, Question Answer.
    #             time.sleep(1)
    #             break
    #         except:
    #             continue
    #     continue
