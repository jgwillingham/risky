from .abstractmodel import AbstractModel
import numpy as np
import pandas as pd
import scipy
from statsmodels.distributions.empirical_distribution import ECDF


class TCopula(AbstractModel):
    def __init__(self, dof):
        self.dof = dof
        

    @property
    def name(self):
        return 't Copula'


    def calibrate(self):
        """
        Calibrate the t copula (i.e. fit model parameters to the
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
        
        # Compute Kendall's tau correlation matrix
        tau = np.empty([self._num_securities, self._num_securities])
        for i in range(self._num_securities):
            for j in range(self._num_securities):
                tau_ij,p = scipy.stats.kendalltau(U[i], U[j])
                tau[i,j] = tau_ij
                    
        self.copula_corr = np.sin(np.pi/2 * tau)
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


    def sample_t_copula(self, num_steps):
        """
        Samples the calibrated t copula
        """
        t_dist = scipy.stats.multivariate_t(shape=self.copula_corr, df=self.dof)
        t = t_dist.rvs(size=num_steps)
        v = scipy.stats.t.cdf(t, df=self.dof)
        return v.T


    def jump_simulate(self, num_steps, num_iter):
        sim_df = self.path_simulate(num_steps)
        endval = sim_df[[f'{sec}-sim' for sec in self._securities]].iloc[-1].values
        return endval
        

    def path_simulate(self, num_steps, num_iter):
        """
        Simulates stock movements: the log-returns are sampled from a 
        joint distribution which has empirical marginals and t copula
        """
        u = self.sample_t_copula(num_steps)
        
        logsteps = np.array([self.ecdf_inv[self._securities[i]]( u[i] ) \
                            for i in range(self._num_securities)])
        cop_walk = np.nancumsum(logsteps, axis=1)
        walk = self.X0 * np.exp(cop_walk.T)
        sim_df = pd.DataFrame(walk, columns=[f'{sec}-sim' \
                            for sec in self._securities])
        
        return sim_df