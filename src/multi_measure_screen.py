import board
import displayio
import constants
import fonts
from adafruit_display_text import label


class MultiMeasureScreen:

    def __init__(self):

        # Setup color palette
        self.color_to_index = {k:i for (i,k) in enumerate(constants.COLOR_TO_RGB)}
        self.palette = displayio.Palette(len(constants.COLOR_TO_RGB))
        for i, palette_tuple in enumerate(constants.COLOR_TO_RGB.items()):
            self.palette[i] = palette_tuple[1]   

        # Create tile grid
        self.bitmap = displayio.Bitmap( 
                board.DISPLAY.width, 
                board.DISPLAY.height, 
                len(constants.COLOR_TO_RGB)
                )
        self.bitmap.fill(self.color_to_index['black'])
        self.tile_grid = displayio.TileGrid(self.bitmap,pixel_shader=self.palette)
        font_scale = 1

        # Create header text label
        header_str = 'Absorbance'
        text_color = constants.COLOR_TO_RGB['white']
        self.header_label = label.Label(
                #fonts.font_10pt, 
                fonts.font_8pt, 
                text = header_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5, 1.0),
                )
        bbox = self.header_label.bounding_box
        header_label_x = board.DISPLAY.width//2 
        header_label_y = bbox[3] + 1 
        self.header_label.anchored_position = (header_label_x, header_label_y)

        # Create absorbance value text label
        self.value_labels = []
        for xpos in (1, 84):
            for i in range(5):
                dummy_value = 0.0
                value_str = f'{dummy_value:1.2f}'.replace('0','O')
                text_color = constants.COLOR_TO_RGB['white']
                value_label = label.Label(
                        fonts.font_8pt, 
                        text = value_str, 
                        color = text_color, 
                        scale = font_scale,
                        anchor_point = (0.0,1.0),
                        rotation=90,
                        )
                bbox = value_label.bounding_box
                value_label_x = xpos 
                value_label_y = header_label_y + (i+1)*(bbox[3] + 7) + 5 
                value_label.anchored_position = (value_label_x, value_label_y)
                self.value_labels.append(value_label)

        
        # Create text label for blanking info
        # Note: not shown when gain and time labels are shown
        blank_str = '*' 
        text_color = constants.COLOR_TO_RGB['orange']
        self.blank_label = label.Label(
                fonts.font_8pt, 
                text=blank_str, 
                color=text_color, 
                scale=font_scale,
                anchor_point = (0.5,0.0),
                )
        bbox = self.blank_label.bounding_box
        blank_label_x = board.DISPLAY.width - 10 
        blank_label_y = board.DISPLAY.height - 14 
        self.blank_label.anchored_position = (blank_label_x, blank_label_y)

        # Create integration time/window text label
        bat_str = 'battery 0.0V'
        text_color = constants.COLOR_TO_RGB['gray']
        self.bat_label = label.Label(
                fonts.font_8pt, 
                text = bat_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.5,0.0),
                )
        bbox = self.bat_label.bounding_box
        bat_label_x = board.DISPLAY.width//2  
        bat_label_y = board.DISPLAY.height - 15 
        self.bat_label.anchored_position = (bat_label_x, bat_label_y)

        # Create gain text label
        gain_str = 'ABCX'
        text_color = constants.COLOR_TO_RGB['gray']
        self.gain_label = label.Label(
                fonts.font_8pt, 
                text = gain_str, 
                color = text_color, 
                scale = font_scale,
                anchor_point = (0.0,0.0),
                )
        bbox = self.gain_label.bounding_box
        gain_label_x = 1 
        gain_label_y = board.DISPLAY.height - 15
        self.gain_label.anchored_position = (gain_label_x, gain_label_y)
        
        # Ceate display group and add items to it
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.group.append(self.header_label)
        for item in self.value_labels:
            self.group.append(item)
        self.group.append(self.blank_label)
        self.group.append(self.bat_label)
        self.group.append(self.gain_label)

    def set_measurement(self, name, units, values, chans, precision):
        # NOTE: precision not used ....
        if values is None:
            self.values_label.color = constants.COLOR_TO_RGB['orange']
            self.values_label.text = 'range error' 
        else:
            self.header_label.text = name
            for label, value, chan in zip(self.value_labels, values, chans):
                if name == "Raw Sensor":
                    values_str = f'{chan} {int(value)}'
                else:
                    values_str = f'{chan} {abs(value):1.2f}'
                values_str = values_str.replace('0','O')
                label.text = values_str
                label.color = constants.COLOR_TO_RGB['white']

    def set_overflow(self, name):
        self.header_label.text = name
        self.value_label.text = 'overflow' 
        self.value_label.color = constants.COLOR_TO_RGB['red']

    def set_not_blanked(self):
        self.blank_label.text = 'NB'

    def set_blanking(self):
        self.blank_label.text = '**'

    def set_blanked(self):
        self.blank_label.text = 'BL'

    def set_battery(self, value):
        self.bat_label.text = f'battery {value:1.1f}V'

    def set_gain(self, value):
        self.gain_label.text = gain_str = constants.GAIN_TO_STR[value]

    def show(self):
        board.DISPLAY.show(self.group)

