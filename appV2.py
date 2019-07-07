import os

os.environ['KIVY_GL_BACKEND'] = 'gl'
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from serial import *
from kivy.clock import Clock
from services import connect_to_arduino
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

sm = ScreenManager()
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


# Declare both screens
class MainScreen(Screen):
    output_label = StringProperty("0")
    last_cut = StringProperty("0")

    def button_call_back(self, value):
        if value == '<':
            current_value = self.output_label
            if current_value != '0' and len(current_value) > 1:
                self.output_label = current_value[:-1]
            else:
                self.output_label = "0"
        elif value == '.':
            current_value = self.output_label
            if current_value.count('.') < 1:
                if current_value == '0':
                    current_value = "0."
                    self.output_label = current_value
                else:
                    self.output_label = current_value + str(value)

        else:
            current_value = self.output_label
            if current_value == '0':
                current_value = ""
            self.output_label = current_value + str(value)

    def start(self):
        if serialConnection:
            value = self.output_label
            value = float(value) - float(self.manager.offset_label)
            if value > -1:
                command = "MC " + str(value) + "\r"
                serialConnection.write(command.encode())
                self.output_label = "0"
                self.last_cut = str(value)
            else:
                print('Not valid input')

    pass


class SettingsScreen(Screen):
    def button_call_back(self, value):
        if value == '<':
            current_value = self.manager.offset_label
            if current_value != '0' and len(current_value) > 1:
                self.manager.offset_label = current_value[:-1]
            else:
                self.manager.offset_label = "0"
        elif value == '.':
            current_value = self.manager.offset_label
            if current_value.count('.') < 1:
                if current_value == '0':
                    current_value = "0."
                    self.manager.offset_label = current_value
                else:
                    self.manager.offset_label = current_value + str(value)

        else:
            current_value = self.manager.offset_label
            if current_value == '0':
                current_value = ""
            self.manager.offset_label = current_value + str(value)

    pass


class ScreenManagement(ScreenManager):
    offset_label = StringProperty('0')


class CutterApp(App):
    def __init__(self, **kwargs):
        super(CutterApp, self).__init__(**kwargs)
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

    def build(self):
        return Builder.load_file("kivy.kv")


if __name__ == '__main__':
    CutterApp().run()
