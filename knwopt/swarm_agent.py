

from .dispatcher import dispatcher
from .house_agent import House
import numpy as np
import pandas as pd


class Swarm:
    
    def __init__(self,houses:list):
        n = None
        freq = None
        names = []
        counter = 0
        for house in houses:
            if not isinstance(house, House):
                raise TypeError("houses have to be of type House")
            if n is not None and len(house.load) != n:
                raise ValueError("load profiles of houses have to be of equal length")
            n = len(house.load)
            if freq is not None and house.tau != freq:
                raise ValueError("load profiles of houses have to be of equal length")
            freq = house.tau
            house.name = f'House_{counter}'
            counter +=1

        self.houses = houses
        self.pdstate = pd.DataFrame(columns=self.state_names) 


    @property
    def state_names(self):
        vrs = []
        for house in self.houses:
            vrs = vrs + [house.name + '__' + x for x in house.state_names]
        return vrs

    def step(self, action = None):      
        dones = []
        infos = {}
        rewards = 0
        _states = []
        _states_ = []

        for house in self.houses:
            state, reward, done, info = house.policy()
            _states_.append(house.pdstate)
            rewards += reward
            dones.append(done)
            _states.append(state)
            infos.update(info)
        self.pdstate = pd.concat(_states_,axis=1)
        self.pdstate.columns = self.state_names
        states = np.concatenate(_states)
        
   
        return states, rewards, any(dones), infos 

    @property
    def count(self):
        for house in self.houses:
            return house.count
    @property
    def current_time(self):
        for house in self.houses:
            return house.load.index[house.count]

  

    def reset(self):   
        _states= []
        __states = []
        for house in self.houses:
            _states.append(house.reset())
            __states.append(house.pdstate)
        states = np.concatenate(_states)
        self.pdstate = pd.concat(__states)
        return states
    
    def request_potential(self):
        self.portfolio = {}
        for house in self.houses:
            self.portfolio[house.name] = house.potential

    def _calculate_expected_power(self):
        m = 0.
        for house in self.houses:
            m += (house.load / house.cop)[max(house.count - int(np.ceil(24 / house.tau)) ,0):house.count + 1].mean()
        return m


    def request_expected_power(self):
        self.expected_power = self._calculate_expected_power()

    
    def dispatch(self):
        self.call = dispatcher(self.expected_power, self.portfolio)
    

    
    def broadcast_potential_demand(self):
        for house in self.houses:
            if house.name in self.call:
                house.external_signal = self.call[house.name]


    def policy(self):
        self.request_potential()
        self.request_expected_power()
        self.dispatch()
        self.broadcast_potential_demand()
        return self.step()

    




