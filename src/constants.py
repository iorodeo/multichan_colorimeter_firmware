import board
import collections

__version__ = '0.1.0'

CALIBRATIONS_FILE = 'calibrations.json'
CONFIGURATION_FILE = 'configuration.json'
SPLASHSCREEN_BMP = 'assets/splashscreen.bmp'

LOOP_DT = 0.01
BLANK_DT = 0.01
DEBOUNCE_DT = 0.6 
NUM_BLANK_SAMPLES = 3 
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
    ('415nm'  , 0x7600ed),
    ('445nm'  , 0x0028ff),
    ('480nm'  , 0x00d5ff),
    ('515nm'  , 0x1fff00),
    ('555nm'  , 0xb3ff00),
    ('590nm'  , 0xffdf00),
    ('630nm'  , 0xff4f00),
    ('680nm'  , 0xff0000),
    ])

