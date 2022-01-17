
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class AbstractModel(ABC):
    """
    An abstract class for all model-specific classes to inherit from
    """
    # all child classes will have the same read-only attributes:
    _iscalibrated = False
    _historical_data = pd.DataFrame([])
    _securities = []
    _num_securities = 0

    @property
    def iscalibrated(self):
        return self._iscalibrated
    @property
    def historical_data(self):
        return self._historical_data
    @property
    def securities(self):
        return self._securities
    @property
    def num_securities(self):
        return self._num_securities

    @property
    @abstractmethod
    def name(self):
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


    def add_historical(self, dataset):
        """
        Add historical data for model calibration
        """
        if not isinstance(dataset, pd.DataFrame):
            dataset = pd.DataFrame(dataset)
        self._historical_data = dataset
        self._securities = dataset.columns.to_list()
        self._num_securities = len(self._securities)
        self._add_calculated_columns(self._historical_data)
        if self._iscalibrated:
            self._iscalibrated = False


    def _add_calculated_columns(self, df):
        """
        adds additional columns such as diff and log returns
        """
        for sec in self._securities:
            data = df[sec]
            df[f'{sec}-diff'] = data.diff()
            df[f'{sec}-logret'] = [np.nan]+[np.log(data[i]/data[i-1]) \
                                        for i in range(1,len(data))]




    

