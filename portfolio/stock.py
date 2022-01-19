
class Stock:
    def __init__(self, name, num_shares, init_price=None):
        self._name = name
        self._num_shares = num_shares # negative for short positions
        self._init_price = init_price
    
    @property
    def name(self):
        return self._name
    @property
    def num_shares(self):
        return self._num_shares
    @property
    def init_price(self):
        return self._init_price

    def payoff(self, price):
        return self._num_shares*(price - self._init_price)