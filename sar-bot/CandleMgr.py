candles = []


class Candle:
    open = 0
    close = 0
    high = 0
    low = 1000000000

    sar = 0
    af = 0

    def isSaRHigher(self):
        return self.sar > ((self.open + self.close) / 2)

    def update(self, price):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price

    def isUp(self):
        return self.close > self.open

    # Calc the first SaR
    def calcSaR0(self):
        sar0 = 0
        ep = 0
        if self.close > self.open:  # 上涨
            sar0 = self.low
            ep = self.low
        else:
            sar0 = self.high
            ep = self.high
        self.af = 0.02
        self.sar = sar0 + self.af * (ep - sar0)
        return self.sar

    # sar1=sar0+af1*(ep0-sar0)
    def calcSaR(self, previous_candle):
        sar0 = previous_candle.sar
        ep = 0
        if self.isUp():
            ep = previous_candle.high
        else:
            ep = previous_candle.low
        # calc af
        if self.isUp() and previous_candle.isUp():
            if self.high > previous_candle.high:
                self.af = previous_candle.af + 0.02
            elif self.high <= previous_candle.high:
                self.af = previous_candle.af
        elif (not self.isUp()) and (not previous_candle.isUp()):
            if self.low < previous_candle.low:
                self.af = previous_candle.af + 0.02
            elif self.low >= previous_candle.low:
                self.af = previous_candle.af
        else:  # 行情逆转,af=0.02
            self.af = 0.02
        if self.af > 0.2:
            self.af = 0.02
        # 计算sar
        tempSaR = previous_candle.sar + self.af * (ep - previous_candle.sar)

        # 确定最终SaR
        if self.isUp():
            if tempSaR > self.low or tempSaR > previous_candle.low:
                self.sar = min(previous_candle.low, self.low)
            elif tempSaR <= self.low and tempSaR <= previous_candle.low:
                self.sar = tempSaR
        else:
            if tempSaR < self.high or tempSaR < previous_candle.high:
                self.sar = max(previous_candle.high, self.high)
            elif tempSaR >= self.high and tempSaR >= previous_candle.high:
                self.sar = tempSaR
        return self.sar


currentCandle = Candle()
previousCandle = Candle()
ppCandle = Candle()


def combinePrevious(amount):
    combination = Candle()
    combination.high = previousCandle.high
    combination.low = previousCandle.low
    combination.close = previousCandle.close
    combination.open = previousCandle.open
    combination.af = previousCandle.af
    combination.sar = previousCandle.sar

    index = len(candles) - amount
    combination.open = candles[max(0,index)].open
    for i in range(index, len(candles)):
        if i<0:
            continue
        combination.high = max(combination.high, candles[i].high)
        combination.low = min(combination.low, candles[i].low)
    return combination