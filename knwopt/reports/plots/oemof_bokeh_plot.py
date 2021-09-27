import os
import pathlib

from bokeh.io import export_png
from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
import pandas as pd


# path to csv file or to directory containing csv files,
# default: /KNW-OPT/knwopt/data/oemof_results
CSV_PATH = os.path.join(os.getcwd(), "knwopt", "data", "oemof_results")

# target directory to save plot as html file
HTML_DIR = os.path.join(os.getcwd(), "knwopt", "reports", "plots")

# how thermal assists are approximately named. E.g. if you assists are named Assth-1, Assth_busth1, ...
# then ASSIST_LABEL = "Assth" (ASSIST_LABEL should be always in your assist names)
ASSIST_LABEL = "Assth"

# plot ntp output with rolling mean
PLOT_NTP = True
# labels of NTPel is/are like (explanation see ASSIST_LABEL)
NTP_LABEL = "pubgel"

# plot hepu output with rolling mean and amount of examplary
# hepus stated in `AMOUNT_HEPUS`
PLOT_HEPUS = False
AMOUNT_HEPUS = 5
# labels of hepus are like (explanation see ASSIST_LABEL)
HEPUS_LABEL = "HePu"

def plot_ntp(csv_file: str, plot_filename: str):
    """plots `NTP_LABEL` and thermal assist `ASSIST_LABEL` output

    Parameters
    ----------
    csv_file : str
        path to csv file with oemof data
    plot_filename : str
        path to target html bokeh plot
    """
    # load data
    df = pd.read_csv(csv_file, index_col=0)
    try:
        df.index = pd.to_datetime(df.index)
    except:
        df = df.transpose()
        index = [int(idx) * 10**6 for idx in df.index]
        df.index = pd.DatetimeIndex(index)

    # get only NTP data
    ntp_el_power = df.filter(like=NTP_LABEL).filter(like="P_el_plus")
    #ntp_el_power.columns = ["Ntp P_el_minus"]

    # get assist data
    ass_th = df.filter(like=ASSIST_LABEL).filter(like="P_th_plus").sum(1)

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
        list(ntp_el_power[list(ntp_el_power.columns)[0]]),
        line_width=2,
        color="#008B29",
        legend_label="Elektrischer Netzbezug"
    )

    """# plot rolling mean
    ntp_fig.step(
        df.index,
        rolling_mean,
        line_width=2,
        color="#2f2f2f",
        legend_label="Rolling Mean"
    )"""

    # plot assists if exists
    if not ass_th.empty:
        ntp_fig.step(
            df.index,
            list(ass_th),
            line_width=2,
            color="#e4932c",
            legend_label="Thermaler Bezug"
        )

    # allow to hide lines
    ntp_fig.legend.click_policy = "hide"
    ntp_fig.legend.location = "top_center"

    # save as html file
    output_file(plot_filename + ".html", title="Systemanalyse: Flexibilität")
    save(ntp_fig, plot_filename + ".html")
    export_png(ntp_fig, filename=plot_filename + ".png")


def plot_hepus(csv_file: str, plot_filename: str):
    """plots aggregated output of all hepus `HEPUS_LABEL`.
    Also examplary hepus are ploted as stated in `AMOUNT_HOUSES`

    Parameters
    ----------
    csv_file : str
        path to csv file with oemof data
    plot_filename : str
        path to target html bokeh plot
    """
    # load data
    df = pd.read_csv(csv_file, index_col=0)
    try:
        df.index = pd.to_datetime(df.index)
    except:
        df = df.transpose()
        index = [int(idx) * 10**6 for idx in df.index]
        df.index = pd.DatetimeIndex(index)

    # get hepu thermal outputs
    df_hepu_power_thermal = df.filter(like='P_th_plus', axis=1).filter(like=HEPUS_LABEL, axis=1)
    df_hepu_power_thermal.columns = [
        c.replace("_P_th_plus", "").replace("P_th_plus_", "") for c in df_hepu_power_thermal.columns
    ]

    # get assist data
    ass_th = df.filter(like=ASSIST_LABEL).filter(like="P_th_plus").sum(1)

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
    """heatpumps_fig.step(
        df.index,
        rolling_mean,
        line_width=2,
        color="#2f2f2f",
        legend_label="Rolling Mean"
    )"""

    # get color palette for each house
    houses_colors = viridis(AMOUNT_HEPUS)

    # plot power of each house
    for i in range(AMOUNT_HEPUS):
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

    # plot assists if exists
    if not ass_th.empty:
        heatpumps_fig.step(
            df.index,
            ass_th,
            line_width=2,
            color="#e4932c",
            legend_label="Thermaler Bezug"
        )

    # allow to hide lines
    heatpumps_fig.legend.click_policy = "hide"
    heatpumps_fig.legend.location = "top_center"

    # save as html file
    output_file(plot_filename + ".html", title="Systemanalyse: Flexibilität")
    save(heatpumps_fig, plot_filename + ".html")
    export_png(heatpumps_fig, filename=plot_filename + ".png")

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
            try:
                csv_name = pathlib.Path(file).stem
                csv_path = os.path.join(CSV_PATH, file)
                if PLOT_NTP:
                    html_file = os.path.join(HTML_DIR, f"ntp_oemof_{csv_name}")
                    plot_ntp(csv_path, html_file)
                if PLOT_HEPUS:
                    html_file = os.path.join(HTML_DIR, f"hepus_oemof_{csv_name}")
                    plot_hepus(csv_path, html_file)
            except:
                print(f"Could not plot oemof results from {file}. (Probably because it is not oemof result)")
