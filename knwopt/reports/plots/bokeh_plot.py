import os
import pathlib

from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
import pandas as pd


# path to csv file or to directory containing csv files, default: /KNW-OPT
CSV_PATH = os.getcwd()

# target directory to save plot as html file
HTML_DIR = os.path.join(os.getcwd(), "knwopt", "reports", "plots")

# how many houses should be plotted (up to 256)
AMOUNT_HOUSES = 5

def create_html_plot(csv_file: str, html_file: str):
    # load data
    df = pd.read_csv(csv_file, index_col=0)

    # get only thermal data
    df_power_thermal = df.filter(like='power_thermal', axis=1)
    df_power_thermal.columns = [c.replace("__power_thermal", "") for c in df_power_thermal.columns]

    # aggregate power per timestep
    power_per_timestep = df_power_thermal.sum(1)

    # calculate rolling mean of aggregated power
    rolling_mean = df_power_thermal.sum(1).rolling(window=24).mean()

    # declare bokeh figure
    heatpumps_fig = figure(
        title=f"Heatpumps KNW-Opt",
        sizing_mode="stretch_width",
        background_fill_color="#fafafa",
        x_axis_type="datetime",
        y_axis_label="Thermal Power in kW",
        tools="wheel_zoom, box_zoom, reset, pan"
    )

    # plot aggregated power per timestep
    heatpumps_fig.step(
        df.index,
        power_per_timestep,
        line_width=2,
        color="#008B29",
        legend_label="Aggregated Heat"
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
    houses_colors = viridis(AMOUNT_HOUSES)

    # plot power of each house
    for i in range(AMOUNT_HOUSES):
        series = df_power_thermal.iloc[:, i]
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
    output_file(html_file, title="Simulation Analysis")
    save(heatpumps_fig, html_file)
    

if __name__ == "__main__":
    if os.path.isfile(CSV_PATH):
        csv_file = pathlib.Path(CSV_PATH).stem
        html_file = os.path.join(HTML_DIR, f"plot_{csv_file}.html")
        create_html_plot(CSV_PATH, html_file)
    else:
        csv_files = [file for file in os.listdir(CSV_PATH) if file.endswith(".csv")]
        for file in csv_files:
            csv_file = pathlib.Path(file).stem
            html_file = os.path.join(HTML_DIR, f"plot_{csv_file}.html")
            create_html_plot(file, html_file)
