from knwopt.swarm_agent import Swarm, House
import os
import pandas as pd
import numpy as np
from time import time

# get data and load profile
# the base
N = 5
# number of simulated timesteps
K = 24 * 7# one day
timestamp  =pd.date_range(start="2021-01-01", freq="60Min", periods= K)
load = pd.Series([5.]*K,index=timestamp)

def simulate(n:int, dispatch=True):
    """simulate n houses over a year

    Parameters
    ----------
    n : int
        number of houses
    """
    # create the swarm
    houses = []
    for i in range(n):
        a = 6
        house = House(load + pd.Series( a*np.random.random_sample(len(timestamp)) - a/2,index=timestamp))
        house.initial_level = np.random.random_sample()
        house.name = f"House{i}"
        houses.append(house)
    swarm = Swarm(houses)
    # start the simulation
    done = False
    df = pd.DataFrame(columns=swarm.state_names)
    while not done:
        if dispatch:
            state, reward, done, info = swarm.policy()
        else:
            state, reward, done, info = swarm.step()
        df = pd.concat([df, swarm.pdstate])
   
    df = df.filter(like="power_thermal", axis=1).sum(axis=1)
    std = df.std()
    mean = df.mean()
    maximum = df.max()
    minimum = df.min()
    q_value = df.quantile(q=0.9)

    return mean, std, maximum, minimum, q_value

table = pd.DataFrame(columns=["number_of_houses","computation_time","steps"])
d = {
    'mean':[],
    'standard_deviation':[],
    'maximum':[],
    'minimum':[],
    'q_value':[],
    'number_of_houses':[],
    'dispatching':[]
    }
for i in range(1,4):
    for dispatching in [True,False]:
        mean, std, maximum, minimum, q_value = simulate(N**i, dispatch= dispatching)
        d["mean"].append(mean)
        d["standard_deviation"].append(std)
        d["minimum"].append(minimum)
        d["maximum"].append(maximum)
        d["q_value"].append(q_value)
        d["number_of_houses"].append(N**i)
        d["dispatching"].append(dispatching)
    

d = pd.DataFrame(d)
# save data
path = os.path.split(__file__)[0] + "/" if len(os.path.split(__file__)[0]) > 0  else ""
data_path = path + f"statistic_analysis_dispatcher_houses_{N**i}.csv"
d.to_csv(data_path)



