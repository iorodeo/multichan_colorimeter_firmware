import board
import collections
import adafruit_as7341

__version__ = '0.1.0'

CALIBRATIONS_FILE = 'calibrations.json'
CONFIGURATION_FILE = 'configuration.json'
SPLASHSCREEN_BMP = 'assets/splashscreen.bmp'

LOOP_DT = 0.1
BLANK_DT = 0.05
DEBOUNCE_DT = 0.7 
NUM_BLANK_SAMPLES = 5 
BATTERY_AIN_PIN = board.A6

BUTTON = { 
        'none'  : 0b00000000,
        'left'  : 0b10000000,
        'up'    : 0b01000000,
        'down'  : 0b00100000, 
        'right' : 0b00010000,
        'menu'  : 0b00001000, 
        'blank' : 0b00000100, 
        'itime' : 0b00000010,
        'gain'  : 0b00000001,
        }

COLOR_TO_RGB = collections.OrderedDict([ 
    ('black'  , 0x000000), 
    ('gray'   , 0x818181), 
    ('red'    , 0xff0000), 
    ('green'  , 0x00ff00),
    ('blue'   , 0x0000ff),
    ('white'  , 0xffffff), 
    ('orange' , 0xffb447),
    ('yellow' , 0xffdf00),
    ])

STR_TO_GAIN = collections.OrderedDict([ 
    ('0.5x',  adafruit_as7341.Gain.GAIN_0_5X),
    ('1x',    adafruit_as7341.Gain.GAIN_1X),
    ('2x',    adafruit_as7341.Gain.GAIN_2X),
    ('4x',    adafruit_as7341.Gain.GAIN_4X),
    ('8x',    adafruit_as7341.Gain.GAIN_8X),
    ('16x',   adafruit_as7341.Gain.GAIN_16X),
    ('32x',   adafruit_as7341.Gain.GAIN_32X),
    ('64x',   adafruit_as7341.Gain.GAIN_64X),
    ('128x',  adafruit_as7341.Gain.GAIN_128X),
    ('256x',  adafruit_as7341.Gain.GAIN_256X),
    ('512x',  adafruit_as7341.Gain.GAIN_512X),
    ])



GAIN_TO_STR = collections.OrderedDict(((v,k) for k,v in STR_TO_GAIN.items()))

STR_TO_INTEGRATION_TIME = collections.OrderedDict([])
INTEGRATION_TIME_TO_STR = \
    collections.OrderedDict(((v,k) for k,v in STR_TO_INTEGRATION_TIME.items()))


STR_TO_CHANNEL = collections.OrderedDict([ 
    ('415nm', 0),
    ('445nm', 1),
    ('480nm', 2),
    ('515nm', 3),
    ('555nm', 4),
    ('590nm', 5),
    ('630nm', 6),
    ('680nm', 7),
    ('910nm', 8),
    ('clear', 9),
    ])

CHANNEL_TO_STR = \
        collections.OrderedDict(((v,k) for k,v in STR_TO_CHANNEL.items()))
        
NUM_CHANNEL = len(STR_TO_CHANNEL)


