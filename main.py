from webull import webull  # for paper trading, import 'paper_webull'
from datetime import datetime
import time
import config.userconfig as cfg
import functions
wb = webull()
# print(wb.get_mfa(cfg.wb_email))
# print(wb.get_security(cfg.wb_email))

DOGE_BUY = 0.105
DOGE_SELL = 0.138

ASTR_BUY = 4.04
ASTR_SELLS = [4.48, 4.66]

SELL_INTERVAL = 12
UPDATE_INTERVAL = 240

DOGE_SYMBOL = 'DOGEUSD'
ASTR_symbol = 'ASTR'

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
    return percentage*1000

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

def getSettledCash():
    cash = wb.get_account()['accountMembers'][2]['value']
    return float(cash)

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

while True:
    try:
        now = datetime.now()
        current_time = now.hour
        #  US Stock Market
        if current_time >= 7 and current_time <= 19:  # Is Market Open??
            numOfASTR = getPositions(ASTR_symbol)
            if numOfASTR == None:
                ASTRLevel = 1
            ### Collect position information
            elif numOfASTR > 100 and ASTRLevel != 0:
                ASTRLevel = 0
            elif numOfASTR <= 100 and ASTRLevel != 1:
                ASTRLevel = 1
            # if numOfASTR >= 120 and ASTRLevel != 0:
            #     ASTRLevel = 0
            #     print("Setting level to 0")
            # if numOfASTR < 120 and ASTRLevel != 1:
            #     ASTRLevel = 1
            #     print("Setting level to 1")

            # Get current price from analysis

            # Get current bid and ask

            ASTRask = getAsk(ASTR_symbol)  ### ASTR
            ASTRbid = getBid(ASTR_symbol)

            ###   ASTR LOGIC
            ### Checking If Order Filled Logic
            # if ASTRLevel == 1 and numOfASTR > 150:  ### Check if Order is filled
            #     time.sleep(60)  ### If not, allow time for order to be filled
            #     if numOfASTR > 150:  ### If Order still not filled, cancel order and reset level.
            #         print(wb.cancel_all_orders())
            #         ASTRLevel = 0
            #         continue
            sell_astr = getPriceWeight(ASTR_SELLS[ASTRLevel], ASTRbid)  ### ASTR
            buy_astr = getPriceWeight(ASTR_BUY, ASTRask)
            if counter % UPDATE_INTERVAL == 0:
                print("ASTR Buy Percentage: " + str(buy_astr / 10) + " Sell Percentage: " + str(sell_astr / 10))
                print("ASTR Bid: " + str(ASTRbid) + " Ask: " + str(ASTRask))
                print("Level: " + str(ASTRLevel) + " Position: " + str(numOfASTR))
                print("Buy at: " + str(ASTR_BUY) + " Sell At: " + str(ASTR_SELLS[ASTRLevel]))

            if sell_astr < 5:
                sell_astr = sell_astr*sell_astr
                placeOrder(ASTR_symbol, 4, ASTRbid, "SELL")
                time.sleep(sell_astr*SELL_INTERVAL)
            elif ASTRbid > ASTR_SELLS[ASTRLevel]: ### Check if Bid exceeds Sell Price
                placeOrder(ASTR_symbol, 4, ASTRbid, "SELL")
                time.sleep(sell_astr * 16)

            if getSettledCash() > ASTRask:
                if buy_astr < 8:
                    buy_astr = buy_astr*buy_astr
                    placeOrder(ASTR_symbol, 1, ASTRask, "BUY")
                    time.sleep(buy_astr*2)
                elif ASTRask < ASTR_BUY:
                    placeOrder(ASTR_symbol, 1, ASTRask, "BUY")
                    time.sleep(buy_astr * 4)

        ###  Misc Logic

        time.sleep(1)
        counter = counter + 1
        if counter % 400 == 0:
            wb.refresh_login()  # Login Refresh
            wb.get_trade_token(cfg.TRADE_TOKEN)
        #    counter = 0  # RESET COUNTER


        ###  Crypto Logic - DOGE

        # numOfDOGE = getPositions(DOGE_SYMBOL)
        # DOGEbid = getCryptoBid(DOGE_SYMBOL)  ### DOGE
        # DOGEask = getCryptoAsk(DOGE_SYMBOL)
        #
        #
        # sell_doge = getPriceWeight(DOGE_SELL, DOGEbid)  ### DOGE
        # buy_doge = getPriceWeight(DOGE_BUY, DOGEask)
        #
        # if counter % UPDATE_INTERVAL * 12000 == 12000:
        #     print("DOGE Buy Percentage: " + str(buy_doge/10) + " Sell Percentage: " + str(sell_doge/10))
        #     print("DOGE Bid: " + str(DOGEbid) + " Ask: " + str(DOGEask))
        #     print("DOGE Position: " + str(numOfDOGE))
        #     print("DOGE Buy at: " + str(DOGE_BUY) + " Sell At: " + str(DOGE_SELL))
        #
        # # if counter % 20 == 0:
        # #     wb.refresh_login()
        # #     time.sleep(1)
        #
        # num = 1.1 / DOGEbid  # Calculate number of shares to equal 1.1 dollars
        #
        #
        # if sell_doge < 4.5:
        #     sell_doge = sell_doge*sell_doge
        #     if numOfDOGE * DOGEbid < 1:
        #         continue
        #     placeCryptoOrder(DOGE_SYMBOL, int(num), DOGEbid, "SELL")
        #     time.sleep(8 * sell_doge)
        #     continue
        #
        # if buy_doge < 3:
        #     buy_doge = buy_doge*buy_doge
        #     placeCryptoOrder(DOGE_SYMBOL, int(num), DOGEask, "BUY")
        #     time.sleep(18 * buy_doge)
        #     continue

    except:
        while True:
            try:
                print("Broken: Continuing")
                wb.logout()
                time.sleep(2)
                wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER)
                # 6 digits MFA, Security Question ID, Question Answer.
                time.sleep(1)
                counter = 0
                break
            except:
                continue
        continue
