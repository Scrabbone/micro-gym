import gym
from gym import spaces
from typing import Tuple
from micro_grid.envs.v1.Ambient import Ambient
from micro_grid.envs.v1.Solar import Solar
from micro_grid.envs.v1.Battery import Battery
from micro_grid.envs.v1.Building import Building
import numpy as np
import random

## PARAMETERS ##
PRICE_FLUCTUATION = 0.5
TOTAL_DAYS = 365.25
PUNISHMENT_FACTOR = 100


class Grid_env(gym.Env):
    def __init__(self):
        self.total_power_bought = 0
        self.seed = random.randint(0, 10_000)
        self.metadata = {'render_modes': ["human"]}

        self.ambient = Ambient(self.seed)
        self.buildings = [Building(self.seed, [Solar(self.seed, 11.1)], Battery(27.76), 5, self.ambient), Building(
            self.seed, [Solar(self.seed, 0.93)], Battery(0), 2, self.ambient), Building(self.seed, [], Battery(0), 1, self.ambient)]

        self.adj = [[0, 1, 1],
                    [1, 0, 1],
                    [1, 1, 0]]

        self.action_space = spaces.Box(low=0.0, high=500.0, shape=(9,))
        # self.observation_space = spaces.Dict({'ambient': spaces.Box(low=0.0, high=23.0, shape=(3,)), 'buildings': spaces.Box(low=0.0, high=500.0,shape=(3,2))})
        self.observation_space = spaces.Box(low=0.0, high=10_000.0, shape=(9,))

    def get_state(self) -> spaces.Box:
        """Generates the environment state consiting of the building states and the ambient state

        Returns:
            spaces.Box: The environment state
        """
        observations = np.array([])
        observations = np.append(observations, self.ambient.render())
        for building in self.buildings:
            observations = np.append(observations, building.render())
        return observations.flatten()

    def reset(self) -> spaces.Box:
        """Resets the Environment

        Returns:
            spaces.Box: The environment state
        """
        self.total_power_bought = 0
        self.ambient = Ambient(self.seed)
        self.buildings = [Building(self.seed, [Solar(self.seed, 11.1)], Battery(27.76), 5, self.ambient), Building(
            self.seed, [Solar(self.seed, 0.93)], Battery(0), 2, self.ambient), Building(self.seed, [], Battery(0), 1, self.ambient)]
        return self.get_state()

    def reward_func(self, power_bought: float) -> float:
        """Calculates the reward based on the bought electricity

        Args:
            power_bought (float): BOught electricity this step, in euros

        Returns:
            float: The reward, max reward is 110 min is -110
        """
        if(power_bought > 0):
            return -100*power_bought
        else:
            return 100

    def step(self, action) -> Tuple[spaces.Box, float, bool, dict]:
        """Performs the environment time step base on the taken action

        Args:
            action (_type_): The action to be taken

        Returns:
            Tuple[spaces.Box, float, bool, dict]: Returns the state, reward, done state and info of the  environment step
        """
        # Check whether action is in self.action_space
        # Run action in Environment
        # Return Tuple[state, reward, done, info]
        shaped_action = np.reshape(action, (3, 3))
        # Abziehen und Geben
        for s_index, source_building in enumerate(shaped_action):
            for d_index, dest_power in enumerate(source_building):
                self.buildings[d_index].receive_power(
                    self.buildings[s_index].consume_power(dest_power))

        # Step Haus
        for building in self.buildings:
            building.step()
        # Ambient Preis abfragen
        self.total_power_bought += self.ambient.hourly_bought_energy
        power_bought = self.ambient.hourly_bought_energy
        # Ambient Step
        self.ambient.step()

        state = self.get_state()
        reward = self.reward_func(power_bought)
        done = self.ambient.hour >= int(TOTAL_DAYS*24)
        info = {}
        return (state, reward, done, info)

    def render(self, mode: str):
        """Renders the Environment, unused at the moment

        Args:
            mode (str): Rendering mode

        Returns:
            _type_: _description_
        """
        pass
        # render_string = "Ambient:(Preis: "+str(self.ambient.actual_price)+", Sonne: "+str(self.ambient.get_sunbeam())+", Tageszeit: "+str(self.ambient.hour%24)+")\nA: "+str((self.buildings[0].power_consumption(), self.buildings[0].get_power()))+"\nB: "+str((self.buildings[1].power_consumption(), self.buildings[1].get_power()))+"\n:C: "+str((self.buildings[2].power_consumption(), self.buildings[2].get_power()))
        # return render_string

    def close(self):
        """Cleans up the Environment and closes it
        """
        print("cleaning up environment...")

    def seed(self, seed: int):
        """Sets the seed

        Args:
            seed (int): Seed to be set
        """
        self.seed = seed
