import imp
import gym
from gym import spaces
from typing import Tuple
from micro_grid.envs.Ambient2 import Ambient
from micro_grid.envs.v2.Solar2 import Solar
from micro_grid.envs.v1.WindGenerator import WindGenerator
from micro_grid.envs.v2.Battery2 import Battery
from micro_grid.envs.v3.Building3 import Building
import numpy as np
import random
import Monitor
import queue as qu
import threading
import os
import yaml

## PARAMETERS ##
PRICE_FLUCTUATION = 0.5
TOTAL_DAYS = 365.25


class Grid_env_3(gym.Env):
    """This is a reinforcement learning environment, based on the openai gym environments.
    This environment creates a microgrid community, every step is one hour. Every building is connect with every other one

    Args:
        gym (_type_): Parent class From openai gym
    """

    def __init__(self):
        self.total_power_bought = [0]
        self.queue = qu.Queue()
        self.ambient = Ambient(TOTAL_DAYS, PRICE_FLUCTUATION)

        self.buildings = self.load_building_config('./config.yml')

        # self.buildings = [Building([Solar(11.1)], Battery(27.76), 5, self.ambient),
        #                   Building([], Battery(0), 3, self.ambient),
        #                   Building([], Battery(0), 1, self.ambient)]
        n_actions = []
        for i in range(pow(len(self.buildings), 2)):
            n_actions.append(3)
        self.action_space = spaces.MultiDiscrete(
            n_actions)  # wegnehmen und senden
        self.observation_space = spaces.Box(
            low=0.0, high=10_000.0, shape=(len(self.buildings) + 3,))
        self.render_thread = threading.Thread(
            args=(self.buildings, self.queue, self.ambient), target=Monitor.create_plot)

    def seed(self, seed: int) -> None:
        """Sets the seed of the different random generators used

        Args:
            seed (int): The seed to be set.
        """
        random.seed(seed)

    def get_state(self) -> spaces.Box:
        """Generates the environment state 
        Consists of the building states and the ambient state

        Returns:
            spaces.Box: The environment state
        """
        observations = np.array([])
        observations = np.append(observations, self.ambient.get_state())
        for building in self.buildings:
            observations = np.append(observations, [building.get_state()])
        return observations.flatten()

    def reset(self) -> spaces.Box:
        """Resets the Environment

        Returns:
            spaces.Box: The environment state
        """
        self.queue = qu.Queue()
        self.render_thread = threading.Thread(
            args=(self.buildings, self.queue, self.ambient), target=Monitor.create_plot)
        self.total_power_bought = [0]
        self.ambient.reset()
        for building in self.buildings:
            building.reset()
        return self.get_state()

    def reward_func(self, power_bought: float) -> float:
        """Calculates the reward based on the bought electricity.
        If the bought energy costs more than the mean bought energy: -1
        If the bought energy costs less or equal than the mean, and is more than 0: -0.5
        IF the power bought is 0 : 1
        Args:
            power_bought (float): BOught electricity this step, in euros

        Returns:
            float: The reward, max reward is 1 min is -1
        """
        mean_cost = np.mean(self.total_power_bought)
        reward = 0
        if(power_bought > mean_cost):
            reward = -1
        elif(power_bought <= mean_cost and power_bought > 0):
            reward = -0.5
        if(power_bought <= 0):
            reward = 1
        return reward

    def step(self, action) -> Tuple[spaces.Box, float, bool, dict]:
        """Performs the environment time step base on the taken action

        Args:
            action (_type_): The action to be taken

        Returns:
            Tuple[spaces.Box, float, bool, dict]: Returns the state, reward, done state and info of the  environment step
        """
        # convert action in matrix shape
        shaped_action = np.reshape(
            action, (len(self.buildings), len(self.buildings)))
        # put shaped action in queue for rendering
        try:
            self.queue.put_nowait(shaped_action)
        except qu.Full:
            pass
        # distriubute energy
        for s_index, source_building in enumerate(shaped_action):
            for d_index, dest_power in enumerate(source_building):
                self.buildings[d_index].receive_power(
                    self.buildings[s_index].consume_percentage(dest_power))
        # call step in all buildings
        for building in self.buildings:
            building.step()
        # read total bought power in this hour from external source
        power_bought = self.ambient.hourly_bought_energy
        # call step in ambient
        self.ambient.step()
        # Get state of environment
        state = self.get_state()
        # Calculate reward
        reward = self.reward_func(power_bought)
        # Log bought power from external source
        self.total_power_bought.append(power_bought)
        done = self.ambient.hour >= int(TOTAL_DAYS*24)
        info = {}
        return (state, reward, done, info)

    def render(self):
        """Renders the Environment, unused at the moment
        """
        if(self.render_thread.is_alive() == False):
            self.render_thread.start()

    def close(self):
        """Cleans up the Environment and closes it
        """
        print("cleaning up environment...")

    def load_building_config(self, config_path: str) -> list:
        """Parses environment config and creates building instances with the attributes of the config

        Args:
            config_path (str): config path as string

        Returns:
            list: list with building instances
        """
        building_list = []
        path = os.path.normpath(config_path)
        if(not os.path.isfile(path)):
            raise FileNotFoundError(
                "The config file that should be parsed does not exist")
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
        for index in range(len(config['buildings'])):
            energy_sources = []
            if(config['buildings'][index]['energy_sources'] is not None):
                for source_index in range(len(config['buildings'][index]['energy_sources'])):
                    peak_performance = config['buildings'][index]['energy_sources'][source_index]['peak_power']
                    if(config['buildings'][index]['energy_sources'][source_index]['type'] == "solar"):
                        energy_sources.append(Solar(peak_performance))
                    elif(config['buildings'][index]['energy_sources'][source_index]['type'] == "wind"):
                        energy_sources.append(WindGenerator(peak_performance))
            battery_capacity = config['buildings'][index]['battery']['capacity']
            inhabs = config['buildings'][index]['inhabitants']
            building_list.append(Building(energy_sources, Battery(
                battery_capacity), inhabs, self.ambient))
        return building_list
