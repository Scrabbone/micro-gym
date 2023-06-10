

class Battery:
    """Structure representing the battery capacity of a buidling
    """

    def __init__(self, capacity: float):
        self.capacity = capacity  # kWh
        self.fuel = 0

    def get_fuel(self) -> float:
        """Returns the battery level

        Returns:
            float: the battery level
        """
        return self.fuel
    # Gets Power for an hour

    def get_power(self, power: float) -> float:
        """Drains the battery.
        If more power is to be taken than is available drains everything that is possible.
        Args:
            power (float): Power to be taken from the battery

        Returns:
            float: Power that was taken
        """
        work = power * 1  # kW * hour
        if self.fuel >= work:
            self.fuel -= work
            return work
        else:
            work = self.fuel
            self.fuel = 0
        return work
    # Loads battery

    def set_power(self, power: float):
        """Loads the battery.
        If loaded over the capacity of the battery the rest power gets dismissed

        Args:
            power (float): power to be loaded onto battery
        """
        work = power * 1
        self.fuel += work
        if(self.fuel > self.capacity):
            self.fuel = self.capacity

    def reset(self):
        """Resets battery level.
        """
        self.fuel = 0
