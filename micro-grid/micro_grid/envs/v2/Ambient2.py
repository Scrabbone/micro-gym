from cmath import nan
import random
from time import daylight
import pysolar.solar
import datetime
from tzwhere import tzwhere
import pytz
import numpy as np
from meteostat import Hourly
from meteostat import Point
import queue as qu


class Ambient:
    """The Ambient of the Environment, keeps track of timespan, weather and sun radiation as well as energy price and buying energy.
    """

    def __init__(self, total_days: float, price_fluctuation: float, energy_price=0.3262, latitude=52.382590, longitude=9.717735):
        self.total_days = total_days
        self.hour = 0
        self.energy_price = energy_price
        self.actual_price = energy_price
        self.sunbeam = 0
        self.price_fluctuation = price_fluctuation
        self.hourly_bought_energy = 0  # in euro
        self.latitude = latitude
        self.longitude = longitude
        self.year_offset = random.randint(1, 20)
        self.night_hours = []
        # print("Year: "+str(datetime.datetime.now().year-self.year_offset))
        # Getting weather
        start = datetime.datetime(
            datetime.datetime.now().year-self.year_offset, 1, 1)
        end = datetime.datetime(
            datetime.datetime.now().year-self.year_offset+1, 1, 1)
        location = Point(self.latitude, self.longitude, 0)
        for attempt in range(10):
            try:
                data = Hourly(location, start, end,)
            except:
                print("Trying again for " + str(9 - attempt) + " times")
            else:
                break
        data = data.fetch()
        self.weather_condition = data['coco']
        self.winds = data['wspd']
        # Calculating sunbeam
        tzwhere_obj = tzwhere.tzwhere()
        timezone_str = tzwhere_obj.tzNameAt(self.latitude, self.longitude)
        self.timezone = pytz.timezone(timezone_str)
        self.sun_beams = []
        for i in range(int((total_days*24)+24)):
            self.sun_beams.append(self.calculate_sunbeam(i))
        # print("Created Ambient")
        self.queue = qu.Queue()
        # print(self.sun_beams)
        # print(np.mean(self.sun_beams))
        # print(np.std(self.sun_beams))
        # print(np.max(self.sun_beams))
        # print(np.min(self.sun_beams))
        # exit()

    def step(self):
        """Performs a time step for the Ambient of the Environment>
        Changes the energy price slightly and changes the radiation.
        """
        global PRICE_FLUCTUATION
        try:
            self.queue.put_nowait(
                [self.hour, self.hourly_bought_energy, self.year_offset])
        except qu.Full:
            pass
        self.hour += 1
        self.hourly_bought_energy = 0
        price_offset = 1
        if(random.randint(0, 1) == 0):
            price_offset = -1
        price_offset *= (self.price_fluctuation * 0.01 * random.random())
        self.actual_price = self.energy_price + price_offset
        # watt per square meter to kilo watt per square meter
        self.sunbeam = self.sun_beams[self.hour]/1000
        if(self.sunbeam > 1):
            self.sunbeam = 1

    def calculate_sunbeam(self, timestep: int) -> float:
        """Calculates the sun radiation for the given timestep

        Args:
            timestep (int): timestep in hours 

        Returns:
            float: the sun radiation in w per square meter
        """
        start_date = datetime.datetime(datetime.datetime.now(
        ).year-self.year_offset, 1, 1, 0, 0, 0, 0, tzinfo=self.timezone)
        date = start_date + datetime.timedelta(hours=timestep)
        altitude_deg = pysolar.solar.get_altitude(
            self.latitude, self.longitude, date)
        radiation = pysolar.solar.radiation.get_radiation_direct(
            date, altitude_deg)
        # Check whether its night
        if(radiation < 0 or altitude_deg <= 0):
            radiation = 0
        self.night_hours.append(altitude_deg <= 0)
        weather = self.weather_condition.iloc[self.hour]
        # Unclear sky
        modifier = 0.8
        if(weather >= 15 or weather == 9 or weather == 13 or weather == 11):
            modifier = 0.5
        # Clear sky
        elif(weather <= 3):
            modifier = 1
        return radiation*modifier

    def get_sunbeam(self) -> float:
        """Returns the sun radiation in kw per square meter in given time step

        Returns:
            float: sun radiation in kw per square meter
        """
        return self.sunbeam

    def get_wind(self) -> float:
        """Returns the windspeed in m per s for the given time step

        Returns:
            float: wind speed in m per s
        """
        if(len(self.winds) <= self.hour):
            return 0
        wind = self.winds[self.hour]
        if wind is nan:
            wind = random.uniform(0, 1)
        return wind * (5.0/18.0)

    def is_night(self) -> bool:
        """Checks if its night time or day time

        Returns:
            bool: True if night time
        """
        return self.night_hours[self.hour]

    def buy_energy(self, energy: float) -> float:
        """Buys energy at momentary energy price

        Args:
            energy (float): energy in kws

        Returns:
            float: price in eur
        """
        price = self.actual_price * energy
        self.hourly_bought_energy += price
        return price

    def get_state(self) -> list:
        """Returns the state of the ambient

        Returns:
            list: energy price, sun radiation and hour of day 
        """
        night = 0
        if(self.is_night()):
            night = 1
        return [self.get_wind(), self.sunbeam, night]

    def reset(self):
        """Resets the ambient.
        Sets timestep to 0, generates new random year, checks wether and radiation for year and resets energy price.
        """
        self.hour = 0
        self.actual_price = self.energy_price
        self.sunbeam = 0
        self.hourly_bought_energy = 0  # in euro
        self.year_offset = random.randint(1, 20)
        # Getting weather
        # print("Year: "+str(datetime.datetime.now().year-self.year_offset))
        start = datetime.datetime(
            datetime.datetime.now().year-self.year_offset, 1, 1)
        end = datetime.datetime(
            datetime.datetime.now().year-self.year_offset+1, 1, 1)
        location = Point(self.latitude, self.longitude, 0)
        data = Hourly(location, start, end,)
        data = data.fetch()
        self.weather_condition = data['coco']
        # Calculating sunbeam
        tzwhere_obj = tzwhere.tzwhere()
        timezone_str = tzwhere_obj.tzNameAt(self.latitude, self.longitude)
        self.timezone = pytz.timezone(timezone_str)
        self.sun_beams = []
        for i in range(int((self.total_days*24)+1)):
            self.sun_beams.append(self.calculate_sunbeam(i))
        self.queue = qu.Queue()
