import os

os.environ['KIVY_GL_BACKEND'] = 'gl'

from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.clock import Clock
from services import connect_to_arduino
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from PIL import Image, ImageDraw, ImageFont
import brother_ql
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send

# Printer on mac
# PRINTER_IDENTIFIER = 'usb://0x04f9:0x2042'
# Printer on rasp
PRINTER_IDENTIFIER = '/dev/ttyUSB1'

sm = ScreenManager()
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
serialConnection = None
serialBuffer = ''
store = JsonStore('config.json')

try:
    serialConnection = connect_to_arduino('/dev/ttyUSB0')
except:
    try:
        serialConnection = connect_to_arduino('/dev/cu.usbserial-A600IP7D')
    except:
        print('Could not find arduino device!')


def print_label(value):
    # print label
    try:
        filename = 'label.png'
        img = Image.new('RGB', (62, 12), color=(255, 255, 255))
        fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 12)
        d = ImageDraw.Draw(img)
        d.text((10, 0), value, font=fnt, fill=(0, 0, 0))
        img.save(filename)
        printer = BrotherQLRaster('QL-700')
        print_data = brother_ql.brother_ql_create.convert(printer, [filename], '62', dither=True)
        send(print_data, PRINTER_IDENTIFIER)
    except:
        pass


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
            if value is "0":
                command = "MC 0\r"
                serialConnection.write(command.encode())
                self.output_label = "0"
                self.last_cut = "0"
            else:
                last_cut = value
                value = float(value) - float(self.manager.offset_label)
                if value > -1:
                    print_label(self.output_label)
                    command = "MC " + str(value) + "\r"
                    serialConnection.write(command.encode())
                    self.output_label = "0"
                    self.last_cut = last_cut
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

    def save(self):
        store.put('offset_label', value=self.manager.offset_label)
        self.manager.offset_label = str(self.manager.offset_label)
        self.manager.current = 'main'

        # TODO not working with python 3
        # def update(self):
        #     result = None
        #     try:
        #         data = urlopen("https://www.google.co.in")
        #         g = git.cmd.Git()
        #         result = g.pull()
        #         if result == "Already up to date.":
        #             popup = NoUpdatesPopup()
        #             popup.open()
        #         else:
        #             subprocess.call([sys.executable, "-m", "pip3", "install", '-r', 'requirements.txt'])
        #             popup = UpdatingPopup()
        #             popup.open()
        #             os.system('sudo shutdown -r now')
        #     except Exception as e:
        #         popup = NoConnectionPopup()
        #         popup.open()

        pass


class ListScreen(Screen):
    def start(self):
        self.manager.current = 'main'

    def button_call_back(self, value):
        pass

    pass


class NoConnectionPopup(Popup):
    pass


class NoUpdatesPopup(Popup):
    pass


class UpdatingPopup(Popup):
    pass


class ScreenManagement(ScreenManager):
    if store.exists('offset_label'):
        offset_label = StringProperty(store.get('offset_label')['value'])
    else:
        store.put('offset_label', value='0')
        offset_label = StringProperty("0")


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
                    serialBuffer = ""  # empty the buffer
                else:
                    serialBuffer += str(c)[2:-1]  # add to the buffer

    def build(self):
        return Builder.load_file("kivy.kv")


if __name__ == '__main__':
    CutterApp().run()
