import time
import tkinter
import CandleMgr
import VirtualTrading

currentX = 0
rowWidth = 20
rowCount = 32
dx = 120
coin = ""

RISE_RATE_RANGE = 0.05

components = []

enable = True


def init(title):
    if not enable:
        return
    global coin, canvas
    coin = title
    top = tkinter.Tk()
    top.title(title)
    top.geometry('800x600+200+500')

    global canvas
    canvas = tkinter.Canvas(top, width=800, height=600, bg='black')
    canvas.create_line(0, 250, 800, 250, fill="white")
    canvas.create_line(0, 501, 800, 501, fill="white")
    canvas.pack()
    updateStatus()

    top.mainloop()


def updateCurrent():
    if not enable:
        return
    tempCurrentX = currentX

    # print("Drawingggggggggggggggggggggggggggggggggggg")

    canvas.create_rectangle(0, 20, dx - 2, 125, fill="black", outline="white")
    # draw price
    canvas.create_text(50, 10, text="" + coin, font=("Serif", 14), fill="white")
    canvas.create_text(60, 30, text="%.7f" % CandleMgr.currentCandle.close, font=("Serif", 10), fill="white")
    ratecl = "red"
    if (CandleMgr.currentCandle.close - CandleMgr.currentCandle.open) >= 0:
        ratecl = "green"
    canvas.create_text(60, 45, text="%.3f%%" % (
            (CandleMgr.currentCandle.close - CandleMgr.currentCandle.open) / CandleMgr.currentCandle.open * 100),
                       font=("Serif", 10), fill=ratecl)

    # profit
    profit = VirtualTrading.fund + float(VirtualTrading.product) * CandleMgr.currentCandle.close - 1000
    canvas.create_text(50, 70, text="profit(u):", fill="white")
    fillcl = "red"
    if profit >= 0:
        fillcl = "green"
    canvas.create_text(55, 90, text="%.3f" % profit, fill=fillcl, font=("Serif", 18))

    canvas.create_text(60, 115, text="(%.5f %%)" % (profit / 1000 * 100), font=("Serif", 13), fill=fillcl)

    # candle
    canvas.create_rectangle((currentX % rowCount) * rowWidth + dx, 0, (currentX % rowCount) * rowWidth + rowWidth + dx,
                            500,
                            fill="black")
    canvas.create_text((tempCurrentX % rowCount) * rowWidth + 5 + dx, 10, text="%d" % (tempCurrentX / rowCount),
                       fill="white")
    canvas.create_text((tempCurrentX % rowCount) * rowWidth + dx + 5, 25, text=CandleMgr.currentCandle.isSaRHigher()
                       , fill="white")
    cl = "red"
    if CandleMgr.currentCandle.isUp():
        cl = "green"
    highY = priceToY(CandleMgr.currentCandle.high)
    lowY = priceToY(CandleMgr.currentCandle.low)
    openY = priceToY(CandleMgr.currentCandle.open)
    closeY = priceToY(CandleMgr.currentCandle.close)
    sarY = priceToY(CandleMgr.currentCandle.sar)

    canvas.create_rectangle((tempCurrentX % rowCount) * rowWidth + rowWidth / 2 + dx, highY
                            , (tempCurrentX % rowCount) * rowWidth + rowWidth / 2 + 2 + dx, lowY, fill=cl,
                            outline="white")
    canvas.create_rectangle((tempCurrentX % rowCount) * rowWidth + dx, min(openY, closeY),
                            (tempCurrentX % rowCount) * rowWidth + rowWidth + dx, max(openY, closeY),
                            fill=cl, outline="white")
    # range line

    if VirtualTrading.affordable():
        highRY = priceToY(CandleMgr.currentCandle.open * (1 + VirtualTrading.nonBuyRange))
        if CandleMgr.previousCandle.isUp():
            highRY = priceToY(CandleMgr.previousCandle.open * (1 + VirtualTrading.nonSellRange))
        canvas.create_rectangle((tempCurrentX % rowCount) * rowWidth + dx + 3, highRY,
                                (tempCurrentX % rowCount) * rowWidth + dx + rowWidth - 3, highRY + 1, fill="orange",
                                outline="orange")
    if VirtualTrading.sellable():
        lowRY = priceToY(CandleMgr.currentCandle.open * (1 - VirtualTrading.nonSellRange))
        if not CandleMgr.previousCandle.isUp():
            lowRY = priceToY(CandleMgr.previousCandle.open * (1 - VirtualTrading.nonSellRange))
        canvas.create_rectangle((tempCurrentX % rowCount) * rowWidth + dx + 3, lowRY,
                                (tempCurrentX % rowCount) * rowWidth + dx + rowWidth - 3, lowRY + 1, fill="orange",
                                outline="orange")

    # draw sar
    c = canvas.create_rectangle((tempCurrentX % rowCount) * rowWidth + rowWidth / 2 - 4 + dx, sarY,
                                (tempCurrentX % rowCount) * rowWidth + rowWidth / 2 + 4 + dx, sarY + 4, fill="yellow")

    canvas.pack()


def updateStatus():
    if not enable:
        return
    canvas.create_rectangle(0, 0, dx - 2, 600, fill="black", outline="white")
    # processing fee
    canvas.create_text(50, 135, text="taking fee(u):", fill="white")

    canvas.create_text(55, 155, text="%.3f" % VirtualTrading.burnt(), fill="red", font=("Serif", 14))

    canvas.create_text(60, 170, text="(%.5f %%)" % (VirtualTrading.burnt() / 1000 * 100), font=("Serif", 13),
                       fill="red")

    # asset
    canvas.create_text(50, 195, text="assets", fill="white")
    canvas.create_text(50, 210, text="product", fill="white")
    canvas.create_text(60, 230, text="%.4f" % VirtualTrading.product, font=("Serif", 12), fill="white")

    canvas.create_text(50, 250, text="fund", fill="white")
    canvas.create_text(60, 270, text="%.4f" % VirtualTrading.fund, font=("Serif", 12), fill="white")

    # time
    canvas.create_text(55, 340, text=time.strftime("%H:%M:%S", time.localtime()), fill="white", font=("Serif", 14))


def priceToY(price):
    kopen = CandleMgr.currentCandle.open
    if len(CandleMgr.candles) > 0:
        kopen = CandleMgr.candles[0].open
    if price > kopen:
        return 250 - (price - kopen) / (kopen * RISE_RATE_RANGE) * 250
    else:
        return 250 + (kopen - price) / (kopen * RISE_RATE_RANGE) * 250


def resetCanvas():
    if not enable:
        return
    # print("reset")
    canvas.delete("all")
    canvas.pack()
    # 绘制已存在的K线candle
    index = 0
    pageNow = int(currentX / rowCount)
    canvas.create_line(0, 250, 600, 250, fill="white")
    canvas.create_line(0, 501, 800, 501, fill="white")
    for candle in CandleMgr.candles:
        if not int(index / rowCount) == pageNow:
            index = index + 1
            continue
        else:
            # candle
            canvas.create_text((index % rowCount) * rowWidth + 5 + dx, 10, text="%d" % (index / rowCount),
                               fill="white")
            canvas.create_text((index % rowCount) * rowWidth + dx + 5, 25,
                               text=candle.isSaRHigher(), fill="white")
            cl = "red"
            if candle.isUp():
                cl = "green"
            highY = priceToY(candle.high)
            lowY = priceToY(candle.low)
            openY = priceToY(candle.open)
            closeY = priceToY(candle.close)
            sarY = priceToY(candle.sar)

            canvas.create_rectangle((index % rowCount) * rowWidth + rowWidth / 2 + dx, highY
                                    , (index % rowCount) * rowWidth + rowWidth / 2 + 2 + dx, lowY, fill=cl, outline=cl)
            canvas.create_rectangle((index % rowCount) * rowWidth + dx, min(openY, closeY),
                                    (index % rowCount) * rowWidth + rowWidth + dx, max(openY, closeY),
                                    fill=cl, outline=cl)

            c = canvas.create_rectangle((index % rowCount) * rowWidth + rowWidth / 2 - 4 + dx, sarY,
                                        (index % rowCount) * rowWidth + rowWidth / 2 + 4 + dx, sarY + 4,
                                        fill="yellow")
        index = index + 1
    canvas.pack()
