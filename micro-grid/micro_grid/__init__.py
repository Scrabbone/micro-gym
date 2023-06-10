from importlib.metadata import entry_points
from gym.envs.registration import register
register(id='micro-v0', entry_point='micro_grid.envs:Grid_env',)
register(id='micro-v1', entry_point='micro_grid.envs:Grid_env_2',)
register(id='micro-v2', entry_point='micro_grid.envs:Grid_env_3',)
register(id='micro_minimal-v0', entry_point='micro_grid.envs:Grid_env_minimal')
