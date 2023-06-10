from argparse import ArgumentError
from sys import hash_info
class Ambient:
    def __init__(self):
        self.green_house_gas_per_kwh = 1.150 #kg source: https://www.tech-for-future.de/co2-kwh-strom/
        self.booking_table = {}

    def buy_energy(self, building: int, energy: float) -> list:
        """Imports energy from external brown coal power plant that is bad for carbon foot print. Emmitted carbon will be logged for the building in an dict with a list

        Args:
            building (Building): The building that wants to buy energy
            energy (float): The amount of energy in kWh that should be bought from external power plant

        Returns:
            float: Returns the amounts of carbon that were emmitted by the building in a list
        """
        if(type(building) is not int):
            raise ArgumentError("Given building is not a object Building")
        carbon_amount = self.green_house_gas_per_kwh*energy
        if carbon_amount < 0:
            raise ArithmeticError("Amount of carbon is negative. That should not be possible")
        if(building in self.booking_table):
            self.booking_table[building].append(carbon_amount)
            return self.booking_table[building]
        self.booking_table[building] = [carbon_amount]
        print(self.booking_table)
        return [carbon_amount]

    def get_state(self) -> list:
        """Returns state of environment.

        Returns:
            list: Returns list of emmitted carbon of all buildings in latest time step
        """
        carbon_amount = []
        for building in self.booking_table:
            carbon_amount.append(self.booking_table[building][-1])
        return carbon_amount

    def reset(self) -> None:
        """Resets the ambient
        """
        for building in self.booking_table:
            self.booking_table[building] = [0]

    def __str__(self) -> str:
        """Returns Information about the state of the ambient itself

        Returns:
            str: Human readable information about the ambient
        """
        string = "Ambient with {carbon} kg carbon gas per kWh and booking_table:\n"
        for building in self.booking_table:
            string += "Building({hash})".format(hash=building)
            string += str(self.booking_table[building])
            string += "\n"
        return string.format(carbon=self.green_house_gas_per_kwh)