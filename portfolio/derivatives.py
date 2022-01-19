from abc import ABC, abstractmethod
from .stock import Stock


class StockOption(ABC):
    """
    Abstract class for stock options (puts, calls)
    """
    _underlying = None
    _strike = None
    _premium = None
    @property
    def underlying(self):
        if not isinstance(self._underlying, Stock):
            raise Exception('Underlying must be instance of Stock class')
        return self._underlying
    @property
    def strike(self):
        return self._strike
    @property
    def premium(self):
        return self._premium

    @abstractmethod
    def payoff(self, underlying_price):
        pass



class Call(StockOption):
    def __init__(self, underlying, strike, premium):
        if isinstance(underlying, str):
            underlying = Stock(underlying, 100)
        self._underlying = underlying
        self._strike = strike
        self._premium = premium

    def payoff(self, underlying_price):
        V = underlying_price
        K = self._strike
        P = self._premium
        n = self._underlying._num_shares
        return n*(max(V-K,0)-P)     


class Put(StockOption):
    def __init__(self, underlying, strike, premium):
        self._underlying = underlying
        self._strike = strike
        self._premium = premium

    def payoff(self, underlying_price):
        V = underlying_price
        K = self._strike
        P = self._premium
        n = self._underlying._num_shares
        return n*(max(K-V,0)-P)
