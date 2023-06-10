import gym
import numpy as np
from stable_baselines3 import *
import warnings
import os
import pandas as pd
import argparse


parser = argparse.ArgumentParser(
    prog="ExecuteBaseline.py", usage="python ExecuteBaseline.py")
parser.add_argument("filename", default="",
                    help="Sets the path where the model should be stored or loaded.")
parser.add_argument("-l", "--load", action="store_true", default=False,
                    help="If this argument is set the program loads an model and does not train a new one.")
parser.add_argument("-r", "--render", action="store_true", default=False,
                    help="[EXPERIMENTAL] Renders the model actions in the environment with mathplotlib.")
parser.add_argument("-x", "--exit", action="store_true",
                    default=False, help="Exits after trainig model if set.")
parser.add_argument("-s", "--eval_seed", type=int,
                    help="Seed for the evaluation environment.")
parser.add_argument("-t", "--timesteps", type=int,
                    help="Specifies the maximum timesteps for training of model. Default 50_000.")
parser.add_argument(
    "--log", help="Specifies the path where the reward log should be saved. Default no logs will be saved.")
parser.add_argument("-e", "--episodes", type=int,
                    help="Sets the amount of evaluation episodes. Default: 1.")
parser.add_argument("--no_random", action='store_true', default=False,
                    help="Does not evaluate random. Default evaluates random.")
args = parser.parse_args()

MODEL_PATH = None
if(args.filename != ""):
    MODEL_PATH = os.path.normpath(args.filename)
EVAL_EPISODES = 1
if(args.episodes):
    EVAL_EPISODES = args.episodes
TOTAL_STEPS = 50_000
if(args.timesteps):
    TOTAL_STEPS = args.timesteps
warnings.filterwarnings('ignore')
print(f"============================Building environment============================")
env = gym.make("micro_grid:micro-v2")
env.seed(42)
eval_env = gym.make("micro_grid:micro-v2")
if args.eval_seed:
    eval_env.seed(args.eval_seed)
if(args.load):
    print(f"============================Loading============================")
    model = PPO.load(str(MODEL_PATH))
else:
    model = PPO('MlpPolicy', env, verbose=1, device='cuda')
    print(f"============================Learning============================")
    model.learn(total_timesteps=TOTAL_STEPS)
if(args.load != True and MODEL_PATH is not None):
    print(f"============================Saving============================")
    model.save(str(MODEL_PATH))

print(f"============================Evaluating============================")
if(args.exit):
    exit()
mean_reward = None
std_reward = None
model_rewards_all_episodes = []
model_sum_rewards_all_episodes = []
for i in range(EVAL_EPISODES):
    rewards_list_episode = np.array([])
    done = False
    obs = eval_env.reset()
    while True:
        action, _ = model.predict(obs)
        obs, reward, done, info = eval_env.step(action)
        rewards_list_episode = np.append(rewards_list_episode, reward)
        if(args.render):
            eval_env.render()
        if done == True:
            break
    model_rewards_all_episodes += rewards_list_episode.tolist()
    model_sum_rewards_all_episodes.append(np.sum(rewards_list_episode))
mean_reward = np.mean(model_rewards_all_episodes)
std_reward = np.std(model_rewards_all_episodes)
print(f"mean_reward_per_step:{mean_reward:.2f} +/- {std_reward:.2f}")
print(f"============================Evaluation Ended============================")
if(not args.no_random):
    print(f"============================Random Action Evaluation============================")
    eval_env.reset()
    rewards_list_all_random = []
    for i in range(EVAL_EPISODES):
        rewards_list_episode = np.array([])
        done = False
        obs = eval_env.reset()
        while True:
            action = eval_env.action_space.sample()
            obs, rewards, done, info = eval_env.step(action)
            rewards_list_episode = np.append(rewards_list_episode, rewards)
            if done == True:
                break
        rewards_list_all_random += rewards_list_episode.tolist()
    print(
        f"mean_reward_per_step random={np.mean(rewards_list_all_random):.2f} +/- {np.std(rewards_list_all_random)}")
    print(f"============================Random Action Evaluation Ended============================")


if(args.log):
    db = pd.DataFrame()
    if(not args.no_random):
        db['rnd_rewards'] = rewards_list_all_random
    db['model_rewards'] = model_rewards_all_episodes
    db2 = pd.DataFrame()
    db2['model_sum_rewards'] = model_sum_rewards_all_episodes
    db3 = pd.DataFrame()
    db3['model_mean_reward_per_step'] = [mean_reward]
    db3['model_std_reward_per_step'] = [std_reward]
    db3['episode_mean_reward'] = [np.mean(model_sum_rewards_all_episodes)]
    db3['episode_std_reward'] = [np.std(model_sum_rewards_all_episodes)]
    path = os.path.normpath(args.log)
    pd.concat([db, db2, db3], axis=1).to_csv(str(path))


# reward_sum_list = [model_rewards_all_episodes[0]]
# x = [0]
# for index in range(1, len(model_rewards_all_episodes)):
#     reward_sum_list.append(
#         model_rewards_all_episodes[index] + reward_sum_list[index-1])
#     x.append(index)
# import matplotlib.pyplot as plt
# plt.plot(x,reward_sum_list)
# plt.show()
