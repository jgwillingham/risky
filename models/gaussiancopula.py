from .abstractmodel import AbstractModel
import numpy as np
import pandas as pd
import scipy
from statsmodels.distributions.empirical_distribution import ECDF



class GaussianCopula(AbstractModel):
    def __init__(self):
        pass
        

    @property
    def name(self):
        return 'Gaussian Copula'


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
    

    def _get_empirical_marginals(self):
        """
        Builds the empirical marginal CDF (and its inverse) for 
        each asset based on the provided historical data
        """
        ecdf, ecdf_inv = {}, {}
        for sec in self._securities:
            logrets = self.historical_data[f'{sec}-logret']
            ecdf[sec] = ECDF(logrets)
            ecdf_inv[sec] = self.monotone_fn_inverter(ecdf[sec], logrets)
        self.ecdf = ecdf
        self.ecdf_inv = ecdf_inv


    def monotone_fn_inverter(self, fn, x, vectorized=True, bounds_error=False, **keywords):
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


    def sample_gaussian_copula(self, num_steps):
        """
        Samples the calibrated Gaussian copula
        """
        x = np.random.randn(self._num_securities, num_steps)
        z = self.copula_corr_cholesky @ x
        u = scipy.stats.norm.cdf(z)
        return u


    def jump_simulate(self, num_steps, num_iter):
        sim_df = self.simulate(num_steps)
        endval = sim_df[[f'{stock}-sim' for stock in self.stocks]].iloc[-1].values
        return endval
        

    def path_simulate(self, num_steps, num_iter):
        """
        Simulates stock movements: the log-returns are sampled from a 
        joint distribution which has empirical marginals and Gaussian copula
        """
        u = self.sample_gaussian_copula(num_steps)
        
        logsteps = np.array([self.ecdf_inv[self._securities[i]]( u[i] ) \
                            for i in range(self._num_securities)])
        cop_walk = np.nancumsum(logsteps, axis=1)
        walk = self.X0 * np.exp(cop_walk.T)
        sim_df = pd.DataFrame(walk, columns=[f'{sec}-sim' \
                            for sec in self._securities])
        
        return sim_df