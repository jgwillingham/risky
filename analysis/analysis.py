from bokeh.plotting import figure, show
import bokeh.palettes 
import pandas as pd



class Analysis:
    """
    Analysis objects take a simulation file (.h5) and provide
    all the necessary plotting and analysis methods
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.historical = self.read_historical()
        self.securities = self.get_securities()
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

    
    def plotsim(self, sim_num):
        """
        Plots a given simulation along with the historical data
        """
        sim_df = self.read_sim(sim_num)
        plot_df = pd.concat([self.historical, sim_df], ignore_index=True)

        fig = figure(title='Simulation', y_axis_label='$')
        for sec,color in zip(self.securities, self.colors):
            fig.line(plot_df.index, plot_df[sec], color=color, \
                        width=1, legend_label=sec)
            fig.line(plot_df.index, plot_df[f'{sec}-sim'], color=color,\
                        width=1, alpha=0.35)
        fig.legend.location = 'top_left'
        show(fig)
        return fig


    def plotall(self):
        """
        Plots all simulations in the provided simulation dataset 
        alongside the historical data
        """
        pass