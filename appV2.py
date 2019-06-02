import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.config import Config
from functools import partial
from serial import *
from kivy.clock import Clock
from services import connect_to_arduino
from kivy.utils import get_color_from_hex

os.environ['KIVY_GL_BACKEND'] = 'gl'
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
serialConnection = None
serialBuffer = ''

try:
    serialConnection = connect_to_arduino('/dev/ttyUSB0')
except:
    try:
        serialConnection = connect_to_arduino('/dev/cu.usbserial-A600IP7D')
    except:
        print('Could not find arduino device!')


class YourApp(App):
    def __init__(self, **kwargs):
        super(YourApp, self).__init__(**kwargs)
        refresh_time = 0.5
        Clock.schedule_interval(self.read_serial, refresh_time)

    def read_serial(self, object):
        if serialConnection:
            while True:
                c = serialConnection.read()  # attempt to read a character from Serial
                # was anything read?
                if len(c) == 0:
                    break

                # get the buffer from outside of this function
                global serialBuffer

                # check if character is a delimeter
                if c == b'\r':
                    c = ''  # don't want returns. chuck it
                if c == b'\n':
                    serialBuffer += "\n"  # add the newline to the buffer

                    # add the line to the TOP of the log
                    print(serialBuffer)
                    serialBuffer = ""  # empty the buffer
                else:
                    serialBuffer += str(c)[2:-1]  # add to the buffer

    def button_call_back(self, value, object):
        if value == '<':
            current_value = self.output_label.text
            if current_value != '0' and len(current_value) > 1:
                self.output_label.text = current_value[:-1]
            else:
                self.output_label.text = "0"
        else:
            current_value = self.output_label.text
            if current_value == '0':
                current_value = ""
            self.output_label.text = current_value + str(value)

    def start(self, object):
        if serialConnection:
            value = self.output_label.text
            if int(value) > -1:
                command = "MC " + value + "\r"
                serialConnection.write(command.encode())
                self.output_label.text = "0"
                self.last_cut.text = value
            else:
                print('Not valid input')

    def build(self):

        self.output_label = Label(size_hint_y=1, text="0", font_size='50sp')
        self.last_cut = Label(size_hint_y=1, text="0", font_size='30sp')
        self.last_cut.color = get_color_from_hex('#A9A9A9')

        button_symbols = ('1', '2', '3',
                          '4', '5', '6',
                          '7', '8', '9',
                          '<', '0')

        button_grid = GridLayout(cols=3, size_hint_y=2)
        for symbol in button_symbols:
            dynamic_button = Button(text=symbol)
            dynamic_button.bind(
                on_press=partial(self.button_call_back, symbol))
            button_grid.add_widget(dynamic_button)

        start_button = Button(text='start', size_hint_y=None,
                              height=100)
        start_button.bind(
            on_press=partial(self.start))

        root_widget = BoxLayout(orientation='vertical')
        label_widget = BoxLayout(orientation='horizontal')
        command_widget = BoxLayout(orientation='vertical', padding=[0, 50, 0, 0])

        label_widget.add_widget(self.output_label)
        label_widget.add_widget(self.last_cut)
        root_widget.add_widget(label_widget)
        root_widget.add_widget(button_grid)
        command_widget.add_widget(start_button)
        root_widget.add_widget(command_widget)

        return root_widget


YourApp().run()
