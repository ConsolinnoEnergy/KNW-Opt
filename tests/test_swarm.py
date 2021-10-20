import unittest
from knwopt.swarm_agent import Swarm, House
import pandas as pd
import numpy as np

class SwarmTest(unittest.TestCase):

    def test_constructor(self):
        """test if the constructor and basic steps work
        """
        houses = []
        for i in range(3):
            houses.append(
                House(
                    load= pd.Series(
                        [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                        )
                    )
                )

        swarm=Swarm(houses)
        done = False
        while not done:
            state, reward, done, info = swarm.step()
            for house in swarm.houses:
                self.assertTrue(45 < house.T < 85)
        
    def test_potential(self):
        """test the call for potential
        """
        houses = []
        for i in range(3):
            houses.append(
                House(
                    load = pd.Series(
                        [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                        )
                    )
                )

        swarm=Swarm(houses)
        swarm.request_potential()
        d = {
            'House_0': {'max_power': 3.0, 'power': 0.0, 'available': True},
            'House_1': {'max_power': 3.0, 'power': 0.0, 'available': True},
            'House_2': {'max_power': 3.0, 'power': 0.0, 'available': True}
        }
        self.assertTrue(swarm.portfolio==d)

    def test_expected_power(self):
        """test the call for potential
        """
        houses = []
        for i in range(3):
            house = House(
                    load = pd.Series(
                        [5.]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                        )
                    )
            houses.append(house)

        swarm=Swarm(houses)
        swarm.request_expected_power()
        # the expected power is simply the aggreagted load in the first step devided by the cop == 3
        self.assertAlmostEqual(swarm.expected_power , 5.)
    
    def test_dispatcher(self):
        """test the call for potential
        """
        houses = []
        for i in range(3):
            house = House(
                    load = pd.Series(
                        [5.]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                        )
                    )
            houses.append(house)

        swarm=Swarm(houses)
        swarm.request_expected_power()
        swarm.request_potential()
        swarm.dispatch()
        # the expected power is 5: all 3 houses are available, each with a power of 3, so we take two houses... 
        self.assertEqual(swarm.call, {'House_0': 3.0, 'House_1': 3.0, 'House_2': 0.0})
    
    def test_broadcast(self):
        """test broadcasting of a potential call
        """
        houses = []
        for i in range(3):
            house = House(
                    load = pd.Series(
                        [5.]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                        )
                    )
            houses.append(house)

        swarm=Swarm(houses)
        swarm.request_expected_power()
        swarm.request_potential()
        swarm.dispatch()
        swarm.broadcast_potential_demand()
        for house in swarm.houses:
            self.assertAlmostEqual(swarm.call[house.name], house.external_signal)

    def test_policy(self):
        """test dispatching policy
        """
        houses = []
        for i in range(100):
            house = House(
                    load =  pd.Series(
                        [5]*24,index = pd.date_range(start='2021-01-01', periods=24, freq= '30Min')
                        )
                    )
            houses.append(house)

        swarm=Swarm(houses)
        done = False
        states = pd.DataFrame(columns=swarm.state_names)
        expected_values = []
        counter = 1
        while not done:
            state, reward, done, info = swarm.policy()
            expected_values.append(swarm.expected_power)
            states = pd.concat([states,swarm.pdstate])
            for house in swarm.houses:
                self.assertTrue(45 < house.T < 85)
            counter += 1

        power = states[[x for x in states.columns if "power_thermal" in x]].sum(axis=1)/3
        # 168: the smallest integer of the form max_power*n (max_power == 3) bigger than the expected_power == 166.666
        self.assertTrue((power <= 168).all())

    