# Bokeh Plot Skripte

## Inhaltsverzeichnis

<!-- vscode-markdown-toc -->
1. [Dispatcher Bokeh Plot Skript](#DispatcherBokehPlotSkript)
	
	1.1. [Daten](#Daten)
	
	1.2. [Bemerkung](#Bemerkung)
2. [OEMOF Bokeh Plot Skript](#OEMOFBokehPlotSkript)
	
	2.1. [Daten](#Daten-1)
	
	2.2. [NTP Plot](#NTPPlot__)
	
	2.3. [Hepu Plot](#HepuPlot__)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

##  1. <a name='DispatcherBokehPlotSkript'></a>Dispatcher Bokeh Plot Skript

Das Skript für den Dispatcher Bokeh Plot oder zum Dispatch Rolling Mean Plot ist unter [dispatcher_bokeh_plot.py](https://github.com/ConsolinnoEnergy/KNW-Opt/blob/main/knwopt/reports/plots/dispatcher_bokeh_plot.py) zu finden.

Dieser Plot beeinhaltet folgende Daten:
- aggregierte Wärme aller Wärmepumpen
- Rolling Mean dieser aggregierten Wärme
- Lastprofile von exemplarischen Wärmepumpen

Es müssen 3 Werte gesetzt, bzw. angepasst werden:
- `CSV_PATH`: Pfad zur CSV Datei oder zum Ordner, der geeignete CSV Dateien enthält. Diese bilden die Datenbasis zur Erzeugung der Plots.
  
  Default: `/KNW-OPT`
- `HTML_DIR`: Pfad zum Ordner, in dem die HTML Bokeh Plots gespeichert werden. 
  
  Default: `/KNW-OPT/knwopt/reports/plots`
- `AMOUNT_HOUSES`: Anzahl an Wärmepumpen, deren Lastprofil im Plot erscheinen werden.
  
  Default: `5`

Sind diese richtig gesetzt, kann das Skript einfach ausgeführt werden.

###  1.1. <a name='Daten'></a>Daten

Die Daten, die für diesen Plot benötigt werden, werden durch das Skript [simulation.py](https://github.com/ConsolinnoEnergy/KNW-Opt/blob/main/knwopt/simulations/variance_peak_analysis/simulation.py) erzeugt. Das Skript liegt in dem Ordner [/KNW-OPT/simulations/variance_peak_analysis](https://github.com/ConsolinnoEnergy/KNW-Opt/blob/main/knwopt/simulations/variance_peak_analysis).

Dieses Skript startet die Simulation mit 5, 25 und 125 Häusern, im Dispatch Modus und ohne.

Um die Simulationen nun abzuspeichern, muss die Variable `CSV_PATH` gesetzt werden. Dort wird der Ordner angegeben, in dem die Simulationen als CSV Dateien abgespeichert werden.

###  1.2. <a name='Bemerkung'></a>Bemerkung

Die Generierung der Plots aus einer CSV Datei unterliegen folgendem Schema:

`hepu_simulation.csv` --> `plot_hepu_simulation.html`

Das kann natürlich im `if __name__ == "__main__":` Block angepasst werden.

##  2. <a name='OEMOFBokehPlotSkript'></a>OEMOF Bokeh Plot Skript

Das Skript für den OEMOF Bokeh Plot oder zum Systemanalyse: Flexibilität Plot ist unter [oemof_bokeh_plot.py](https://github.com/ConsolinnoEnergy/KNW-Opt/blob/main/knwopt/reports/plots/oemof_bokeh_plot.py)

Hierbei können zwei verschiedene Plotarten erstellt werden, s.u.

Es müssen 5 Werte gesetzt, bzw. angepasst werden:

- `CSV_PATH`: Pfad zur CSV Datei oder zum Ordner, der geeignete CSV Dateien enthält. Diese bilden die Datenbasis zur Erzeugung der Plots.
  
  Default: `/KNW-OPT/knwopt/data/oemof_results`
- `HTML_DIR`: Pfad zum Ordner, in dem die HTML Bokeh Plots gespeichert werden. 
  
  Default: `/KNW-OPT/knwopt/reports/plots`
- `PLOT_NTP`: Gibt an, ob __NTP Plot__ erstellt werden soll.

  Default: `True`
- `PLOT_HEPUS`: Gibt an, ob __Hepu Plot__ erstellt werden soll.

  Default: `False`
- `AMOUNT_HEPUS`: Anzahl an Wärmepumpen, deren Lastprofil im Plot erscheinen werden.
  
  Default: `5`

Sind diese richtig gesetzt, kann das Skript einfach ausgeführt werden (Beachte Sektion __Daten__!).


###  2.1. <a name='Daten-1'></a>Daten

Die ursprünglichen Daten sind im Gitlab Repository [Energy System Analysis Projects](https://gitlab.consolinno-it.de/flexa/energy-system-analysis/energy-system-analysis-projects) unter [KNW-Opt/oemof/results](https://gitlab.consolinno-it.de/flexa/energy-system-analysis/energy-system-analysis-projects/-/tree/master/KNW-Opt/oemof/results) zu finden.

Die wichtigen Dateien wurden in dieses Projekt kopiert, zu finden hier: [KNW-Opt/knwopt/data/oemof_results](https://github.com/ConsolinnoEnergy/KNW-Opt/tree/main/knwopt/data/oemof_results).

Auf Grund der Dateigrößeneinschränkung von Github __fehlen 2 CSV Dateien__ in diesem Projekt:
- [solution_1_day_steps_hepus_150.csv](https://gitlab.consolinno-it.de/flexa/energy-system-analysis/energy-system-analysis-projects/-/blob/master/KNW-Opt/oemof/results/solution_1_day_steps_hepus_150.csv)
- [solution_1_day_steps_hepus_200.csv](https://gitlab.consolinno-it.de/flexa/energy-system-analysis/energy-system-analysis-projects/-/blob/master/KNW-Opt/oemof/results/solution_1_day_steps_hepus_200.csv)

Diese Dateien bitte extra runterladen. Insgesamt sind es also __8__ CSV Dateien.

###  2.2. <a name='NTPPlot__'></a>__NTP Plot__

Dieser Plot beeinhaltet folgende Daten:
- Netzbezug aus `ntp_el-1`. Dieser versorgt alle Wärmepumpen und ist somit repräsentativ für die erzeugte Wärme.
- Rolling Mean des Netzbezuges

####  2.2.1. Bemerkung

Die Generierung der Plots aus einer CSV Datei unterliegen folgendem Schema:

`hepu_simulation.csv` --> `ntp_oemof_hepu_simulation.html`

Das kann natürlich im `if __name__ == "__main__":` Block angepasst werden.

###  2.3. <a name='HepuPlot__'></a>__Hepu Plot__

Dieser Plot beeinhaltet folgende Daten:

- aggregierte Wärme aller Wärmepumpen
- Rolling Mean dieser aggregierten Wärme
- Lastprofile von exemplarischen Wärmepumpen

####  2.3.1. Bemerkung

Die Generierung der Plots aus einer CSV Datei unterliegen folgendem Schema:

`hepu_simulation.csv` --> `hepus_oemof_hepu_simulation.html`

Das kann natürlich im `if __name__ == "__main__":` Block angepasst werden.
