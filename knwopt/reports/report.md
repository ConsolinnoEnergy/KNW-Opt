# Peak Vermeidung durch Dispatching auf Rolling Mean

**Abstract**

In KNW-Opt sollen unterschiedliche Optimierungsmaßnahmen eines kalten Nahwärmenetzes untersucht werden.
Eine Maßnahme soll die elektrische Lastspitzenvermeidung des Wärmepumpenschwarms sein. Hierbei sollte möglichst
das gleichzeitige Anlaufen von vielen Wärmepumpenvermieden werden. Da die Wärmepumpen über Warmwasserspeicher verfügen, steht hier eine energetische Flexibilität zur Verfügung, welche eine gezielte Koordination der Wärmepumpen ermöglichen sollte, um Lastspitzen zu vermeiden.
### Lastspitzen im KNW-Netz glätten

Eines der erklärten Ziele ist das Glätten elektrischer Lastspitzen im kalten Nahwäremenetz. Doch was soll Ausglätten bedeuten?
Ein möglichst glatter Betrieb der Wärmepumpen über einen diskreten Zeithorizont $T$ kann durch folgende *Kostenfunktion* beschrieben werden:

$$\min_{(x_{up},x_{down})} \sum_{t \in T} x_{up}(t) + x_{down}(t),$$

so dass folgende fünf Randbedingungen gelten:
 
$$P_{WP}(t) = \sum_{wp \in WP} P_{wp}(t),$$ 
$$mean(P_{WP}) = \frac{1}{|T|}\sum_{t \in T}P_{WP}(t),$$
$$P_{WP}(t) = mean(P_{WP}) + x_{up}(t) - x_{down}(t),$$
$$x_{up}(t), x_{down}(t)\geq 0$$
$$ P_{wp}(t) \text{ muss zu jedem Zeitpunkt }$$

Hierbei ist $WP$ die Menge aller Wärmepumpen und $P_{wp}$ die (elektrische oder thermische) Leistung der Wärmepumpe $wp$. Mit anderen Worten, die Minimierungsaufgabe strebt den Baselastagang bei dem aggregierten Lastgang aller Wärmepumpen an:
Ist das Minimum $0$, so gilt nach (4) $x_{up}(t)=x_{down}(t)=0$ und dann mit (3) $P_{WP}(t) = mean(P_{WP})$ konstant.







