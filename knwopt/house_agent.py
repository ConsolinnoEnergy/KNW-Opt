"""provides a class representing a agent for the simulation of a house with heatpump, hot water and storage"""
import pandas as pd
import numpy as np

class House:
    _c = 1.16  # kWh/Km³
    _T_low = 0
    _T_high = 100
    state_names = [
        "temperature",
        "load_thermal",
        "power_thermal",
        "available"
        ]
    
    def __init__(self, load:pd.Series):
        self.load = load
        self.cop = pd.Series([3.]*len(self.load), index=load.index)
        self.power_electric = 3.
        self.volume = 1.
        self.T_min = 70
        self.T_max = 80
        self.count = 0
        self.initial_level = 0.5
        self.T = (self.T_max - self.T_min) * self.initial_level + self.T_min
        self.heating = 0
        self.min_run = 0.25
        self.min_down = 0.25
        self.endurance = self.min_down
        self.external_signal = None
        self.name="House"
        
    
    def reset(self):
        self.heating = 0
        self.count = 0
        self.T = (self.T_max - self.T_min) * self.initial_level  + self.T_min
        self.endurance = self.min_down
        self.state = pd.Series(
            np.array([self.T, self.load_thermal, self.power_thermal * self.heating, self.available]),
            index = self.state_names
            )
        self.state.name = self.load.index[self.count]
        self.count += 1
        return self.state 


    @property
    def tau(self):
        return self.load.index.freq.delta.total_seconds()/3600
    @property
    def power_thermal(self):
        return (self.power_electric * self.cop)[self.count]
    @property
    def load_thermal(self):
        return self.load[self.count]
    def step(self, action:float):
        action = int(action!=0)
        deltaE = (self.power_thermal * action - self.load_thermal) * self.tau
        deltaT = deltaE / (self._c * self.volume)
        self.T += deltaT
        self.T = max([self._T_low, min([self._T_high,self.T])]) 
        
        if int(action) != int(self.heating):
            self.endurance = self.tau
        else:
            self.endurance += self.tau 

        self.heating = action 

        self.state = pd.Series(
            np.array([self.T, self.load_thermal, self.power_thermal * self.heating, self.available]),
            index = self.state_names
            )
        self.state.name = self.load.index[self.count]
        self.count += 1
        done = False
        if self.count >= len(self.load):
            done = True
        reward  = 0
        info = {}
        
        return self.state.values, reward, done, info

    @property
    def pdstate(self):
        return pd.DataFrame(self.state).T

    @property
    def available(self):
        available = True
        if (self.T < self.T_min) or (self.T > self.T_max):
            available = False
        else:
            if self.heating!=0.:
                if self.endurance < self.min_run:
                    available = False
            else:
                if self.endurance < self.min_down:
                    available = False
        return available

    @property
    def power_expected(self):
        if self.T < self.T_min:
            return self.power_electric
        elif self.T > self.T_max:
            return 0.
        else:
            return int(self.heating) * self.power_electric


    @property
    def potential(self):
        return {"max_power": self.power_electric, "power": self.power_expected, "available": self.available}

    def policy(self):
        if self.available and not self.external_signal is None:
            return self.step(int(self.external_signal))
        else:
            if (self.T < self.T_min):
                action = 1.

            elif (self.T > self.T_max):
                action = 0.
            else:
                action = self.heating
        
            return self.step(action)




