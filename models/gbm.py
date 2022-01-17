from .abstractmodel import AbstractModel


class GBM(AbstractModel):
    def __init__(self):
        pass


    @property
    def name(self):
        return 'GBM'


    def calibrate(self):
        if len(self.historical_data) == 0:
            raise Exception('No historical data to calibrate to')


    def jump_simulate(self, num_steps, num_iter):
        pass


    def path_simulate(self, num_steps, num_iter):
        pass




