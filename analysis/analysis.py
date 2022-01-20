from bokeh.plotting import figure, show
import bokeh.palettes 
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
    

    def plot_sim(self, sim_num):
        """
        Plots a given simulation along with the historical data
        """
        sim_df = self.read_sim(sim_num)
        df = pd.concat([self.historical, sim_df], ignore_index=True)
        L = len(self.historical)
        time_steps = df.index - L + 1 # center t=0 on last real data point

        fig = figure(title=f'Simulated Path {sim_num}', y_axis_label='$', x_axis_label='Time steps', \
                        plot_height=400, plot_width=800)

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
                        plot_height=400, plot_width=800)

        for sec,color in zip(self.securities, self.colors):
            fig.line(time_steps[:L], df0[sec][:L], color=color, \
                        width=2, legend_label=sec)
            fig.line(time_steps[L-1:], df0[sec][L-1:], color=color,\
                        width=1, alpha=0.35)

            for ii in range(1, self.num_iterations):
                sim_df = self.read_sim(ii)
                df = pd.concat([self.historical, sim_df], ignore_index=True)
                fig.line(time_steps[L-1:], df[sec][L-1:], color=color,\
                            width=1, alpha=0.35)

        fig.legend.location = 'top_left'
        show(fig)
        return fig