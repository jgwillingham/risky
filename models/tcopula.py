from .abstractmodel import AbstractModel
import numpy as np
import pandas as pd
import scipy


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