

class Portfolio:
    def __init__(self, positions=[]):
        self.positions = []
        self.stakes = []
        self.return_fns = []
        if len(positions) != 0:
            self.build(positions)


    def build(self, positions):
        self.positions = positions
        self.return_fns = [position.payoff for position in positions]

    
    def payoff(self, prices):
        profits = [position.payoff(price) \
                    for position,price in zip(self.positions,prices)]
        return sum(profits)


    def payoff_sim(self, sim_df):
        profits = [self.payoff(sim_df.iloc[i]) for i in range(len(sim_df))]
        return profits
    
        

