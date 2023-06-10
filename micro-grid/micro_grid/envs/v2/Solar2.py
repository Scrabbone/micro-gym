from micro_grid.envs.v2.Ambient2 import Ambient
from micro_grid.envs.v1.EnergySource import Energysource


class Solar(Energysource):
    """The solar class representing a solar generator.

    Args:
        Energysource (_type_): Parent class for easier identification
    """

    def __init__(self, peak_power: float):
        self.peak_power = peak_power  # KWp per kilo watt per square meter sun beam

    def get_power(self, ambient: Ambient) -> float:
        """Return the generated solar power of the generator at the timestep

        Args:
            ambient (Ambient): The ambient of the environment

        Returns:
            float: The generated power at the given timestep
        """
        power = ambient.get_sunbeam()*self.peak_power
        return power
