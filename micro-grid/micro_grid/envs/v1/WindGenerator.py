from micro_grid.envs.v2.Ambient2 import Ambient
from micro_grid.envs.v1.EnergySource import Energysource


class WindGenerator(Energysource):
    """This class represents a wind turbine

    Args:
        Energysource (_type_): Parent class for easier identification
    """

    def __init__(self, peak_power: float):
        self.peak_power = peak_power  # kilo watt per meter per second wind

    def get_power(self, ambient: Ambient) -> float:
        """Return the generated wind power of the generator at the timestep

        Args:
            ambient (Ambient): The ambient of the environment

        Returns:
            float: The generated power at the given timestep in kw 
        """
        power = ambient.get_wind()*self.peak_power
        return power
