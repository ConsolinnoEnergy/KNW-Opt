import unittest
from knwopt.house_agent import House
import pandas as pd

class HouseTest(unittest.TestCase):

    def test_house_constructor(self):
        """test constructor of house defaults, properties and the fallback policy
        """
        house = House(load=
            pd.Series(
                [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                )
            )
        self.assertAlmostEqual(house.load_thermal, 5)
        self.assertAlmostEqual(house.cop[0],3)
        self.assertAlmostEqual(house.initial_level,0.5)
        self.assertTrue(house.available == True)
        done = False
        state = house.reset()
        heating= []
        while not done:
            state, reward, done, info = house.policy()
            heating.append(house.heating != 0)
            self.assertTrue(45 < state[0] < 85)
        self.assertTrue(any(heating))

    def test_external_signal(self):
        """test the integration of an external signal
        """
        house = House(
            load=pd.Series(
                [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                )
            )
        house.reset()
        state, reward, done, info = house.policy()
        self.assertTrue(state[2]==0)
        house.reset()
        house.external_signal = house.power_electric
        state, reward, done, info = house.policy()
        self.assertTrue(state[2]== house.power_thermal)
    
    def test_pdstate(self):
        """test pdstate
        """
        house = House(
            load = pd.Series(
                [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                )
            )
        house.reset()
        df = house.pdstate
        self.assertAlmostEqual(df["temperature"].iloc[0], house.T)
        self.assertAlmostEqual(df["power_thermal"].iloc[0], 0)
        self.assertAlmostEqual(df["load_thermal"].iloc[0], 5)
   
    def test_potential(self):
        """test the potential
        """
        house = House(
            load = pd.Series(
                [5]*24,index = pd.date_range(start='2021-01-01',end='2021-01-01 23:00',freq= '1H')
                )
            )
        house.reset()
        self.assertEqual(house.potential, {'max_power':3.0, 'power':0.0, 'available':True} )

