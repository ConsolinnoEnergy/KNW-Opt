import unittest
from knwopt.dispatcher import dispatcher

class DispatcherTest(unittest.TestCase):

    def test_nothing_available(self):
        expected_power = 5 
        portfolio = {
            "hans":{
                "available":False,
                "power": -1.,
                "max_power": -1.
            },
            "Wurscht":{
                "available":False,
                "power": 6.,
                "max_power": 6.
            },
        }
        self.assertTrue({}==dispatcher(expected_power, portfolio) )
    
    def test_one_available_helping(self):
        expected_power = 5 
        portfolio = {
            "hans":{
                "available":True,
                "power": 5.,
                "max_power": 5.
            },
            "Wurscht":{
                "available":False,
                "power": 0.,
                "max_power": 0.
            },
        }
        self.assertAlmostEqual(5.,dispatcher(expected_power, portfolio)["hans"] )
    def test_one_available_not_helping(self):
        expected_power = 5 
        portfolio = {
            "hans":{
                "available":True,
                "power": 5.,
                "max_power": 5.
            },
            "Wurscht":{
                "available":False,
                "power": 5.,
                "max_power": 5.
            },
        }
        self.assertAlmostEqual(0.,dispatcher(expected_power, portfolio)["hans"] )

    def test_available_positive(self):
        expected_power = 10 
        portfolio = {
            "hans":{
                "available":True,
                "power": 5.,
                "max_power": 5.
            },
            "Wurscht":{
                "available":True,
                "power": 5.,
                "max_power": 5.
            },
        }
        self.assertAlmostEqual(5.,dispatcher(expected_power, portfolio)["hans"] )
        self.assertAlmostEqual(5.,dispatcher(expected_power, portfolio)["Wurscht"] )
    
    def test_available_positive_negative(self):
        expected_power = 10 
        portfolio = {
            "hans":{
                "available":True,
                "power": 13.,
                "max_power": 13.
            },
            "Wurscht":{
                "available":True,
                "power": -5.,
                "max_power": -5.
            },
        }
        self.assertAlmostEqual(13.,dispatcher(expected_power, portfolio)["hans"] )
        self.assertAlmostEqual(-5.,dispatcher(expected_power, portfolio)["Wurscht"] )

    def test_available_negative_negative(self):
        expected_power = 10 
        portfolio = {
            "hans":{
                "available":True,
                "power": -13.,
                "max_power": -13.
            },
            "Wurscht":{
                "available":True,
                "power": -5.,
                "max_power": -5.
            },
        }
        self.assertAlmostEqual(0.,dispatcher(expected_power, portfolio)["hans"] )
        self.assertAlmostEqual(0.,dispatcher(expected_power, portfolio)["Wurscht"] )