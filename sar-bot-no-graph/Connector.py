import sys
import time
import websocket
import json
import CandleMgr
import threading
import VirtualTrading
import Strategy

print(str(sys.argv))

conf = open("bot.conf", "r")

confs = conf.readline(1000).split(" ")
if confs[0].startswith("#"):
    confs=conf.readline(1000).split(" ")
print(str(confs))
PRODUCT = confs[0]
VirtualTrading.initialFund = float(confs[1])
VirtualTrading.processRate = float(confs[2])
conf.close()

VirtualTrading.takeProfit=float(confs[3])

VirtualTrading.init(initialFund=VirtualTrading.initialFund)

VirtualTrading.PRODUCT = PRODUCT
PUBLIC_URL = "wss://ws.okex.com:8443/ws/v5/public"

ws = 0


def connect():
    global ws
    ws = websocket.WebSocket()
    while 1:
        try:
            print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) + " connecting...")
            ws.connect(PUBLIC_URL, http_proxy_host="localhost", http_proxy_port=10809)
            break
        except BaseException:
            print("retry...")
            continue
    subscribeDict = {
        "op": "subscribe",
        "args": [{
            "channel": "candle1m",
            "instId": PRODUCT
        }]
    }

    ws.send(json.dumps(subscribeDict))

    print(ws.recv())


connect()


def closeCandle():
    # print("Close Candle:o:%.5f" % CandleMgr.currentCandle.open + " c:%.5f" % CandleMgr.currentCandle.close +
    #       "\n\th:%.5f" % CandleMgr.currentCandle.high + " l:%.5f" % CandleMgr.currentCandle.low)
    CandleMgr.candles.append(CandleMgr.currentCandle)
    CandleMgr.previousCandle = CandleMgr.currentCandle
    CandleMgr.currentCandle = CandleMgr.Candle()
    # VirtualTrading.lsTradingPrice = -1.0


currentCandleStart = 0

isPreviousSaRPointHigh = True


def loopRecv():
    global currentCandleStart, isPreviousSaRPointHigh, ws
    while True:
        dataJSON = ""
        try:
            dataJSON = ws.recv()
        except BaseException:
            connect()
            continue

        tStartProcess=time.time()


        # print(dataJSON)
        receive = json.loads(dataJSON)
        # check if this is a new candle
        if not receive["data"][0][0] == currentCandleStart:
            if not currentCandleStart == 0:
                closeCandle()
            currentCandleStart = receive["data"][0][0]
        CandleMgr.currentCandle.update(float(receive["data"][0][4]))
        if CandleMgr.currentCandle.open == 0:
            CandleMgr.currentCandle.open = float(receive["data"][0][1])

        if len(CandleMgr.candles) == 0:
            CandleMgr.currentCandle.calcSaR0()
        else:
            CandleMgr.currentCandle.calcSaR(CandleMgr.previousCandle)
            # CandleMgr.currentCandle.calcSaR(CandleMgr.combinePrevious(2))

            # take profit
            if CandleMgr.currentCandle.close/VirtualTrading.lsTradingPrice>=(1.0+VirtualTrading.takeProfit) and VirtualTrading.sellable():
                VirtualTrading.__doSell()
                continue
            # check if the position of sar changed
            if (not CandleMgr.currentCandle.isSaRHigher() == isPreviousSaRPointHigh) and len(CandleMgr.candles) > 1:
                if CandleMgr.currentCandle.isSaRHigher():
                    if VirtualTrading.sellAll():
                        isPreviousSaRPointHigh = CandleMgr.currentCandle.isSaRHigher()

                    # KGraph.updateStatus()
                else:
                    if VirtualTrading.buyAll():
                        isPreviousSaRPointHigh = CandleMgr.currentCandle.isSaRHigher()
                    # KGraph.updateStatus()
        # KGraph.updateCurrent()

        tEndProcess=time.time()
        if tEndProcess-tStartProcess>500:
            print(time.strftime("%m-%d,%H:%M:%S", time.localtime()) + " Process data spent too much time:%d ms"%(tEndProcess-tStartProcess))


REPAINT_INTERVAL = 0.5


def repaintTimer():
    count = 0
    while True:
        time.sleep(REPAINT_INTERVAL)
        count = count + 1
        if count == 10:
            count = 0


threading.Thread(target=repaintTimer).start()

print("Thread starting.")

t0 = threading.Thread(target=loopRecv)
print("Thread started.")
t0.daemon = True
t0.start()
t0.join()
