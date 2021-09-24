import os
import pathlib

from bokeh.io import export_png
from bokeh.io.export import get_screenshot_as_png
from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
import pandas as pd


# path to csv file or to directory containing csv files
CSV_PATH = os.path.join(os.getcwd(), "knwopt", "data", "jay_simulation_dispatch_60min_49x2houses.csv")

# target directory to save plot as html file
HTML_DIR = os.path.join(os.getcwd(), "knwopt", "reports", "plots")

# how many houses should be plotted (up to 256)
AMOUNT_HOUSES = 5

def create_html_plot(csv_file: str, plot_filename: str):
    """plots aggregated output of all hepus and its rolling mean in a
    window of 24 h. Also examplary hepus are ploted as specified in `AMOUNT_HOUSES`

    Parameters
    ----------
    csv_file : str
        path to csv file with oemof data
    plot_filename : str
        path to target bokeh plot
    """
    # load data
    df = pd.read_csv(csv_file, index_col=0)
    index = pd.DatetimeIndex(pd.date_range(start="2021-01-01", freq="60Min", periods=len(df)))
    df.index = pd.to_datetime(index)

    # get only thermal data
    df_power_thermal = df.filter(like='power_thermal', axis=1)
    df_power_thermal.columns = [c.replace("__power_thermal", "") for c in df_power_thermal.columns]

    # aggregate power per timestep
    power_per_timestep = df_power_thermal.sum(1)

    # calculate rolling mean of aggregated power
    rolling_mean = df_power_thermal.sum(1).rolling(window=24).mean()

    # declare bokeh figure
    heatpumps_fig = figure(
        title=f"Dispatcher Rolling Mean",
        sizing_mode="stretch_width",
        background_fill_color="#fafafa",
        x_axis_type="datetime",
        y_axis_label="Leistung in kW",
        tools="wheel_zoom, box_zoom, reset, pan"
    )

    # plot aggregated power per timestep
    heatpumps_fig.step(
        df.index,
        power_per_timestep,
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
    heatpumps_fig.legend.click_policy = "hide"
    heatpumps_fig.legend.location = "top_center"

    # save as html and png file
    output_file(plot_filename + ".html", title="Dispatcher Rolling Mean")
    save(heatpumps_fig, plot_filename + ".html")
    export_png(heatpumps_fig, filename=plot_filename + ".png")
    

if __name__ == "__main__":
    if os.path.isfile(CSV_PATH):
        csv_name = pathlib.Path(CSV_PATH).stem
        plot_filename = os.path.join(HTML_DIR, f"plot_{csv_name}")
        create_html_plot(CSV_PATH, plot_filename)
    else:
        csv_files = [file for file in os.listdir(CSV_PATH) if file.endswith(".csv")]
        for file in csv_files:
            try:
                csv_name = pathlib.Path(file).stem
                plot_filename = os.path.join(HTML_DIR, f"plot_{csv_name}")
                csv_path = os.path.join(CSV_PATH, file)
                create_html_plot(csv_path, plot_filename)
            except:
                print(f"Could not plot dispatcher results from {file}. (Probably because it is not dispatcher result)")