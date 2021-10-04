"""berechnet Größen, die zur Kostenanalyse benötigt werden.
Z.B. mit Hilfe von
https://www.bayernwerk-netz.de/content/dam/revu-global/bayernwerk-netz/files/netz/netzzugang/netzentgeltestrom/20201006-bayernwerk-preisblaetter-strom-2021gesamt.pdf
"""

import os

import pandas as pd

# path to oemof results
simulation_path = os.path.join(os.getcwd(), "knwopt", "data", "oemof_results", "solution_MAGGIE_1_day_steps_hepus_49.csv")

df_sim = pd.read_csv(simulation_path)

# get all electrical output = gets electric output from public grid for heatpumps
df_power_el = df_sim.filter(like="P_el_plus")

verrechnungswirkarbeit = df_power_el.sum(axis=1).sum()
verrechnungsleistung = df_power_el.sum(axis=1).max()

vollbenutzungsstunden = verrechnungswirkarbeit/verrechnungsleistung

print(f"Vollbenutzungsstunden: {vollbenutzungsstunden}")
print(f"Maximum: {verrechnungsleistung}")
print(f"Verrechnungswirkarbeit: {verrechnungswirkarbeit}\n\n")