from knwopt.swarm_agent import Swarm, House
import os
import pandas as pd
from time import time

# get data and load profile
# the base
N = 5
# number of simulated timesteps
K = 24 # one week
timestamp  =pd.date_range(start="2021-01-01", freq="60Min", periods= K)
load = pd.Series([5.]*K,index=timestamp)

def simulate(n:int):
    """simulate n houses over a year

    Parameters
    ----------
    n : int
        number of houses
    """
    # create the swarm
    houses = []
    for i in range(n):
        house = House(load)
        house.name = f"House{i}"
        houses.append(house)
    swarm = Swarm(houses)
    # start the simulation
    done = False
    while not done:
        state, reward, done, info = swarm.policy()
       

table = pd.DataFrame(columns=["number_of_houses","computation_time","steps"])

for i in range(1,8):
    print("----------------------------------------------------------------")
    print(f"trying to simulate {N**i} houses...")
    t = time()
    simulate(N**i)
    t = time() - t

    table = pd.concat([table,pd.DataFrame({
        "number_of_houses": [N**i],
        "computation_time":[t],
        "steps":[K]
    })])
table["mean_computaion_time_per_step"] = table['computation_time']/table['steps']
# save data
path = os.path.split(__file__)[0] + "/" if len(os.path.split(__file__)[0]) > 0  else ""
data_path = path + "computation_performance_dispatcher.csv"
table.to_csv(data_path)



