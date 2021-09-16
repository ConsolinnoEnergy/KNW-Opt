import os
import pathlib

from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
import pandas as pd


# path to csv file or to directory containing csv files,
# default: /KNW-OPT
CSV_PATH = os.path.join(os.getcwd(), "knwopt", "data", "oemof_results")

# target directory to save plot as html file
HTML_DIR = os.path.join(os.getcwd(), "knwopt", "reports", "plots")

# plot ntp output with rolling mean
PLOT_NTP = True

# plot hepu output with rolling mean and amount of examplary
# hepus stated in `AMOUNT_HEPUS`
PLOT_HEPUS = True
AMOUNT_HEPUS = 5

def plot_ntp(csv_file: str, html_file: str):
    """plots ntp_el-1 output and its rolling mean in a
    window of 24 h.

    Parameters
    ----------
    csv_file : str
        path to csv file with oemof data
    html_file : str
        path to target html bokeh plot
    """
    # load data
    df = pd.read_csv(csv_file, index_col=0)
    df.index = pd.to_datetime(df.index)

    # get only ntp_el-1 data
    ntp_el_power = df.loc[:, "ntp_el-1_P_el_plus"]
    #ntp_el_power.columns = ["Ntp P_el_minus"]

    # calculate rolling mean of aggregated power
    rolling_mean = ntp_el_power.rolling(window=24).mean()

    # declare bokeh figure
    ntp_fig = figure(
        title="Systemanalyse: Flexibilität",
        sizing_mode="stretch_width",
        background_fill_color="#fafafa",
        x_axis_type="datetime",
        y_axis_label="Leistung in kW",
        tools="wheel_zoom, box_zoom, reset, pan"
    )

    # plot aggregated power per timestep
    ntp_fig.step(
        df.index,
        ntp_el_power,
        line_width=2,
        color="#008B29",
        legend_label="Elektrischer Netzbezug"
    )

    # plot rolling mean
    ntp_fig.step(
        df.index,
        rolling_mean,
        line_width=2,
        color="#2f2f2f",
        legend_label="Rolling Mean"
    )

    # allow to hide lines
    ntp_fig.legend.click_policy="hide"

    # save as html file
    output_file(html_file, title="Systemanalyse: Flexibilität")
    save(ntp_fig, html_file)

def plot_hepus(csv_file: str, html_file: str):
    """plots aggregated output of all hepus and its rolling mean in a
    window of 24 h. Also examplary hepus are ploted as stated in `AMOUNT_HOUSES`

    Parameters
    ----------
    csv_file : str
        path to csv file with oemof data
    html_file : str
        path to target html bokeh plot
    """
    # load data
    df = pd.read_csv(csv_file, index_col=0)
    df.index = pd.to_datetime(df.index)

    # get hepu thermal outputs
    df_hepu_power_thermal = df.filter(like='P_th_plus', axis=1).filter(like='hepu', axis=1)
    df_hepu_power_thermal.columns = [c.replace("_P_th_plus", "") for c in df_hepu_power_thermal.columns]

    # aggregate power per timestep
    hepu_power_thermal_per_timestep = df_hepu_power_thermal.sum(1)

    # calculate rolling mean of aggregated power
    rolling_mean = df_hepu_power_thermal.sum(1).rolling(window=24).mean()

    # declare bokeh figure
    heatpumps_fig = figure(
        title=f"Systemanalyse: Flexibilität",
        sizing_mode="stretch_width",
        background_fill_color="#fafafa",
        x_axis_type="datetime",
        y_axis_label="Leistung in kW",
        tools="wheel_zoom, box_zoom, reset, pan"
    )

    # plot aggregated power per timestep
    heatpumps_fig.step(
        df.index,
        hepu_power_thermal_per_timestep,
        line_width=2,
        color="#008B29",
        legend_label="Aggregierte Wärme"
    )

    # plot rolling mean
    heatpumps_fig.step(
        df.index,
        rolling_mean,
        line_width=2,
        color="#2f2f2f",
        legend_label="Rolling Mean"
    )

    # get color palette for each house
    houses_colors = viridis(5)

    # plot power of each house
    for i in range(5):
        series = df_hepu_power_thermal.iloc[:, i]
        source = {"index": df.index, "value": series}
        heatpumps_fig.step(
            x="index",
            y="value",
            source=source,
            line_width=2,
            color=houses_colors[i],
            legend_label=series.name
        )

    # allow to hide lines
    heatpumps_fig.legend.click_policy="hide"

    # save as html file
    output_file(html_file, title="Systemanalyse: Flexibilität")
    save(heatpumps_fig, html_file)

if __name__ == "__main__":
    if os.path.isfile(CSV_PATH):
        csv_name = pathlib.Path(CSV_PATH).stem
        if PLOT_NTP:
            html_file = os.path.join(HTML_DIR, f"ntp_oemof_{csv_name}.html")
            plot_ntp(CSV_PATH, html_file)
        if PLOT_HEPUS:
            html_file = os.path.join(HTML_DIR, f"hepus_oemof_{csv_name}.html")
            plot_hepus(CSV_PATH, html_file)
    else:
        csv_files = [file for file in os.listdir(CSV_PATH) if file.endswith(".csv")]
        for file in csv_files:
            csv_name = pathlib.Path(file).stem
            csv_path = os.path.join(CSV_PATH, file)
            if PLOT_NTP:
                html_file = os.path.join(HTML_DIR, f"ntp_oemof_{csv_name}.html")
                plot_ntp(csv_path, html_file)
            if PLOT_HEPUS:
                html_file = os.path.join(HTML_DIR, f"hepus_oemof_{csv_name}.html")
                plot_hepus(csv_path, html_file)
