from knwopt.swarm_agent import Swarm, House
import os
import numpy as np
import oemof.solph as solph
import oemof_eso.components as comps
from oemof_eso.modelling.results import Result
import pandas as pd
from time import time

# timesteps (for filenames)
MINUTES = 60

# amount of houses (for filenames)
HOUSES = 49

# target directory for saving simulations as csv files
CSV_PATH = "."

# normed profiles with 10 min timesteps
PROFILE_HOUSES = os.path.join(os.getcwd(), "knwopt", "data",
                              f"MAGGIE_{HOUSES}_houses_{MINUTES}_min.csv")

# real data
YEARLY_HOUSES_DATA = os.path.join(os.getcwd(), "knwopt", "data",
                                  "210921_Zusammenfassung_der_WP_mit_Standort_Spieldaten_fuer_OpenSource.xlsx")

profiles_df = pd.read_csv(PROFILE_HOUSES)
profiles_df.index = pd.DatetimeIndex(pd.date_range(start="2021-01-01", freq=f"{MINUTES}Min", periods=len(profiles_df)))
dhw_df = pd.read_excel(YEARLY_HOUSES_DATA, sheet_name="Trinkwarmwasser")
heat_df = pd.read_excel(YEARLY_HOUSES_DATA, sheet_name="Raumwarme")

season_indices = {
        "spring": ("2021-05-01 01:00:00", "2021-05-06 00:00:00"),
        "summer": ("2021-08-01 01:00:00", "2021-08-06 00:00:00"),
        "fall": ("2021-10-15 01:00:00", "2021-10-20 00:00:00"),
        "winter": ("2021-12-15 01:00:00", "2021-12-20 00:00:00")
    }

def prepare_house_data(i, season=None):
    if season is not None:
        idx = season_indices[season]
        dhw_load = profiles_df.loc[idx[0]:idx[1], f"u__DHW_House{i+1}"]
        heat_load = profiles_df.loc[idx[0]:idx[1], f"u__HeatDemand_House{i+1}"]
        index = pd.date_range(start=idx[0], end=idx[1], freq=f"{MINUTES}Min")
    else:
        dhw_load = profiles_df.loc[:, f"u__DHW_House{i+1}"]
        heat_load = profiles_df.loc[:, f"u__HeatDemand_House{i+1}"]
        index = profiles_df.index
    data = {
        "DHW": {
            "load": 6 * dhw_load * dhw_df.loc[i,"Bedarf Trinkwarmwasser"],
            "cop": pd.Series(dhw_df.loc[i,"COP (B10/W55)"], index=index),
            "power_electric": dhw_df.loc[i,"elektrische Leistung (B10/W55)"],
            "volume": dhw_df.loc[i,"Pufferspeicher Volumen"],
            "T_min": dhw_df.loc[i,"Pufferspeicher Temp_min"],
            "T_max": dhw_df.loc[i,"Pufferspeicher Temp_max"],
            "initial_level": np.random.random_sample(),
            "name": f"DHW_House{i+1}"
        },
        "HEAT": {
            "load": 6 * heat_load * heat_df.loc[i,"Bedarf Raumwaerme"],
            "cop": pd.Series(heat_df.loc[i,"COP (B10/W35)"], index=index),
            "power_electric": heat_df.loc[i,"elektrische Leistung (B10/W35)"],
            "volume": heat_df.loc[i,"Pufferspeicher Volumen"],
            "T_min": heat_df.loc[i,"Pufferspeicher Temp_min"],
            "T_max": heat_df.loc[i,"Pufferspeicher Temp_max"],
            "initial_level": np.random.random_sample(),
            "name": f"HEAT_House{i+1}"
        }
    }
    for key in ["DHW", "HEAT"]:
        if data[key]["power_electric"] == 0 or not data[key]["cop"].all():
            print(data[key]["power_electric"])
            print(data[key]["cop"])
            print(i)
    return data

def simulate_oemof(n, season):
    types = ["HEAT", "DHW"]
    idx = season_indices[season]
    timeindex  = pd.date_range(start=idx[0], end=idx[1], freq=f"{MINUTES}Min")
    es = solph.EnergySystem(timeindex=timeindex)

    bel = comps.ElectricBus("bel")
    es.add(bel)

    pubgel = comps.NetworkTransmissionPointElectric(
        "pubgel",
        outputs={bel: solph.Flow()}
    )
    es.add(pubgel)

    start = time()
    print("Building...")
    for i in range(n):
        house_data = prepare_house_data(i, season)
        for typ in types:
            typ_data = house_data[typ]

            bth = comps.ThermalBus(label="bth_" + typ_data["name"])
            es.add(bth)

            hepu = comps.Heatpump(
                label="HePu_" + typ_data["name"],
                COP=typ_data["cop"],
                maxP_th_plus=typ_data["power_electric"],
                minDowntime=1.5,
                minRuntime=1.5,
                inputs={bel: solph.Flow()},
                outputs={bth: solph.Flow()}
            )
            es.add(hepu)

            ts_capacity = typ_data["volume"]/860 * (typ_data["T_max"] - typ_data["T_min"])
            ts = comps.StorageThermal(
                label="TS_" + typ_data["name"],
                maxE_th=ts_capacity,
                EnergyStart=typ_data["initial_level"] * ts_capacity,
                eff_losses=1,
                inputs={bth: solph.Flow()},
                effMaxP_th_minus=1,
                outputs={bth: solph.Flow()}
            )
            es.add(ts)

            demth = comps.DemandThermal(
                label="Demth_" + typ_data["name"],
                load_abstract_th=typ_data["load"],
                inputs={bth: solph.Flow()}
            )
            es.add(demth)

            assth = comps.AssistThermal(
                label="Assth_" + typ_data["name"],
                outputs={bth: solph.Flow(variable_costs=10)}
            )
            es.add(assth)
    print("Set up Model...")
    om = solph.Model(es)
    print(time() - start)
    print(f"Solving {season}...")
    om.solve(cmdline_options={"threads": 6})
    print(time() - start)
    return om

def simulate(n, dispatch=True):
    """simulate n houses over a year

    Parameters
    ----------
    n : int
        number of houses
    """
    # create the swarm
    houses = []
    for i in range(n):
        house_data = prepare_house_data(i)
        house_dhw = House(**house_data["DHW"])
        house_heat = House(**house_data["HEAT"])
        houses.extend([house_dhw, house_heat])
    swarm = Swarm(houses)
    # start the simulation
    done = False
    df = pd.DataFrame(columns=swarm.state_names)
    print("Dispatching...")
    start = time()
    while not done:
        if dispatch:
            state, reward, done, info = swarm.policy()
        else:
            state, reward, done, info = swarm.step()
        df = pd.concat([df, swarm.pdstate])
    print(round(time() - start))
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

amount_houses = dhw_df.shape[0]

"""
seasons = ["winter"]#["spring", "summer", "fall", "winter"]
for season in seasons:
    om = simulate_oemof(int(amount_houses), season)
    results = Result.from_model(om)
    results.to_csv(f"MAGGIE_5day_60min_{season}_49x2houses.csv")
"""
for dispatching in [True, False]:
    df_simulation = simulate(amount_houses, dispatch=dispatching)

    disp_str = "dispatch" if dispatching else "not_dispatch"
    if CSV_PATH is not None:
        path = os.path.join(CSV_PATH, f"summary_simulation_{disp_str}_{MINUTES}min_{HOUSES}x2houses.csv")
        df.to_csv(path)

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
d = pd.DataFrame(d)
# save data
path = os.path.split(__file__)[0] + "/" if len(os.path.split(__file__)[0]) > 0  else ""
data_path = path + f"statistic_analysis_dispatcher_{MINUTES}min_{HOUSES}x2houses.csv"
d.to_csv(data_path)
