# QuantConnect (LEAN) version of the forward-test rule. Paste into a new Python algorithm on quantconnect.com,
# backtest, then deploy to paper trading. Replace the rule with your own model to match trackers/t17_forward_test.py.
from AlgorithmImports import *
class MarketsLabForwardTest(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2018, 1, 1); self.set_cash(100000)
        self.sym = self.add_equity("SPY", Resolution.DAILY).symbol      # ASX data is limited on QC; SPY used as the liquid proxy
        self.fast = self.sma(self.sym, 20, Resolution.DAILY); self.slow = self.sma(self.sym, 50, Resolution.DAILY)
        self.set_warm_up(60); self.set_benchmark(self.sym)
    def on_data(self, data):
        if self.is_warming_up or not self.slow.is_ready: return
        long = self.fast.current.value > self.slow.current.value
        if long and not self.portfolio.invested: self.set_holdings(self.sym, 1.0)
        elif not long and self.portfolio.invested: self.liquidate(self.sym)
