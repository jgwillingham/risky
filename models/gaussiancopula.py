from .abstractmodel import AbstractModel


class GaussianCopula(AbstractModel):
    name = 'Gaussian Copula'
    iscalibrated = False

    def add_historical(self, dataset):
        pass

    def calibrate(self):
        pass

    def jump_simulate(self, num_steps, num_iter):
        pass

    def path_simulate(self, num_steps, num_iter):
        pass