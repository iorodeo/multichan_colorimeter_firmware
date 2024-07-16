import busio
import board
import constants
import adafruit_as7341
import ulab
from collections import OrderedDict

class LightSensor:

    NUM_CHAN = 10
    DEFAULT_GAIN = constants.STR_TO_GAIN['16x']
    CHANNEL_NAMES = [k for k in constants.STR_TO_CHANNEL]
    AS7341_MAX_COUNT = 2**16-1

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        try:
            self._device = adafruit_as7341.AS7341(i2c)
        except ValueError as error:
            raise LightSensorIOError(error)
        self.gain = self.DEFAULT_GAIN

    @property 
    def max_counts(self):
        return self.AS7341_MAX_COUNT

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value
        self._device.gain = value

    @property
    def values_as_dict(self):
        values_dict = OrderedDict()
        values = self.values
        for name, value in zip(self.CHANNEL_NAMES, values):
            values_dict[name] = value
        return values_dict

    @property
    def raw_values(self):
        values = list(self._device.all_channels)
        values.append(self._device.channel_nir)
        values.append(self._device.channel_clear)
        return values

    def raw_channel(self, channel):
        if channel >= constants.NUM_CHANNEL:
            raise ValueError('channel out of range') 
        value = self.raw_values[channel]
        if value >= self.max_counts:
            raise LightSensorOverflow('light sensor reading > max_counts')
        return value



class LightSensorOverflow(Exception):
    pass

class LightSensorIOError(Exception):
    pass

