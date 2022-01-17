from .abstractmodel import AbstractModel
import numpy as np

class GBM(AbstractModel):
    def __init__(self):
        pass


    @property
    def name(self):
        return 'GBM'


    def calibrate(self):
        if len(self.historical_data) == 0:
            raise Exception('No historical data to calibrate to')
        log_returns = self._historical_data[self._logret_columns]
        self.mu = log_returns.mean().values
        self.cov = log_returns.cov().values
        self.cov_cholesky = np.linalg.cholesky(self.cov)
        self.X0 = self._historical_data[self._securities].dropna().iloc[-1].values
        self.params = {'mu':self.mu, 'cov':self.cov,'X0':self.X0}


    def jump_simulate(self, num_steps, num_iter):
        L = self.cov_cholesky
        normal = np.random.randn(self._num_securities)
        logstep = self.mu*num_steps + np.sqrt(num_steps)*L @ normal
        Xt = self.X0 * np.exp(logstep)
        return Xt


    def path_simulate(self, num_steps, num_iter):
        normals = np.random.randn(num_steps, self._num_securities)
        sim_logret = [self.mu + self.cov_cholesky @ normals[i] \
                        for i in range(num_steps)]
        random_walk = np.cumsum(sim_logret, axis=0)
        gbm = self.X0 * np.exp(random_walk)
        return gbm






