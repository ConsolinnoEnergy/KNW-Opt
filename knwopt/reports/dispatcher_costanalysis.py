"""berechnet Größen, die zur Kostenanalyse benötigt werden.
Z.B. mit Hilfe von
https://www.bayernwerk-netz.de/content/dam/revu-global/bayernwerk-netz/files/netz/netzzugang/netzentgeltestrom/20201006-bayernwerk-preisblaetter-strom-2021gesamt.pdf
"""
import os
from numpy import float64

import pandas as pd

# path to directory with agent data
DATA_PATH = os.path.join(os.getcwd(), "knwopt", "data")

simulation_paths = {
    "dispatch": os.path.join(DATA_PATH, "dispatcher_results", "simulation_dispatch_final_MAGGIE_49.csv"),
    "no_dispatch": os.path.join(DATA_PATH, "dispatcher_results", "simulation_no_dispatch_final_MAGGIE_49.csv")
}

# path to parameters of heatpumps, demand, thermal storages 
yearly_house_data = os.path.join(
    DATA_PATH,
    "210921_Zusammenfassung_der_WP_mit_Standort_Spieldaten_fuer_OpenSource.xlsx"
)

for disp in simulation_paths.keys():
    simulation_path = simulation_paths[disp]
    df_sim = pd.read_csv(simulation_path)
    dhw_df = pd.read_excel(yearly_house_data, sheet_name="Trinkwarmwasser")
    heat_df = pd.read_excel(yearly_house_data, sheet_name="Raumwarme")

    df_power_thermal = df_sim.filter(like="power_thermal")

    # empty series
    cop_series = pd.Series(index=[f"House_{i}" for i in range(df_power_thermal.shape[1])], dtype= float64)

    # calculate cops
    for i in range(df_power_thermal.shape[1]):
        lambda1 = dhw_df.loc[i,"Bedarf Trinkwarmwasser"]/(dhw_df.loc[i,"Bedarf Trinkwarmwasser"] + heat_df.loc[i,"Bedarf Raumwaerme"])
        lambda2 = heat_df.loc[i,"Bedarf Raumwaerme"]/(dhw_df.loc[i,"Bedarf Trinkwarmwasser"] + heat_df.loc[i,"Bedarf Raumwaerme"])
        cop = lambda2 * heat_df.loc[i,"COP (B10/W35)"] + lambda1 * dhw_df.loc[i,"COP (B10/W55)"]
        cop_series[f"House_{i}"] = cop

    # empty dataframe
    df_power_el = pd.DataFrame(index=df_sim.index, columns=[f"House_{i}" for i in range(df_power_thermal.shape[1])])
    
    # calculate thermal power
    for i in range(df_power_thermal.shape[1]):
        p_el = df_power_thermal.loc[:, f"House_{i}__power_thermal"] / cop_series[f"House_{i}"]
        df_power_el[f"House_{i}"] = p_el

    verrechnungswirkarbeit = df_power_el.sum(axis=1).sum() / 6
    verrechnungsleistung = df_power_el.sum(axis=1).max()

    benutzungsstunden = verrechnungswirkarbeit/verrechnungsleistung
    print(f"###### {disp} ######")
    print(f"Bh: {benutzungsstunden}")
    print(f"Maximum: {verrechnungsleistung}")
    print(f"Verrechnungswirkarbeit: {verrechnungswirkarbeit}\n\n")