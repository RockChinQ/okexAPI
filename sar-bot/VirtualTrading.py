import time

import CandleMgr

fund = 1000.0
product = 0.0
processRate = 0.0006

burntFund = 0.0
burntProduct = 0.0

lsTradingPrice = -1.0

nonSellRange = 0.0035  # 0.35%
nonBuyRange = 0.005  # 0.5%

PRODUCT = ""


def sellAll():
    global fund, product, burntFund, lsTradingPrice
    if product == 0:
        # print("no product to sell")
        return False
    # price range
    priceRange = abs(CandleMgr.currentCandle.close - CandleMgr.currentCandle.open)
    priceOpen = CandleMgr.currentCandle.open
    if not CandleMgr.previousCandle.isUp() and not CandleMgr.currentCandle.isUp():
        priceRange = abs(CandleMgr.currentCandle.close - CandleMgr.previousCandle.open)
        priceOpen = CandleMgr.previousCandle.open

    if abs(CandleMgr.currentCandle.close - lsTradingPrice) / CandleMgr.currentCandle.open > nonSellRange and \
            priceRange / priceOpen > nonSellRange:
        print(time.strftime("%m-%d,%H:%M:%S",
                            time.localtime()) + " SELL ALL @ %.5f" % CandleMgr.currentCandle.close + " fee(f):%.4f" % (
                      float(product) * float(CandleMgr.currentCandle.close) * processRate) + " profit:%.3f" % (
                      fund + float(product) * CandleMgr.currentCandle.close - 1000))
        fund = float(product) * float(CandleMgr.currentCandle.close) * (1.0 - processRate)
        burntFund = burntFund + float(product) * float(CandleMgr.currentCandle.close) * processRate
        f = open("dumps-" + PRODUCT + ".txt", "a")
        f.write(time.strftime("%m-%d,%H:%M:%S",
                              time.localtime()) + " SELL ALL @ %.5f" % CandleMgr.currentCandle.close + " fee(f):%.4f" % (
                        float(product) * float(CandleMgr.currentCandle.close) * processRate) + " profit:%.3f" % (
                        fund + float(product) * CandleMgr.currentCandle.close - 1000) + "\n")
        f.close()
        product = 0.0
        lsTradingPrice = CandleMgr.currentCandle.close
        return True
    # else:
    # print("SELL PRICE NOT IN RANGE")
    return False


def buyAll():
    global fund, product, burntProduct, lsTradingPrice
    if fund == 0:
        # print("not fund to afford")
        return False

    priceRange = abs(CandleMgr.currentCandle.close - CandleMgr.currentCandle.open)
    priceOpen = CandleMgr.currentCandle.open
    if CandleMgr.previousCandle.isUp() and CandleMgr.currentCandle.isUp():
        priceRange = abs(CandleMgr.currentCandle.close - CandleMgr.previousCandle.open)
        priceOpen = CandleMgr.previousCandle.open
    if abs(CandleMgr.currentCandle.close - lsTradingPrice) / CandleMgr.currentCandle.open > nonBuyRange and \
            priceRange / priceOpen > nonBuyRange:
        print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) +
              " BUY ALL @ %.5f" % CandleMgr.currentCandle.close + " fee(p):%.4f" % (
                      float(fund) / float(CandleMgr.currentCandle.close) * processRate))
        product = float(fund) / float(CandleMgr.currentCandle.close) * (1.0 - processRate)
        burntProduct = burntProduct + float(fund) / float(CandleMgr.currentCandle.close) * processRate
        f = open("dumps-" + PRODUCT + ".txt", "a")
        f.write(time.strftime("%m-%d,%H:%M:%S",
                              time.localtime()) + " BUY ALL @ %.5f" % CandleMgr.currentCandle.close + " fee(p):%.4f" % (
                        float(fund) / float(CandleMgr.currentCandle.close) * processRate) + "\n")
        f.close()
        fund = 0.0
        lsTradingPrice = CandleMgr.currentCandle.close

        return True
    # else:
    # print("BUY PRICE NOT IN RANGE.")
    return False

def affordable():
    return fund>0
def sellable():
    return product>0

def burnt():
    return burntFund + float(burntProduct) * CandleMgr.currentCandle.close


def profit():
    return fund + float(product) * CandleMgr.currentCandle.close - 1000.0 - burnt()
