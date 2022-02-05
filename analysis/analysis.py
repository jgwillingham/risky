from bokeh.plotting import figure, show
import bokeh.palettes 
import scipy
import numpy as np
import pandas as pd
import h5py



class Analysis:
    """
    Analysis objects take a simulation file (.h5) and provide
    all the necessary plotting and analysis methods
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self._fetch_information()
        self.colors = bokeh.palettes.Dark2_5


    def _fetch_information(self):
        with h5py.File(self.filepath) as file:
            hist_ds = file['historical']
            historical = hist_ds[:]
            self.securities = hist_ds.attrs['securities']
            self.num_securities = len(self.securities)
            self.historical = pd.DataFrame(historical, columns=self.securities)
            sim_ds = file['simulation']
            self.num_steps = sim_ds.shape[0]
            self.num_iterations = sim_ds.shape[1]//self.num_securities


    def read_sim(self, sim_num):
        ii = sim_num
        N = self.num_securities
        with h5py.File(self.filepath, 'r') as file:
            sim_path = file['simulation'][:,ii*N:(ii+1)*N]
        return sim_path


    def read_sim_df(self, sim_num):
        sim_path = self.read_sim(sim_num)
        sim_df = pd.DataFrame(sim_path,columns=self.securities)
        return sim_df


    def get_section_df(self, time_step):
        """
        Returns all simulation results for a single future time step.
        A "cross section" of the simulation results
        """
        with h5py.File(self.filepath, 'r') as file:
            cross_section = file['simulation'][time_step,:]

        section_df = pd.DataFrame()
        N = self.num_securities
        for jj in range(N):
            sec = self.securities[jj]
            section_df[sec] = cross_section[jj::N] # jump by N steps for each security
        return section_df
    

    def plot_sim(self, sim_num):
        """
        Plots a given simulation along with the historical data
        """
        sim_df = self.read_sim_df(sim_num)
        df = pd.concat([self.historical, sim_df], ignore_index=True)
        L = len(self.historical)
        time_steps = df.index - L + 1 # center t=0 on last real data point

        fig = figure(title=f'Simulated Path {sim_num}', y_axis_label='$', x_axis_label='Time steps', \
                        plot_height=400, plot_width=600)

        for sec,color in zip(self.securities, self.colors):
            # plot historical data
            fig.line(time_steps[:L], df[sec][:L], color=color, \
                        width=2, legend_label=sec)
            # plot simulated data
            fig.line(time_steps[L-1:], df[sec][L-1:], color=color,\
                        width=2, alpha=0.35)

        fig.legend.location = 'top_left'
        show(fig)
        return fig


    def plot_all(self):
        """
        Plots all simulations in the provided simulation dataset 
        alongside the historical data
        """
        L = len(self.historical)
        N = self.num_securities
        index = np.arange( L + self.num_steps )
        time_steps = index-L+1 # center t=0 on last real data point

        fig = figure(title='Simulation', y_axis_label='$', x_axis_label='Time Steps', \
                        plot_height=400, plot_width=600)

        with h5py.File(self.filepath) as file:
            simdata = file['simulation']
            
            print('Plotting . . . ', end='')
            for jj,color in zip(range(N), self.colors):
                sec = self.securities[jj]
                # plot historical
                fig.line(time_steps[:L], self.historical[sec][:L], color=color, \
                            width=2, legend_label=sec)
                # plot simulations
                for ii in range(1, self.num_iterations):
                    fig.line(time_steps[L:], simdata[:,ii*N+jj], color=color,\
                                width=1, alpha=0.35)
                print('. . ', end='')

        fig.legend.location = 'top_left'
        show(fig)
        return fig


    def plot_distributions(self, time_step, kde=True):

        df = self.get_section_df(time_step)

        fig = figure(title=f'Price Distribution After {time_step} Steps ({self.num_iterations} iterations)',\
                     x_axis_label='$', plot_height=400, plot_width=600)

        for sec, color in zip(self.securities, self.colors):
            data = df[sec]          
            num_bins = self.fd_bins(data)
            hist, edges = np.histogram(data, density=True, bins=num_bins)
            fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], \
                    color=color, alpha=0.45, legend_label=sec)
            if kde:
                f = scipy.stats.gaussian_kde(data)
                xmin = min(min(data), min(data))
                xmax = max(max(data), max(data))
                X = np.linspace(xmin, xmax, 1000)
                fig.line(X, f(X), width=2, color=color)
        
        fig.legend.location = 'top_right'
        fig.y_range.start = 0
        show(fig)
        return fig


    def fd_bins(self, data):
        """
        Returns the number of bins for a histogram according to the Friedman-Diaconis rule
        """
        iqr = data.quantile(0.75) - data.quantile(0.25)
        n = len(data)
        bin_width = 2*iqr/ n**(1/3)
        num_bins = (data.max() - data.min())/bin_width
        return int(num_bins)


    def get_var(self, portfolio, time_step, alpha=0.05):
        """
        Returns the value-at-risk (VaR) for the given portfolio
        forecasted out to time_step. Alpha defines the worst cases.
        e.g. alpha=0.05 means the worst 5% of cases have payoff worse than
        VaR
        """
        df = self.get_section_df(time_step)
        dataset = df.to_numpy()
        pf_prices = [self.arrange_prices_for_portfolio(prices, portfolio) \
                        for prices in dataset]
        payoffs = [portfolio.payoff(prices) for prices in pf_prices]
        f = scipy.stats.gaussian_kde(payoffs)
        inv_cdf = lambda x: f.integrate_box(-np.inf, x) - alpha
        VaR = scipy.optimize.newton(inv_cdf, -1)
        return VaR


    def plot_var(self, portfolio, time_step, alpha=0.05, x0=-10):
        """
        plots the value-at-risk of the given for portfolio 
        forecasted out to the given time-step. Returns the 
        kernel density estimate of the payoff distribution 
        function 
        """
        df = self.get_section_df(time_step)
        dataset = df.to_numpy()
        pf_prices = [self.arrange_prices_for_portfolio(prices, portfolio) \
                        for prices in dataset]
        payoffs = [portfolio.payoff(prices) for prices in pf_prices]
        f = scipy.stats.gaussian_kde(payoffs)
        cdf_alpha = lambda x: f.integrate_box(-np.inf, x) - alpha
        VaR = scipy.optimize.newton(cdf_alpha, x0)

        hist, edges = np.histogram(payoffs, density=True, bins=self.fd_bins(pd.Series(payoffs)))
        
        neg = edges[edges < 0]
        lneg = neg[neg < VaR]
        uneg = neg[neg >= VaR]
        pos = edges[edges >= 0]
        
        lneg = list(lneg); uneg = list(uneg)
        
        lneg.append(uneg[0])
        uneg.append(pos[0])
        
        lneghist = hist[:len(lneg)-1]
        uneghist = hist[len(lneg)-1:len(neg)]
        poshist = hist[len(neg):len(hist)]
        
        fig = figure(title=f'Projected Returns Distribution ({self.num_iterations} iterations)', plot_height=300, plot_width=500, x_axis_label='Return')
        fig.quad(top=lneghist, bottom=0, left=lneg[:-1], right=lneg[1:], alpha=0.5, color='darkred', legend_label=f'VaR : ${abs(np.round(VaR, 2))}')
        fig.quad(top=uneghist, bottom=0, left=uneg[:-1], right=uneg[1:], alpha=0.5, color='red')
        fig.quad(top=poshist, bottom=0, left=pos[:-1], right=pos[1:], alpha=0.25, color='darkgreen')
        
        X1 = np.linspace(1.2*min(payoffs), VaR, 500)
        X2 = np.linspace(VaR, 1.2*max(payoffs), 500)
        fig.line(X1, f(X1), width=3, color='darkred')
        fig.line(X2, f(X2), width=3, color='black')
        
        fig.y_range.start = 0
        show(fig)
        return f


    def arrange_prices_for_portfolio(self, prices, portfolio):
        price_dict = {sec:price for sec,price in zip(self.securities, prices)}
        pf_prices = [price_dict[sec] for sec in portfolio.securities]
        return pf_prices
            