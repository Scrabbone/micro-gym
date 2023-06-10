from abc import abstractmethod


from micro_grid.envs.v1.Ambient import Ambient


class Energysource:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_power(self, ambient: Ambient) -> float:
        """Returns the generated power of the power source

        Returns:
            float: The generated power at the given timestep
        """
        pass
