# Peak Vermeidung durch Dispatching auf Rolling Mean

**Abstract**

In KNW-Opt sollen unterschiedliche Optimierungsmaßnahmen eines kalten Nahwärmenetzes untersucht werden.
Eine Maßnahme soll die elektrische Lastspitzenvermeidung des Wärmepumpenschwarms sein. Hierbei sollte möglichst
das gleichzeitige Anlaufen von vielen Wärmepumpenvermieden werden. Da die Wärmepumpen über Warmwasserspeicher verfügen, steht hier eine energetische Flexibilität zur Verfügung, welche eine gezielte Koordination der Wärmepumpen ermöglichen sollte, um Lastspitzen zu vermeiden.

## Lastspitzen im KNW-Netz glätten

Eines der erklärten Ziele ist das Glätten elektrischer Lastspitzen im kalten Nahwäremenetz. Doch was soll Ausglätten bedeuten?
Ein möglichst glatter Betrieb der Wärmepumpen über einen diskreten Zeithorizont $T$ kann durch folgende *Kostenfunktion* beschrieben werden:

$$\min_{(x_{up},x_{down})} \sum_{t \in T} x_{up}(t) + x_{down}(t),$$

so dass folgende fünf Randbedingungen gelten:
 
$$P_{WP}(t) = \sum_{wp \in WP} P_{wp}(t),$$ 
$$mean(P_{WP}) = \frac{1}{|T|}\sum_{t \in T}P_{WP}(t),$$
$$P_{WP}(t) = mean(P_{WP}) + x_{up}(t) - x_{down}(t),$$
$$x_{up}(t), x_{down}(t)\geq 0$$


Hierbei ist $WP$ die Menge aller Wärmepumpen und $P_{wp}$ die (elektrische oder thermische) Leistung der Wärmepumpe $wp$. Mit anderen Worten, die Minimierungsaufgabe strebt den Baselastagang bei dem aggregierten Lastgang aller Wärmepumpen an:
Ist das Minimum $0$, so gilt nach (4) $x_{up}(t)=x_{down}(t)=0$ und dann mit (3) $P_{WP}(t) = mean(P_{WP})$ konstant.
Desweiteren muss auch noch folgende Bedingung gelten:

$P_{wp}(t)$ muss zu jedem Zeitpunkt $t$ die Wärmelast des Hauses, welches zur Wärmepumpe $wp$ gehört decken.

Warum ist das nun eine Lösung unseres Problems Lastspitzen zu vermeiden?

Wenn man die benötigte Energie als eine feste Zustandsgröße ansieht, so ist der Baselastgang derjenige Lastgang, welcher die geringste Leistungsspitzen aufweist. Denn jeder (stetige) Lastgang, welcher zu einer Zeit einen Leistungswert geringer als die Baselast aufweist, muss um die selbe Energie zu liefern zu einem anderen Zeitpunkt eine Leistung größer als die Baselast aufweisen. Und das ist gerade der Punkt: Der angestrebte Mittelwert bildet die Energie des Systems ab, das heißt unsere eigentliche Zielgröße ist die Baselast der benötigten Energie des Systems.

## Flexibilitätsbetrachtungen im KNW-Netz

Zunächst soll eine Systemanalyse des KNW-Netz durch geführt werden. Diese Systemanalyse soll aufzeigen, in wie weit theoretisch eine Annäherung an den Baselastgang möglich ist. Im wesentlichen untersucht die Systemanalyse die von den Warmwasserspeichern zur Verfügung gestellte Flexibilität: Ist theoretisch eine Lastgangverschiebung der Wärmepumpen über einen Tag möglich, so dass ihr Summenlastgang dem Baselastgang entspricht?

Für die Systemanalyse modellieren wir das KNW-Netz als lineares Programm, welches obiges Optimierungsproblem formuliert, also diejenigen Lastgänge der Wärmepumpen sucht, so dass der Summenlastgang möglichst Nahe am Base liegen. Die Warmwasserspeicher werden also durch lineare Gleichungen modelliert, die Information der thermischen Verbräuche der Häuser stehen dem Optimierer in perfekter Voraussicht zur Verfügung und die Wärmepumpen können zwischen 0 und 100 Prozent moduliert werden. Man beachte, dass dies noch keine Steuerungsstartegie liefert, welche diese Lastgänge in Laufzeit generieren könnte!  

Die Ergebins Lastgänge sehen wir hier:



Wir sehen also, dass theoretisch jeden Tag eine Lastverschiebung auf den Base möglich ist, auch schon bei geringen Portfoliogrößen.
Desweiteren sehen wir, dass diese Analyse in der Anzahl der Wärmepumpen Rechenzeit technisch linear skaliert:  

## Algorithmische Flexibilisierung im KNW-Netz

Da die Analysen ergeben haben, dass eine Flexibilisierung auf den Base theoretische möglich ist, geht es in einem nächsten Schritt darum sich diesem Optimierungsziel algorithmisch in Laufzeit anzunähern. Unsere Analyse zeigt, dass theoretisch zu jedem Zeitpunkt eine Lastverteilung der Wärmepumpen auf den Base der benötigten Tagesenergie möglich ist. Das bedeutet, dass wir in Laufzeit zunächst dies benötigte Energie für 24 Stunden schätzen müssen. Diese Schätzung kann im einfachsten Fall über einen rollierenden Mittelwert der letzten 24 Stunden geschehen und liefert uns die *erwartete Baseleistung*. 

Alle Wärmepumpen sind mit Warmwasserspeicher ausgestattet und so haben sie eine gewisse Flexibilität in ihrem Betrieb. Genauer können wir die Flexibilität der Wärmepumpen über ihr *Potential* beschrieben. Das *Potential* ist definiert durch ihre maximale Leistung, momentane Leistung und der *Verfügbarkeit*. Eine Wärmepumpe ist *verfügbar*, wenn sich die Temperaturen im Warmwasserspeicher in enem Wohlfühlbereich befinden, etwa die mittlere Temperatur ist zwischen $T_{min}$ und  $T_{max}$, und die Wärmepumpe hat eine minimale Lauf- oder Standzeit durchlaufen, etwa eine Stunde. 

Zu jedem Zeitpunkt kann man nun die erwartete Baseleistung berechnen und das Potential aller Wärmepumpen abfragen. Die Leistung der nicht verfügbaren Wärmepumpen zieht man von der Baseleistung ab und die Restleistung verteilt man dann auf die verfügbaren Wärmepumpen. 

Dieses Verfahren nennen wir *Dispatching auf den Rolling Mean*.


## Vorteile des Algorithmischen Modells

Der Algorithmus erstellt nicht für jede Wärmepumpe einen Einsatzplan, so dass der aggregierte Plan einen möglichst glatten Lastgang liefert, sondern er schätzt den idealen glatten Lastgang, den Base des Tages, und nutzt dann das ihm statistisch zur Verfügung stehende Potential um sich diesem Base anzunähern, bzw. die Leistung der Wärmepumpen so zu verteilen, dass ihre aggregierte Leistung diesem Base möglichst nahe kommt.

Der Vorteil gegenüber der indivuellen Einsatzplanung ist vor allem, dass keine Energien von Häusern und keine Energien in From von hochaufgelösten Zeitreihen Forecasts erstellt werden müssen. Dies ist wesentlich schwieriger und mit einem höheren Fehlerrisiko verbunden. Der Forecast der aggregierten Tagesenergie ist robuster und erfolgsversprechender, da statistische Protfolioeffekte vorhanden sind.

Desweiteren ist algorithmishe Modell sparsam mit Daten und Berechnungen. Die Wärmepumpen sind als selbstständige Agenten modelliert, welche ihre individuellen Betriebsconstraints beliebig realisieren können. Dadurch ist die Optimierung des Wärmepumpenbetriebs im Sinnen der Wärmelieferung in den Häusern ermöglicht, ohne die individuellen Betriebsconstraints in der globalen Optimierung berücksichtigen zu müssen.

## Simulation des Algorithmus 'Dispatching auf Rolling Mean' und Analyse des Algorithmus

Um den oben beschriebenen Algorithmus zu testen und zu überprüfen, ob er unser Ziel der Lastspitzenvermeidung realisiert wurde eine Simualtionsumgebung entwickelt. Sie orientiert sich an Agenten basierten Simuationen, realisert aber Häuser und Leitzentrale nicht als selbstständige Software-Agenten/Programme.

Es handelt sich um eine Simulation mit 98 Häusern: jeweils 49 Häuser mit Trinkwarmwasserbedarf und Raumwärmebedarf. Die Wärmepumpen haben eine Leistung von 1 - 5 kW und einen mittleren COP von 4.9 (Trinkwarmwasser) und 6.9 (Raumwärme). Der thermische Jahresenergiebedarf der Häuser ist 115 500 kWh (Trinkwarmwasser) und 173 250 kWh (Raumwärme).

Die Ergebnisse einer klassischen Hysterese-Regelung sehen wir hier

![](./plots/plot_jay_simulation_not_dispatch_60min_49x2houses.png)

Mittlere aggregierte Leistung: 194.4 kW

Standardabweichung der aggregierten Leistung: 170.7 kW

Maximum der aggregierten Leistung: 783.1 kW

Minimum der aggregierten Leistung: 0 kW

90%-Qunatil der Aggregierten Leistung: 469.1 kW



Die Ergebnisse Refelung mit Dispatching auf den rolling Mean sehen wir hier

![](./plots/plot_jay_simulation_dispatch_60min_49x2houses.png)

Mittlere aggregierte Leistung: 204.7 kW

Standardabweichung der aggregierten Leistung: 149.3 kW

Maximum der aggregierten Leistung: 819.3 kW

Minimum der aggregierten Leistung: 30.2 kW

90%-Qunatil der Aggregierten Leistung: 433.7 kW

## Performance des Dispatching auf den Rolling Mean

Es wurde eine Performanzanalyse des Dispatching algorithmus durchgeführt:


Prozessor		: AMD Ryzen 7 4700U with Radeon Graphics

Hauptspeicher		: 15657MB 


|number_of_houses|computation_time|steps|
|----------------|----------------|-----|
|5|0.374|24|
|25|0.607|24|
|125|1.416|24|
|625|5.648|24|
|3125|28.093|24|
|15625|141.250|24|

Man sieht, dass der Algorithmus für sehr große Wärmepumpenschwärme geeignet ist. 

## Fazit Simulation

Die Simulationsergebnisse zeigen deutlich, dass durch Dispatching auf den Rolling Mean das Ziel der Peakvermeidung realisiert werden kann. Desweiteren stellt es eine Software technisch leicht umzusettende Lösung dar, welche gut in der Größe der Wärmepumpenschwärme skaliert.