from copy import deepcopy
import os

import pandas as pd
import numpy as np

######################## MAKE SURE `epsilon_sd` AND THEREFORE `epsilon` MAKES SENSE ########################

# path to original data
CSV_PATH = os.path.join(os.getcwd(), "knwopt", "data", "Loadprofiles_MAGGIE.csv")

# how many houses should be generated additionally to original ones
ADD_HOUSES = 43

# frequency of timesteps in minutes
MINUTES_TIMESTEP = 10


def from_csv(csv_path: str, freq_mins: int) -> pd.DataFrame:
    """prepares df by setting a DatetimeIndex

    Parameters
    ----------
    csv_path : str
        path to original csv data
    freq_mins : int
        frequency of timesteps in minutes

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(CSV_PATH, delimiter=";", decimal=",")
    df.index = pd.DatetimeIndex(pd.date_range(start="2021-01-01", freq=f"{freq_mins}Min", periods=len(df)))
    return df

def generate_data_from_df(df: pd.DataFrame, columnslike: str, new_columnname: str) -> pd.DataFrame:
    """statistically generates data from `df`.

    Parameters
    ----------
    df : pd.DataFrame
        original data
    columnslike : str
        how do the columns of interest look like? E.g. they look like "HeatDemand"
    new_columnname : str
       the schema for column names of generated data, e.g. "u__HeatDemand"
    """
    df_data = df.filter(like=columnslike)

    existing_houses = df_data.shape[1]

    mean_dhw = df_data.mean(axis=1)
    sd_dwh = df_data.std(axis=1)

    # generate an epsilon with mean 0 which will be added to generated load profile
    # (if all existing houses have the same value at a timestep (--> deviaton=0), then the epsilon will make
    # sure that the generated data does not look the same and varies at least a little bit)
    if not df_data.min().all():
        minimum = 0.00001
    else:
        minimum = df_data.min()
    
    raise Exception("Did you check if `epsilon` makes sense? If so, remove the exception.")
    
    epsilon_sd = (np.array(abs(minimum)) / (np.array(abs(df_data.max()))) * 10).mean()
    epsilon = np.random.normal(loc=0, scale=epsilon_sd, size=(ADD_HOUSES, len(df)))

    # generate new profiles with epsilon
    generated_profile_epsilon = np.random.normal(loc=mean_dhw, scale=sd_dwh, size=(ADD_HOUSES, len(df))) + epsilon

    # only positive profiles
    generated_profile = np.array(
        [np.maximum(np.zeros(shape=a.shape), a) for a in generated_profile_epsilon]
    )

    # norm profiles
    normed_profile = [
        generated_profile[i] / sum(generated_profile[i])
        for i in range(ADD_HOUSES)
    ]

    # save in dataframe with given `new_columnname` schema
    generated_df = pd.DataFrame(
        data={
            f"{new_columnname}{i + existing_houses + 1}": normed_profile[i]
            for i in range(ADD_HOUSES)
        },
        index=df.index
    )

    return generated_df

def to_csv(filename: str, original_df: pd.DataFrame, *args):
    """saves generated data to csv. In `args` is generated data

    Parameters
    ----------
    filename : str
        target csv file name
    original_df : pd.DataFrame
        original data
    """
    original_house_columns  = original_df.filter(like="House").columns

    original_houses_df = deepcopy(original_df)
    normed_original_houses_df = (
        original_houses_df.loc[:, original_house_columns] /
        original_houses_df.loc[:, original_house_columns].sum()
    )

    new_df = pd.concat([normed_original_houses_df, *args], axis=1)
    new_df.to_csv(filename)

if __name__ == "__main__":
    df = from_csv(CSV_PATH, MINUTES_TIMESTEP)
    generated_dhw_df = generate_data_from_df(df, "DHW", "u__DHW_House")
    generated_heat_df = generate_data_from_df(df, "HeatDemand", "u__HeatDemand_House")
    to_csv("TEST.csv", df, generated_dhw_df, generated_heat_df)
