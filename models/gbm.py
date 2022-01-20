from .abstractmodel import AbstractModel
import numpy as np
import pandas as pd


class GBM(AbstractModel):
    def __init__(self):
        pass


    @property
    def name(self):
        return 'gbm'


    def calibrate(self):
        """
        Calibrate the model (i.e. fit model parameters to the
        provided historical data)
        """
        if len(self._historical_data) == 0:
            raise Exception('No historical data to calibrate to')
        log_returns = self._historical_data[self._logret_columns]
        self.mu = log_returns.mean().values
        self.cov = log_returns.cov().values
        self.cov_cholesky = np.linalg.cholesky(self.cov)
        self.X0 = self._historical_data[self._securities].dropna().iloc[-1].values
        self.params = {'mu':self.mu, 'cov':self.cov,'X0':self.X0}

        self._iscalibrated = True


    def simulate_jump(self, num_steps):
        """
        Simulate the security value only num_steps into the future
        but for no time in between
        """
        if not self._iscalibrated:
            raise Exception('Model must first be calibrated')

        L = self.cov_cholesky
        normal = np.random.randn(self._num_securities)
        sim_logstep = self.mu*num_steps + np.sqrt(num_steps)*L @ normal
        Xt = self.X0 * np.exp(sim_logstep)
        return Xt


    def simulate_path(self, num_steps):
        """
        Simulate the security value for num_steps into the future
        """
        if not self._iscalibrated:
            raise Exception('Model must first be calibrated')

        L = self.cov_cholesky
        normals = np.random.randn(num_steps, self._num_securities)
        sim_logret = [self.mu + L @ normals[i] \
                        for i in range(num_steps)]
        random_walk = np.cumsum(sim_logret, axis=0)
        gbm = self.X0 * np.exp(random_walk)
        
        sim_df = pd.DataFrame(gbm, columns=self._securities)

        return sim_df






