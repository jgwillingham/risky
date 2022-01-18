from .abstractsecurities import AbstractEquity


class Stock(AbstractEquity):
    def __init__(self, name, num_shares, init_price):
        self._name = name
        self.num_shares = num_shares # negative for short positions
        self._init_price = init_price

    def payoff(self, price):
        return self.num_shares*(price - self._init_price)