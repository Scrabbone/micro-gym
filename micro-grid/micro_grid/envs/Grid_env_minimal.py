import gym
from gym import spaces
from typing import Tuple
from random import random
from micro_grid.envs.v_minimal.Ambient import Ambient
from micro_grid.envs.v_minimal.Building import Building
import numpy as np

## PARAMETERS ##
TOTAL_DAYS = 365.25


class Grid_env_minimal(gym.Env):
    """Presents an environment that simulates a village with a microgrid, in which an agent has to steer the energy distribution. The goal is to import as few energy from external as possible to reduce the carbon foot print

    Args:
        gym (_type_): Inherits from Env class of the framework openai gym
    """

    def __init__(self):
        self.ambient = Ambient()
        self.buildings = [Building(self.ambient), Building(
            self.ambient, energy_produce=0)]

        for building in self.buildings:
            self.ambient.booking_table[hash(building)] = [0]

        self.carbon_sum_per_timestep = [0]

        n_actions = []
        for i in range(pow(len(self.buildings), 2)):
            n_actions.append(3)
        self.action_space = spaces.MultiDiscrete(
            n_actions)  # wegnehmen und senden
        self.observation_space = spaces.Box(
            low=0.0, high=(4_919/365.25/24)*1.150, shape=(len(self.buildings),))

    def reset(self) -> list:
        """Resets the environment to initial state

        Returns:
            list: returns the initial state
        """

        self.ambient.reset()
        for building in self.buildings:
            building.reset()
        self.carbon_sum_per_timestep = [0]
        return self.get_state()

    def reward_func(self, state: list) -> float:
        """Calculates the reward for the last executed action and appends sum of carbon in latest timestep to self.carbon_sum_per_timestep

        Args:
            state(list): list with emmitted carbon of every building in latest timestep

        Returns:
            float: The reward. Higher is better than lower
        """
        max = np.max(self.carbon_sum_per_timestep)
        mean = np.mean(self.carbon_sum_per_timestep)
        min = np.mean(self.carbon_sum_per_timestep)
        sum = np.sum(state)
        self.carbon_sum_per_timestep.append(sum)
        if(sum > max):
            return -1.0
        if(sum < min):
            return 1.0
        if(sum > mean):
            return -0.5
        if(sum < mean):
            return 0.5
        return 0.0

    def step(self, action: spaces.MultiDiscrete) -> Tuple:
        """Executes an action in the environment

        Args:
            action (_type_): the action as adjazenz matrix with percentual energy that has to be sent from building A to building B

        Returns:
            Tuple[]: Tuple with (new_state, reward of executed action, whether tne environment ended, custom info(not used yet))
        """
        shaped_action = np.reshape(
            action, (len(self.buildings), len(self.buildings)))

        # distriubute energy
        for s_index, source_building in enumerate(shaped_action):
            for d_index, dest_power in enumerate(source_building):
                self.buildings[d_index].add_energy(
                    self.buildings[s_index].trit_substract_energy(dest_power))

        # call step in all buildings
        for building in self.buildings:
            building.step()

        state = self.ambient.get_state()
        reward = self.reward_func(state)
        done = len(next(iter(self.ambient.booking_table.values()))
                   ) >= TOTAL_DAYS*24
        info = {}
        return (state, reward, done, info)

    def get_state(self) -> list:
        """Returns the state of Environment

        Returns:
            list: Returns list of emmitted carbon of all buildings in latest time step
        """
        return self.ambient.get_state()

    def render(self):
        """Renders the environment states as 2D Animation
        #TODO   
        """
        raise NotImplementedError("Not implemented render-function yet!")

    def close(self):
        """Deconstructs the environment and kills all working tasks
        """
        self.reset()
        print("Closed environment")

    def seed(self, seed: int) -> None:
        """Sets as specific seed. So that random actions are reproduceable

        Args:
            seed (int): The seed that will be set in the random generator
        """

        random.seed(seed)
