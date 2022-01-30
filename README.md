# risky
This is a Python package for estimating portfolio risk metrics via Monte Carlo simulation. 

For running simulations, three types of stochastic model are supported: geometric Brownian motion (GBM), Gaussian copula models, and t-copula models. Historical data must be provided to calibrate for simulation. Any dataset containing price data in its columns will do. 

________________________________
#### Topics:
* [Models](#Models)
* [Portfolios](#Portfolios)
* [Analysis](#Analysis)
________________________________


## Models

All financial models in `risky` inherit from the same abstract model class `AbstractModel` so they all have the same interface. In general, if a historical dataset of prices is loaded into a pandas dataframe called `my_historical_dataset` then a model is created and calibrated like this:

```python
from risky import GBM, GaussianCopula, TCopula

model = GBM()            # for a geometric Brownian motion model
#model = GaussianCopula()  for a Gaussian copula model
#model = TCopula(1)        for a Student's t-copula model (takes one arg for degrees of freedom)

model.add_historical(my_historical_dataset)
model.calibrate()
```
The `add_historical` method loads the historical dataset into the object and then the `calibrate` method performs the calibration based on that data. The model is then ready to simulate. To run a simulation for later analysis, it is as simple as
```python
N_steps = 30     # number of steps to simulate into the future (units taken from historical data set)
N_iter = 10000   # number of iterations to run in Monte Carlo

filepath = model.run_simulation(N_steps, N_iter)  # output is saved to file
```
The results of the simulation along with the historical data are stored in a HDF5 file, the path to which is returned by the `run_simulation` method (`filepath` in this example). An optional argument can also specify where to save the simulation files.

________________________________

## Portfolios

`Portfolio` objects are able to work with `Stock`, `Call`, and `Put` objects to easily compute the net payoff function for a portfolio. To use this, make a list of all positions in the portfolio and pass it to `Portfolio` at instantiation:
```python
from risky import Stock, Call, Put, Portfolio

positions = [Stock('AAPL', 50, 169.80),    # 50 shares of AAPL bought at $169.80
            Stock('GOOG', -10, 2725.81),   # 10 shares of GOOG in a short position (initially at $2725.81)
            Call('MSFT', 310.0, 1.50),     # call option for 100 shares of MSFT with strike $310.0 and premium $1.50
            Put('INTC',  50.0,  0.04)]     # put option for 100 shares of INTC with strike $50.0 and premium $0.04
            
my_portfolio = Portfolio(positions)
```
The net payoff of the portfolio is computed with the `payoff` method.
________________________________

## Analysis

The `Analysis` class contains all the methods needed to validate the simulation model, determine portfolio risk metrics, and generally visualize the data. All the visualization is done using [Bokeh](https://bokeh.org/).

With the path to a simulation file, `filepath`, a corresponding analysis is started with
```python
from risky import Analysis

my_analysis = Analysis(filepath)
```
 The `Analysis` object `my_analysis` handles reading from the .h5 file with minimal RAM usage so as to prevent excessively slow performance when working with large simulations. 