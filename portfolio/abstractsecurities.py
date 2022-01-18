
from abc import ABC, abstractmethod


class AbstractEquity(ABC):
    _name = ''
    _init_price = None

    @property
    def name(self):
        return self._name
    @property
    def init_price(self):
        return self._init_price

    @abstractmethod
    def payoff(self, price):
        pass




class AbstractDerivative(ABC):
    _underlying_name = ''
    _underlying_init_price = None

    @property
    def underlying_name(self):
        return self._underlying_name
        
    @property
    def underlying_init_price(self):
        return self._underlying_init_price

    @abstractmethod
    def payoff(self, underlying_price):
        pass

    









