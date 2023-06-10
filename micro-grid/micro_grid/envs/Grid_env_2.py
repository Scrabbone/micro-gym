import imp
import gym
from gym import spaces
from typing import Tuple
from micro_grid.envs.v2.Ambient2 import Ambient
from micro_grid.envs.v2.Solar2 import Solar
from micro_grid.envs.v1.WindGenerator import WindGenerator
from micro_grid.envs.v2.Battery2 import Battery
from micro_grid.envs.v2.Building2 import Building
import numpy as np
import random
import Monitor
import queue as qu
import threading

## PARAMETERS ##
PRICE_FLUCTUATION = 0.5
TOTAL_DAYS = 365.25


class Grid_env_2(gym.Env):
    """This is a reinforcement learning environment, based on the openai gym environments.
    This environment creates a microgrid community, every step is one hour. Every building is connect with every other one

    Args:
        gym (_type_): Parent class From openai gym
    """

    def __init__(self):
        self.total_power_bought = [0]
        self.metadata = {'render_modes': ["human"]}
        self.queue = qu.Queue()
        self.ambient = Ambient(TOTAL_DAYS, PRICE_FLUCTUATION)
        self.buildings = [Building([Solar(11.1)], Battery(27.76), 5, self.ambient),
                          Building([Solar(5.55)], Battery(
                              9.25), 2, self.ambient),
                          Building([Solar(2.78)], Battery(
                              1.85), 1, self.ambient),
                          Building([WindGenerator(2.7)], Battery(1.85), 1, self.ambient)]

        self.action_space = spaces.Box(low=0.0, high=500.0, shape=(
            pow(len(self.buildings), 2),))  # wegnehmen und senden
        self.observation_space = spaces.Box(
            low=0.0, high=10_000.0, shape=(len(self.buildings)*2 + 3,))
        self.render_thread = threading.Thread(
            args=(self.buildings, self.queue, self.ambient), target=Monitor.create_plot)
        self.render_thread = None

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
        observations = np.append(observations, self.ambient.render())
        for building in self.buildings:
            observations = np.append(observations, building.render())
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
        If the bought energy costs more than the mean bought energy -10, else +10
        If the bought energy costs more than the max bought energy -100 else +100

        Args:
            power_bought (float): BOught electricity this step, in euros

        Returns:
            float: The reward, max reward is 110 min is -110
        """
        mean_cost = np.mean(self.total_power_bought)
        max_cost = np.max(self.total_power_bought)
        reward = 0
        if(power_bought > mean_cost):
            reward -= 10
        else:
            reward += 10
        if(power_bought > max_cost):
            reward -= 100
        if(power_bought <= 0.2):  # TODO
            reward += (100 - pow(100, int(power_bought)) * 10)
        if(power_bought == 0.0):
            reward += 1_000
        return reward

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
        shaped_action = np.reshape(
            action, (len(self.buildings), len(self.buildings)))
        try:
            self.queue.put_nowait(shaped_action)
        except qu.Full:
            pass
        # Abziehen und Geben
        for s_index, source_building in enumerate(shaped_action):
            for d_index, dest_power in enumerate(source_building):
                self.buildings[d_index].receive_power(
                    self.buildings[s_index].consume_power(dest_power))

        # Step Haus
        for building in self.buildings:
            building.step()
        power_bought = self.ambient.hourly_bought_energy
        # Ambient Step
        self.ambient.step()
        state = self.get_state()
        reward = self.reward_func(power_bought)
        self.total_power_bought.append(power_bought)
        done = self.ambient.hour >= int(TOTAL_DAYS*24)
        info = {"money_used": self.total_power_bought}
        return (state, reward, done, info)

    def render(self, mode: str):
        """Renders the Environment, unused at the moment

        Args:
            mode (str): Rendering mode

        Returns:
            _type_: _description_
        """
        # pass
        # render_string = "Ambient:(Preis: "+str(self.ambient.actual_price)+", Sonne: "+str(self.ambient.get_sunbeam())+", Tageszeit: "+str(self.ambient.hour % 24)+")\nA: "+str((self.buildings[0].power_consumption(
        # ), self.buildings[0].get_power()))+"\nB: "+str((self.buildings[1].power_consumption(), self.buildings[1].get_power()))+"\n:C: "+str((self.buildings[2].power_consumption(), self.buildings[2].get_power()))
        if(self.render_thread.is_alive() == False):
            self.render_thread.start()
        return ""

    def close(self):
        """Cleans up the Environment and closes it
        """
        print("cleaning up environment...")
