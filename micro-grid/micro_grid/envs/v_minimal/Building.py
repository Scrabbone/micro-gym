
from argparse import ArgumentError
from micro_grid.envs.v_minimal.Ambient import Ambient


class Building:

    def __init__(self, ambient: Ambient, capacity=0, energy_consume=4_919/365.25/24, energy_produce=1):
        self.capacity = capacity  # in kWh
        self.energy_consume = energy_consume  # in kW
        self.energy_produce = energy_produce  # in kWp
        self.ambient = ambient
        self.available_energy = self.energy_produce

    def subtract_energy(self, percent: float) -> float:
        """Exports energy from this building and reduces the available energy for this building

        Args:
            percent (float): percent of energy that this building produces. Value 1.0 for 100 % and 0.0 for 0 %

        Raises:
            ArgumentError: Raises ArgumentError if the percent argument is not valid

        Returns:
            float: returns amount of exported energy from this building in kWh
        """

        if(percent > 1 or percent < 0):
            raise ArgumentError(
                "percent must be between 1.0 for 100 % or 0.0 for 0 %")
        asked_energy = percent*self.available_energy
        if(self.available_energy > asked_energy):
            self.available_energy -= asked_energy
            return asked_energy
        temp = self.available_energy
        self.available_energy = 0
        return temp

    def trit_substract_energy(self, trit: int) -> float:
        """Exports energy from this building and reduces the available energy for this building in 3 options [0,0.5,1.0]

        Args:
            trit (int): tryte that describes the amount of energy that should be exported

        Returns:
            float: amount of exported energy from this building in kWh
        """

        if(trit == 0):
            return self.subtract_energy(0.0)
        if (trit == 1):
            return self.subtract_energy(0.5)

        return self.subtract_energy(1.0)

    def add_energy(self, energy: float) -> None:
        """Adds energy to the available energy of this building in kWh

        Args:
            energy (float): The amount of energy in kWh that will be added to the available energy of this building
        """

        self.available_energy += energy

    def step(self) -> None:
        """ The Building steps one timestep.
            In that time the building consumes energy and maybe produces energy
        """

        self.available_energy -= self.energy_consume
        if(self.available_energy < 0):
            self.ambient.buy_energy(hash(self), self.available_energy*-1)
        else:
            self.ambient.buy_energy(hash(self), 0)
        self.available_energy = self.energy_produce

    def reset(self) -> None:
        """Sets Building in initial state.
            In that state the building has no available_energy and no filled capacity
        """
        self.capacity = 0
        self.available_energy = 0

    def get_state(self):
        raise NotImplementedError("NOCH NICHT IMPLEMENTIERT!")

    def __str__(self) -> str:
        """Returns Information about the state of the Building and the building itself

        Returns:
            str: Human readable information about the building
        """
        str = "Building {hash} with capacity: {cap} kWh, energy_consume: {cons} kW, energy_produce: {prod} kWp and actual available energy: {avai}."
        return str.format(hash=hash(self), cap=self.capacity, cons=self.energy_consume, prod=self.energy_produce, avai=self.available_energy)
