import gc
import time
import ulab
import busio
import board
import analogio
import digitalio
import gamepadshift
import constants
import adafruit_itertools

from light_sensor import LightSensorOverflow
from light_sensor import LightSensorIOError
from light_sensor import MultiChanLightSensor

from battery_monitor import BatteryMonitor

from configuration import Configuration
from configuration import ConfigurationError

from calibrations import Calibrations
from calibrations import CalibrationsError

from menu_screen import MenuScreen
from message_screen import MessageScreen
from measure_screen import MeasureScreen

class Mode:
    MEASURE = 0
    MENU    = 1
    MESSAGE = 2
    ABORT   = 3

class DisplayMode:
    TEXT = 0
    BARS = 1

class Colorimeter:

    ABOUT_STR = 'About'
    RAW_SENSOR_STR = 'Raw Sensor' 
    ABSORBANCE_STR = 'Absorbance'
    TRANSMITTANCE_STR = 'Transmittance'
    DEFAULT_MEASUREMENTS = [ABSORBANCE_STR, TRANSMITTANCE_STR, RAW_SENSOR_STR]

    def __init__(self):

        self.i2c = busio.I2C(board.SCL, board.SDA)

        self.menu_items = list(self.DEFAULT_MEASUREMENTS)
        self.menu_view_pos = 0
        self.menu_item_pos = 0
        self.mode = Mode.MEASURE
        self.blank_values = ulab.numpy.ones((MultiChanLightSensor.NUM_CHAN,))
        self.is_blanked = False
        #self.measurement_name = self.TRANSMITTANCE_STR
        self.measurement_name = self.RAW_SENSOR_STR
        self.display_mode = DisplayMode.TEXT

        # Create screens
        board.DISPLAY.brightness = 1.0
        self.measure_screen = MeasureScreen()
        self.message_screen = MessageScreen()
        self.menu_screen = MenuScreen()

        # Setup gamepad inputs - change this (Keypad shift??)
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Load Configuration
        self.configuration = Configuration()
        try:
            self.configuration.load()
        except ConfigurationError as error:
            # Unable to load configuration file or not a dict after loading
            self.message_screen.set_message(error)
            self.message_screen.set_to_error()
            self.mode = Mode.MESSAGE

        # Load calibrations and populate menu items
        self.calibrations = Calibrations()

        # Setup multi-channel light sensor
        try:
            self.mc_light_sensor = MultiChanLightSensor(self.i2c)
        except LightSensorIOError as error:
            error_msg = f'missing sensor? {error}'
            self.message_screen.set_message(error_msg,ok_to_continue=False)
            self.message_screen.set_to_abort()
            self.mode = Mode.ABORT
        else:
            self.blank_sensor(set_blanked=False)
            self.measure_screen.set_not_blanked()

        # Setup up battery monitoring settings cycles 
        self.battery_monitor = BatteryMonitor()

    @property
    def num_menu_items(self):
        return len(self.menu_items)

    def incr_menu_item_pos(self):
        if self.menu_item_pos < self.num_menu_items-1:
            self.menu_item_pos += 1
        diff_pos = self.menu_item_pos - self.menu_view_pos
        if diff_pos > self.menu_screen.items_per_screen-1:
            self.menu_view_pos += 1

    def decr_menu_item_pos(self):
        if self.menu_item_pos > 0:
            self.menu_item_pos -= 1
        if self.menu_item_pos < self.menu_view_pos:
            self.menu_view_pos -= 1

    def update_menu_screen(self):
        n0 = self.menu_view_pos
        n1 = n0 + self.menu_screen.items_per_screen
        view_items = []
        for i, item in enumerate(self.menu_items[n0:n1]):
            led = self.calibrations.led(item)
            if led is None:
                item_text = f'{n0+i} {item}' 
            else:
                item_text = f'{n0+i} {item} ({led})' 
            view_items.append(item_text)
        self.menu_screen.set_menu_items(view_items)
        pos = self.menu_item_pos - self.menu_view_pos
        self.menu_screen.set_curr_item(pos)

    @property
    def is_absorbance(self):
        return self.measurement_name == self.ABSORBANCE_STR

    @property
    def is_transmittance(self):
        return self.measurement_name == self.TRANSMITTANCE_STR

    @property
    def is_raw_sensor(self):
        return self.measurement_name == self.RAW_SENSOR_STR

    @property
    def measurement_units(self):
        if self.measurement_name in self.DEFAULT_MEASUREMENTS: 
            units = None 
        else:
            units = self.calibrations.units(self.measurement_name)
        return units

    @property
    def raw_sensor_values(self):
        return self.mc_light_sensor.values

    @property
    def transmittances(self):
        transmittances = self.raw_sensor_values/self.blank_values
        mask = transmittances > 1.0
        transmittances[mask] = 1.0
        return transmittances

    @property
    def absorbances(self):
        absorbances = -ulab.numpy.log10(self.transmittances)
        mask = absorbances < 0.0
        absorbances[mask] = 0.0
        return absorbances

    @property
    def measurement_values(self):
        if self.is_absorbance: 
            values = self.absorbances
        elif self.is_transmittance:
            values = self.transmittances
        elif self.is_raw_sensor:
            values = self.raw_sensor_values
        else:
            try:
                value = self.calibrations.apply( 
                        self.measurement_name, 
                        self.absorbance
                        )
            except CalibrationsError as error:
                self.message_screen.set_message(error_message)
                self.message_screen.set_to_error()
                self.measurement_name = 'Absorbance'
                self.mode = Mode.MESSAGE
        return values

    def blank_sensor(self, set_blanked=True):
        num_chan = self.mc_light_sensor.NUM_CHAN
        num_samp = constants.NUM_BLANK_SAMPLES
        blank_samples = ulab.numpy.zeros((num_samp,num_chan))
        for i in range(num_samp):
            values = self.mc_light_sensor.values
            blank_samples[i,:] = self.mc_light_sensor.values 
            time.sleep(constants.BLANK_DT)
        self.blank_values = ulab.numpy.median(blank_samples,axis=0)
        if set_blanked:
            self.is_blanked = True

    def blank_button_pressed(self, buttons):  
        if self.is_raw_sensor:
            return False
        else:
            return buttons & constants.BUTTON['blank']

    def menu_button_pressed(self, buttons): 
        return buttons & constants.BUTTON['menu']

    def up_button_pressed(self, buttons):
        return buttons & constants.BUTTON['up']

    def down_button_pressed(self, buttons):
        return buttons & constants.BUTTON['down']

    def right_button_pressed(self, buttons):
        return buttons & constants.BUTTON['right']

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        #print(buttons)
        if not buttons:
            # No buttons pressed
            return 
        if not self.check_debounce():
            # Still within debounce timeout
            return  

        # Get time of last button press for debounce check
        self.last_button_press = time.monotonic()

        # Update state of system based on buttons pressed.
        # This is different for each operating mode. 
        if self.mode == Mode.MEASURE:
            if self.blank_button_pressed(buttons):
                self.measure_screen.set_blanking()
                self.blank_sensor()
            elif self.menu_button_pressed(buttons):
                self.mode = Mode.MENU
                self.menu_view_pos = 0
                self.menu_item_pos = 0
                self.update_menu_screen()

        elif self.mode == Mode.MENU:
            if self.menu_button_pressed(buttons):
                self.mode = Mode.MEASURE
            elif self.up_button_pressed(buttons): 
                self.decr_menu_item_pos()
            elif self.down_button_pressed(buttons): 
                self.incr_menu_item_pos()
            elif self.right_button_pressed(buttons): 
                selected_item = self.menu_items[self.menu_item_pos]
                if selected_item == self.ABOUT_STR:
                    about_msg = f'firmware version {constants.__version__}'
                    self.message_screen.set_message(about_msg) 
                    self.message_screen.set_to_about()
                    self.mode = Mode.MESSAGE
                else:
                    self.measurement_name = self.menu_items[self.menu_item_pos]
                    self.mode = Mode.MEASURE
            self.update_menu_screen()

        elif self.mode == Mode.MESSAGE:
            if self.calibrations.has_errors:
                error_msg = self.calibrations.pop_error()
                self.message_screen.set_message(error_msg)
                self.message_screen.set_to_error()
                self.mode = Mode.MESSAGE
            else:
                self.mode = Mode.MEASURE

    def check_debounce(self):
        button_dt = time.monotonic() - self.last_button_press
        if button_dt < constants.DEBOUNCE_DT: 
            return False
        else:
            return True

    def run(self):

        while True:

            gc.collect()

            # Deal with any button presses
            self.handle_button_press()

            # Update display based on the current operating mode
            if self.mode == Mode.MEASURE:

                # Get measurement and result to measurment screen
                try:
                    self.measure_screen.set_measurement(
                            self.measurement_name, 
                            self.measurement_units, 
                            self.measurement_values,
                            self.mc_light_sensor.CHANNEL_NAMES
                            )
                except LightSensorOverflow:
                    self.measure_screen.set_overflow(self.measurement_name)

                # Display whether or not we have blanking data. Not relevant
                # when device is displaying raw sensor data
                if self.is_raw_sensor:
                    self.measure_screen.set_blanked()
                else:
                    if self.is_blanked:
                        self.measure_screen.set_blanked()
                    else:
                        self.measure_screen.set_not_blanked()

                # Update and display measurement of battery voltage
                self.battery_monitor.update()
                battery_voltage = self.battery_monitor.voltage_lowpass
                self.measure_screen.set_bat(battery_voltage)

                self.measure_screen.show()

            elif self.mode == Mode.MENU:
                self.menu_screen.show()

            elif self.mode in (Mode.MESSAGE, Mode.ABORT):
                self.message_screen.show()

            time.sleep(constants.LOOP_DT)



