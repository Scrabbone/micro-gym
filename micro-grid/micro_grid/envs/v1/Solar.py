import random
from micro_grid.envs.v1.Ambient import Ambient


class Solar:
    """The solar class representing a solar generator.
    """

    def __init__(self, seed, peak_power: float):
        random.seed(seed)
        self.peak_power = peak_power  # KWp

    def get_power(self, ambient: Ambient):
        """Return the generated solar power of the generator at the timestep

        Args:
            ambient (Ambient): The ambient of the environment

        Returns:
            float: The generated power at the given timestep
        """
        power = ambient.get_sunbeam()*self.peak_power
        return power
