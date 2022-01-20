
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import scipy
from statsmodels.distributions.empirical_distribution import ECDF
import os

# this suppresses an annoying warning when saving simulations to h5 file
import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

class AbstractModel(ABC):
    """
    An abstract class for all model-specific classes to inherit from
    """
    # all child classes will have the same read-only attributes:
    _iscalibrated = False
    _historical_data = pd.DataFrame([])
    _logret_columns = []
    _securities = []
    _num_securities = 0

    @property
    def iscalibrated(self):
        return self._iscalibrated
    @property
    def historical_data(self):
        return self._historical_data
    @property
    def logret_columns(self):
        return self._logret_columns
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
    def simulate_jump(self, num_steps):
        # must output simulation results in a pandas dataframe
        pass
    
    @abstractmethod
    def simulate_path(self, num_steps):
        # must output simulation results in a pandas dataframe
        pass



    
    def run_simulation(self, num_steps, num_iter, path=None):
        if path == None:
            path = os.getcwd()
        filepath = lambda n: os.path.join(path, \
                        'simulation-'+self.name+'-'+format(n,'03d')+'.h5')

        n = 0
        while os.path.isfile(filepath(n)):
            n += 1
        filepath = filepath(n)

        h5file = pd.HDFStore(filepath)
        h5file['historical'] = self._historical_data[self._securities]

        for ii in range(num_iter):
            sim_df = self.simulate_path(num_steps)
            h5file[f'simulations/sim-{ii}'] = sim_df
                        
        h5file.close()
        print(f'Simulation finished.\nSaved in {filepath}\n')

    

    def add_historical(self, dataset):
        """
        Add historical data for model calibration
        """
        if not isinstance(dataset, pd.DataFrame):
            dataset = pd.DataFrame(dataset)
        else:
            dataset = dataset.copy()
        self._historical_data = dataset
        self._securities = dataset.columns.to_list()
        self._num_securities = len(self._securities)
        self._add_calculated_columns(self._historical_data)
        self._logret_columns = [f'{sec}-logret' for sec in self._securities]

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


    def _get_empirical_marginals(self):
        """
        Builds the empirical marginal CDF (and its inverse) for 
        each asset based on the provided historical data
        """
        ecdf, ecdf_inv = {}, {}
        for sec in self._securities:
            logrets = self._historical_data[f'{sec}-logret']
            ecdf[sec] = ECDF(logrets)
            ecdf_inv[sec] = self._monotone_fn_inverter(ecdf[sec], logrets)
        self.ecdf = ecdf
        self.ecdf_inv = ecdf_inv


    def _monotone_fn_inverter(self, fn, x, vectorized=True, bounds_error=False, **keywords):
        """
        Given a monotone function fn (no checking is done to verify monotonicity)
        and a set of x values, return an linearly interpolated approximation
        to its inverse from its values on x.
        """
        x = np.asarray(x)
        if vectorized:
            y = fn(x, **keywords)
        else:
            y = []
            for _x in x:
                y.append(fn(_x, **keywords))
            y = np.array(y)
        a = np.argsort(y)
        inverse_fn = scipy.interpolate.interp1d(y[a], x[a], \
                    bounds_error=bounds_error, fill_value='extrapolate')
        return inverse_fn




    

