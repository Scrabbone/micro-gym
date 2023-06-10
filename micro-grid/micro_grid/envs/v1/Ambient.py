import random

from torch import rand


class Ambient:
    """The Ambient of the Environment, keeps track of timespan, weather and sun radiation as well as energy price and buying energy.
    """

    def __init__(self, seed: int, energy_price=0.3262):
        self.seed = seed
        self.hour = 0
        self.energy_price = energy_price
        self.actual_price = energy_price
        self.sunbeam = 0
        self.hourly_bought_energy = 0  # in euro

    def step(self):
        """Performs a time step for the Ambient of the Environment>
        Changes the energy price slightly and changes the radiation.
        to a random value.
        """
        global PRICE_FLUCTUATION
        self.hour += 1
        self.hourly_bought_energy = 0
        random.seed(self.seed)
        price_offset = 1
        if(random.randint(0, 1) == 0):
            price_offset = -1
        price_offset *= (0.5 * 0.01 * random.random())
        self.actual_price = self.energy_price + price_offset
        if(self.is_night()):
            self.sunbeam = 0
        else:
            self.sunbeam = random.random()

    def get_sunbeam(self) -> float:
        """Returns the sun radiation in kw per square meter in given time step

        Returns:
            float: sun radiation in kw per square meter
        """
        return self.sunbeam

    def is_night(self) -> bool:
        """Checks if its night time or day time

        Returns:
            bool: True if night time
        """
        hour_of_day = self.hour % 24
        if hour_of_day < 8 or hour_of_day > 20:
            return True
        return False

    def buy_energy(self, energy: float) -> float:
        """Buys energy at momentary energy price

        Args:
            energy (float): energy in kw

        Returns:
            float: price in eur
        """
        price = self.actual_price * energy
        self.hourly_bought_energy += price
        return price

    def render(self) -> list:
        """Returns the state of the ambient

        Returns:
            list: energy price, sun radiation and hour of day 
        """
        return [self.actual_price, self.sunbeam, self.hour % 24]

    def reset(self):
        """Resets the ambient.
        Sets timestep, sunbeam and bought energy to 0, resets energy price.
        """
        self.hour = 0
        self.actual_price = self.energy_price
        self.sunbeam = 0
        self.hourly_bought_energy = 0  # in euro
