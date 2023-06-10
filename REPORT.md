# Report

## Compute Infrastructure

The agents were trained on the following setups:


* Intel NUC NUC7i5BNH: Prozessor intel i5 7260U, Hauptspeicher 8GB DDR4 RAM, Grafikkarte
integrierte Grafikeinheit.
- Intel NUC NUC8i5BEK: Prozessor intel i5 8259U, Hauptspeicher 8GB DDR4 RAM, Grafikkarte inte-
grierte Grafikeinheit.
- Desktop-PC: Prozessor AMD Ryzen 7 3700x, 32 GB DDR4 RAM, Grafikkarte Nvidia RTX 2080 Super.


## Training Parameters

The agents are standard [Stabel Baseline 3 PPO Agents](https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html). However for completions sake here are the Parameters used to train the Agents:

```
Gamma:  .99
Learning rate: .0003
Policy: MlpPolicy
Lambda:.95
Batch size: 64
n_steps: 2048
device: CPU
```

__A Episode is always one year in hours or 365.25 * 24__

The Following total timesteps were used for training models:

* 10,000
* 25,000
* 75,000
* 125,000
* 250,000
* 500,000
* 750,000

The models can be found in the [trained_models](./trained_models/) Folder with the Naming scheme:
_PPO_model_timesteps.zip_

A Comparison of all the different episode rewards of all models can be found [here](./Plotter/Plotter.html) and the evaluation data for the different models can be found [here](./trained_csv/), named _model_timsteps.csv_.
## Environment Setup

This chapter gives an insight of the setup of the microgrid the agents were trained and evaluated on.

### Environment Version 2

The agent was trained on a grid consisting of 3 buildings:


* Building 1: 5 inhabitants, big solar generator with 11.1 kWp and big battery with 27.76 kWh
* Building 2: 2 inhabitants, small solar generator with 0.93 kWp, no battery
*  Building 3: 1 inhabitant, no solar, no battery



### Environment Minimal Version

The agent was trained on a grid consisting of 2 buildings:


* Building 1: produces 1 kWp Energy, consumes 0.56 kW
* Building 2: produces no Energy, consumes 0.56 kW



## Reward Function

The Reward function is a function of the following 


![formula](images/lagrida_latex_editor.png)

### Environment Version 2

```Python

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
```

The reward function keeps track of the power bought in every past timestep of an episode and calculates a mean value from them. If the power bought in the present timestep equals 0 and is smaller than the mean the reward is 1. If the power bought is bigger than the mean the reward is -1. If the power bought is smaller or equal the reward is -0.5. 

### Environment Minimal Version

```Python

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
```

The reward function keeps track of the carbon emitted in every past timestep of an episode and calculates a mean, max and min value from them. If the carbon emitted in the present timestep is bigger than the max the reward is -1. If the carbon emitted is smaller than the min a 1 is returned, if its bigger than the mean value a -0.5 and if smaller a 0.5. If none of the above cases aplly a 0 is returned.