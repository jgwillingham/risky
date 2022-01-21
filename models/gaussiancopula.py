from .abstractmodel import AbstractModel
import numpy as np
import pandas as pd
import scipy


class GaussianCopula(AbstractModel):
    def __init__(self):
        pass
        

    @property
    def name(self):
        return 'gaussian-copula'


    def calibrate(self):
        """
        Calibrate the Gaussian copula (i.e. fit model parameters to the
        provided historical data)
        """
        if len(self._historical_data) == 0:
            raise Exception('No historical data to calibrate to')

        self._get_empirical_marginals()

        logret_data = self._historical_data[self._logret_columns]
        pseudo_observations = []
        for sec in self._securities:
            logrets = logret_data[f'{sec}-logret']
            ecdf = self.ecdf[sec]
            pseudo_observations.append( ecdf(logrets) )
        U = np.array(pseudo_observations)
        
        P = scipy.stats.norm.ppf(U)
        P = P.T[~np.isinf(P.T).any(axis=1)].T
        self.copula_corr = np.corrcoef(P)
        self.copula_corr_cholesky = np.linalg.cholesky(self.copula_corr).T
        self.X0 = self._historical_data[self._securities].dropna().iloc[-1].values


    def sample_gaussian_copula(self, num_steps):
        """
        Samples the calibrated Gaussian copula
        """
        x = np.random.randn(self._num_securities, num_steps)
        z = self.copula_corr_cholesky @ x
        u = scipy.stats.norm.cdf(z)
        return u


    def simulate_jump(self, num_steps):
        sim_df = self.simulate_path(num_steps)
        endval = sim_df[self._securities].iloc[-1].values
        return endval


    def simulate_path(self, num_steps, return_df=False):
        """
        Simulates stock movements: the log-returns are sampled from a 
        joint distribution which has empirical marginals and Gaussian copula
        """
        u = self.sample_gaussian_copula(num_steps)
        
        logsteps = np.array([self.ecdf_inv[self._securities[i]]( u[i] ) \
                            for i in range(self._num_securities)])
        cop_walk = np.nancumsum(logsteps, axis=1)
        walk = self.X0 * np.exp(cop_walk.T)
        if return_df:
            walk = pd.DataFrame(walk, columns=self._securities)
        
        return walk