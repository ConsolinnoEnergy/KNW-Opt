from knwopt.swarm_agent import Swarm, House
import os
import pandas as pd
import numpy as np
from time import time


# timesteps 
MINUTES = 10

# amount of houses
HOUSES = 49

# target directory for saving simulations as csv files
CSV_PATH = os.path.join(os.getcwd(), "knwopt", "data", "dispatcher_results")

# path to normed profiles with 10 min timesteps
PROFILE_HOUSES = os.path.join(os.getcwd(), "knwopt", "data",
                              f"MAGGIE_49_houses_{MINUTES}min.csv")

# path to parameters for heatpump, demand and thermal storage
YEARLY_HOUSES_DATA = os.path.join(os.getcwd(), "knwopt", "data",
                                  "210921_Zusammenfassung_der_WP_mit_Standort_Spieldaten_fuer_OpenSource.xlsx")

# path to initial storage levels
INITIAL_LEVELS = os.path.join(os.getcwd(), "knwopt", "data",
                              f"initial_levels_49_houses.csv")

profiles_df = pd.read_csv(PROFILE_HOUSES)
profiles_df.index = pd.DatetimeIndex(pd.date_range(start="2021-01-01", freq=f"{MINUTES}Min", periods=len(profiles_df)))
index = profiles_df.index
dhw_df = pd.read_excel(YEARLY_HOUSES_DATA, sheet_name="Trinkwarmwasser")
heat_df = pd.read_excel(YEARLY_HOUSES_DATA, sheet_name="Raumwarme")
initial_level = pd.read_csv(INITIAL_LEVELS, index_col=0)

def simulate(dispatch: bool, n: int) -> pd.DataFrame:
    """simulate n houses over a year

    Parameters
    ----------
    dispatch : bool
        indicates if dispatching or fallback
    n : int
        number of houses

    Returns
    -------
    pd.DataFrame
        result of simulation
    """
    # create the swarm
    houses = []
    for i in range(n):
        dhw_load = profiles_df.loc[index[0]:index[-1], f"u__DHW_House{i+1}"]
        heat_load = profiles_df.loc[index[0]:index[-1], f"u__HeatDemand_House{i+1}"]
        lambda1 = dhw_df.loc[i,"Bedarf Trinkwarmwasser"]/(dhw_df.loc[i,"Bedarf Trinkwarmwasser"] + heat_df.loc[i,"Bedarf Raumwaerme"])
        lambda2 = heat_df.loc[i,"Bedarf Raumwaerme"]/(dhw_df.loc[i,"Bedarf Trinkwarmwasser"] + heat_df.loc[i,"Bedarf Raumwaerme"])
        
        cop = lambda2 * pd.Series(heat_df.loc[i,"COP (B10/W35)"], index=index) + lambda1 * pd.Series(dhw_df.loc[i,"COP (B10/W55)"], index=index)
        power_electric = dhw_df.loc[i,"elektrische Leistung (B10/W55)"]
        load = 60/MINUTES * (dhw_load * dhw_df.loc[i,"Bedarf Trinkwarmwasser"] + heat_load * heat_df.loc[i,"Bedarf Raumwaerme"])
        house = House(
            load=load,
            cop=cop,
            power_electric=power_electric,
            initial_level=initial_level.iloc[i, 0],
            name="House{i}"
        )
        houses.append(house)
    swarm = Swarm(houses)
    # start the simulation
    done = False
    df = pd.DataFrame(columns=swarm.state_names)
    print("Dispatching...")
    while not done:
        if dispatch:
            state, reward, done, info = swarm.policy()
        else:
            state, reward, done, info = swarm.step()
        df = pd.concat([df, swarm.pdstate])
    return df


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
for dispatching in [True, False]:
    start = time()
    df_simulation = simulate(n=HOUSES, dispatch=dispatching)
    df = df_simulation.filter(like="power_thermal", axis=1).sum(axis=1)
    std = df.std()
    mean = df.mean()
    maximum = df.max()
    minimum = df.min()
    q_value = df.quantile(q=0.9)
    d["mean"].append(mean)
    d["standard_deviation"].append(std)
    d["minimum"].append(minimum)
    d["maximum"].append(maximum)
    d["q_value"].append(q_value)
    d["number_of_houses"].append(HOUSES)
    d["dispatching"].append(dispatching)
    if CSV_PATH is not None:
        disp_str = "dispatch" if dispatching else "no_dispatch"
        path = os.path.join(CSV_PATH, f"simulation_{disp_str}_MAGGIE_{HOUSES}.csv")
        df_simulation.to_csv(path)
    print(time() - start)


    stat_df = pd.DataFrame(d)
    # save data
    path = os.path.split(__file__)[0] + "/" if len(os.path.split(__file__)[0]) > 0  else ""
    data_path = os.path.join(os.getcwd(), f"statistic_analysis_dispatcher_MAGGIE_49.csv")
    stat_df.to_csv(data_path)
