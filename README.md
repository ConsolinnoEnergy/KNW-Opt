# KNW-Opt

Centralized optimization strategy for a swarm of heat pumps.
The aim is to implement a peak shaving strategy.

To test the strategy houses with heatpumps are implemented as agents a la openai/gym api ("reset" the environment, move one discrete simulation step forward by a "step" method, which takes actions (heating = 0/1) as parameter). These house environments may expose their electric potential and availability to the outside.

These house environmets are then connected in a swarm environment. This swarm environment requests the potentials of the houses and determines an expected power level (the base power the system needs). the swarm environment dispatches then the available potentials in an optimal manner, such that the resulting aggregated power of the heatpumps matches the expected power level best. 

