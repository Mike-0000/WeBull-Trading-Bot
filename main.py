from webull import webull # for paper trading, import 'paper_webull'
from datetime import datetime
import time
import config.userconfig as cfg

wb = webull()
# print(wb.get_mfa(cfg.wb_email))
# print(wb.get_security(cfg.wb_email))
BUY_PRICE = 4.35
SELL_PRICE = 4.7
UPDATE_INTERVAL = 30



data = wb.login(cfg.wb_email, cfg.webull_pass, cfg.HOSTNAME, cfg.AUTH_CODE, '1001', cfg.ANSWER) # 6 digits MFA, Security Question ID, Question Answer.
wb.get_trade_token(cfg.TRADE_TOKEN)

print(data)

counter = 0
level = 1
while 0 < 1:
    try:

        now = datetime.now()
        current_time = now.hour
        if current_time >= 4 and current_time < 21:     #    Is Market Open??
            positions1 = wb.get_positions()
            positions2 = positions1[0] # ASTR in 0th position
            ASTR = wb.get_analysis("ASTR")

            price = ASTR['targetPrice']['current']  #  Get price from analysis
            position = positions2['position']
            quote = wb.get_quote("ASTR")
            askbidlist = quote['depth']
            asks = askbidlist['ntvAggAskList']
            bids = askbidlist['ntvAggBidList']

            min1 = 9999
            for price in asks:
                if float(price["price"]) < min1: # FIND MIN CURRENT ASK
                    min1 = float(price["price"])
                    ask = float(min1)

            max1 = 0
            for price in bids:
                if float(price["price"]) > max1: # FIND MAX CURRENT BID
                    max1 = float(price["price"])
                bid = float(max1)


            if counter % UPDATE_INTERVAL == 1:
                print("Bid: " + str(bid) + " Ask: " + str(ask))

            if level == 2:
                print("triggered")
                time.sleep(100)

            if ask <= BUY_PRICE and level == 2:     # BUYING
                print("Bought: " + ask)
                wb.place_order(stock='ASTR', price=ask, action='BUY', orderType='LMT', enforce='GTC', quant=position+10)
                level = level - 1

            if bid >= SELL_PRICE and level == 1:    # SELLING
                print("SOLD: " + bid)
                wb.place_order(stock='ASTR', price=bid, action='SELL', orderType='LMT', enforce='GTC', quant=position/2)
                level = level + 1

        else:
            #print(current_time)
            time.sleep(60)
        time.sleep(1)
        counter = counter + 1
        if counter > 400:
            print(wb.refresh_login()) # Login Refresh
            wb.get_trade_token(cfg.TRADE_TOKEN)
            counter = 0 # RESET COUNTER

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
