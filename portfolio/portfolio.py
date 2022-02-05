from .derivatives import *
from IPython.display import display
import pandas as pd


class Portfolio:
    def __init__(self, positions=[]):
        self.positions = []
        self.payoff_fns = []
        self.securities = []
        if len(positions) != 0:
            self.build(positions)


    def build(self, positions):
        self.positions = positions
        self.payoff_fns = [position.payoff for position in positions]
        self.securities = [position._name for position in positions]

    
    def payoff(self, prices):
        profits = [position.payoff(price) \
                    for position,price in zip(self.positions,prices)]
        return sum(profits)


    def payoff_sim(self, sim_df):
        profits = [self.payoff(sim_df.iloc[i]) for i in range(len(sim_df))]
        return profits


    def summary(self):
        derivatives = [position for position in self.positions if isinstance(position,StockOption)]
        non_derivatives = [position for position in self.positions if position not in derivatives]
        
        deriv_dict = {'Type':[], 'Underlying':[], 'Strike':[], 'Premium':[], 'Shares':[]}
        for deriv in derivatives:
            deriv_dict['Type'].append(deriv.__class__.__name__)
            deriv_dict['Underlying'].append(deriv.underlying.name)
            deriv_dict['Strike'].append(deriv.strike)
            deriv_dict['Premium'].append(deriv.premium)
            deriv_dict['Shares'].append(deriv._underlying._num_shares)

        nonderiv_dict = {'Stock':[], 'Shares':[], 'Initial Price':[]}
        for nonderiv in non_derivatives:
            nonderiv_dict['Stock'].append(nonderiv.name)
            nonderiv_dict['Shares'].append(nonderiv._num_shares)
            nonderiv_dict['Initial Price'].append(nonderiv._init_price)

        deriv_df = pd.DataFrame(deriv_dict)
        nonderiv_df = pd.DataFrame(nonderiv_dict)

        print('Derivative Securities :\n')
        display(deriv_df)
        print('\nNon-Derivative Securities :\n')
        display(nonderiv_df)
            
        
        
    
        

