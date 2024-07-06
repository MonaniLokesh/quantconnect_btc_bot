from AlgorithmImports import *
from alpha import PriceActionAlpha

# BTCUSD Long Only Dual Thrust Algorithm 
# Originated by Michael Vitucci
class DualThrustAlgorithm(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2017, 1, 1)
        self.set_end_date(2024, 1, 1)
        self.set_cash(100000)
        self.set_brokerage_model(BrokerageName.GDAX, AccountType.CASH)

        symbol = self.add_crypto("BTCUSD", Resolution.MINUTE).symbol

        self.add_alpha(PriceActionAlpha(self, symbol))
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel(lambda time: None))
        self.set_execution(ImmediateExecutionModel())
