from bokeh.plotting import figure, show
import bokeh.palettes 
import scipy
import numpy as np
import pandas as pd
from h5py import File as h5pyFile



class Analysis:
    """
    Analysis objects take a simulation file (.h5) and provide
    all the necessary plotting and analysis methods
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.historical = self.read_historical()
        self.securities = self.get_securities()
        self.num_securities = len(self.securities)
        self.num_iterations = self.get_num_iterations()
        self.colors = bokeh.palettes.Dark2_5



    def read_historical(self):
        historical_data = pd.read_hdf(self.filepath, 'historical')
        return historical_data


    def read_sim(self, sim_num):
        sim_name = f'simulations/sim-{sim_num}'
        sim_path = pd.read_hdf(self.filepath, sim_name)
        return sim_path

    
    def get_securities(self):
        sim_df = self.read_sim(0)
        cols = sim_df.columns.to_list()
        securities = [col.split('-')[0] for col in cols]
        return securities


    def get_num_iterations(self):
        with h5pyFile(self.filepath) as h5file:
            simulations = h5file['simulations'].keys()
            num_iterations = len(simulations)
        return num_iterations


    def get_section(self, time_step):
        """
        Returns all simulation results for a single future time step.
        A "cross section" of the simulation results
        """
        df = pd.DataFrame(columns=self.securities)
        for sec in self.securities:
            df[sec] = pd.Series([self.read_sim(ii)[sec][time_step] \
                    for ii in range(self.num_iterations)])  
        return df
    

    def plot_sim(self, sim_num):
        """
        Plots a given simulation along with the historical data
        """
        sim_df = self.read_sim(sim_num)
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
        sim_df0 = self.read_sim(0)
        df0 = pd.concat([self.historical, sim_df0], ignore_index=True)
        L = len(self.historical)
        time_steps = df0.index - L+1 # center t=0 on last real data point

        fig = figure(title='Simulation', y_axis_label='$', x_axis_label='Time Steps', \
                        plot_height=400, plot_width=600)
        
        print('Plotting . . . ', end='')
        for sec,color in zip(self.securities, self.colors):
            # plot historical
            fig.line(time_steps[:L], df0[sec][:L], color=color, \
                        width=2, legend_label=sec)
            # plot simulations
            fig.line(time_steps[L-1:], df0[sec][L-1:], color=color,\
                        width=1, alpha=0.35)
            for ii in range(1, self.num_iterations):
                sim_df = self.read_sim(ii)
                df = pd.concat([self.historical, sim_df], ignore_index=True)
                fig.line(time_steps[L-1:], df[sec][L-1:], color=color,\
                            width=1, alpha=0.35)
            print('. . ', end='')

        fig.legend.location = 'top_left'
        show(fig)
        return fig


    def plot_distributions(self, time_step, kde=True):

        df = self.get_section(time_step)

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
        Returns the number of bins for a histogram according to the Friedman-Draconis rule
        """
        iqr = data.quantile(0.75) - data.quantile(0.25)
        n = len(data)
        bin_width = 2*iqr/ n**(1/3)
        num_bins = (data.max() - data.min())/bin_width
        return int(num_bins)


    
