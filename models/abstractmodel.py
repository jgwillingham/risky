
from abc import ABC, abstractmethod


class AbstractModel(ABC):
    """
    An abstract class for all model-specific classes to inherit from
    """
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def iscalibrated(self):
        pass

    @abstractmethod
    def add_historical(self, dataset):
        pass

    @abstractmethod
    def calibrate(self):
        pass

    @abstractmethod
    def jump_simulate(self, num_steps, num_iter):
        pass
    
    @abstractmethod
    def path_simulate(self, num_steps, num_iter):
        pass




    

