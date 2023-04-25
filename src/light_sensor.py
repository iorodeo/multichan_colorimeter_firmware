import adafruit_as7341
import ulab
from collections import OrderedDict

class MultiChanLightSensor:

    NUM_CHAN = 10
    DEFAULT_GAIN = adafruit_as7341.Gain.GAIN_16X
    #DEFAULT_GAIN = adafruit_as7341.Gain.GAIN_32X
    #DEFAULT_GAIN = adafruit_as7341.Gain.GAIN_64X
    #DEFAULT_GAIN = adafruit_as7341.Gain.GAIN_128X
    CHANNEL_NAMES = [
            '415nm',  # chan 1
            '445nm',  # chan 2
            '480nm',  # chan 3
            '515nm',  # chan 4
            '555nm',  # chan 5
            '590nm',  # chan 6
            '630nm',  # chan 7
            '680nm',  # chan 8
            '910nm',  # chan 9 
            'clear',  # chan 10 
            ]
    def __init__(self,i2c):
        try:
            self._device = adafruit_as7341.AS7341(i2c)
        except ValueError as error:
            raise LightSensorIOError(error)
        self._device.gain = self.DEFAULT_GAIN

    @property
    def values_as_dict(self):
        values_dict = OrderedDict()
        values = self.values
        for name, value in zip(self.CHANNEL_NAMES, values):
            values_dict[name] = value
        return values_dict

    @property
    def values(self):
        values = ulab.numpy.zeros((10,))
        all_chans = self._device.all_channels
        for i in range(8):
            values[i] = all_chans[i]
        values[8] = self._device.channel_nir
        values[9] = self._device.channel_clear
        return values


class LightSensorOverflow(Exception):
    pass

class LightSensorIOError(Exception):
    pass

