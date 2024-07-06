from AlgorithmImports import *

class PriceActionAlpha(AlphaModel):
    def __init__(self, algorithm, symbol):
        self.algorithm = algorithm
        self.btc = symbol

        self.hour = -1
        self.selltrig = None
        self.buytrig = None
        self.currentopen = None

        self.consolidator = TradeBarConsolidator(timedelta(1))
        self.consolidator.data_consolidated += self.on_consolidated
        self.window = RollingWindow[TradeBar](4)

        history = algorithm.history[TradeBar](self.btc, 4*24*60, Resolution.MINUTE)
        for bar in history:
            self.consolidator.update(bar)

        algorithm.subscription_manager.add_consolidator(self.btc, self.consolidator)

    def on_consolidated(self, sender, bar):
        self.window.add(bar)
        self.currentopen = bar.open

        if not self.window.is_ready: return

        df = self.algorithm.pandas_converter.get_data_frame[TradeBar](self.window)    
        k1 = 0.5
        k2 = 0.5
        
        HH, HC, LC, LL = max(df['high']), max(df['close']), min(df['close']), min(df['low'])
        if (HH - LC) >= (HC - LL):
            signalrange = HH - LC
        else:
            signalrange = HC - LL
        
        self.selltrig = self.currentopen - k2 * signalrange
        self.buytrig = self.currentopen + k1 * signalrange    
    
    def update(self, algorithm, data):        
        # We only use hourly signals
        if not data.contains_key(self.btc) or not self.window.is_ready:
            return []

        if self.hour == algorithm.time.hour:
            return []
        self.hour = algorithm.time.hour
        
        price = data[self.btc].price
        
        if algorithm.live_mode:
            algorithm.log(f'Buy Trigger {self.buytrig} > Price {price} > {self.selltrig}')
        
        if price >= self.buytrig:
            return [Insight(self.btc, timedelta(days=365), InsightType.PRICE, InsightDirection.UP)]
        elif price < self.selltrig:
            algorithm.insights.cancel([self.btc])
        
        return []
