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
from PIL import Image, ImageDraw,ImageFont
from threading import Timer
import urllib
from sh import git
import threading

PRINTER_IDENTIFIER = 'usb://0x04f9:0x2042'

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
    try:
        filename = 'label.png'
        fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 60)
        img = Image.new('RGB', (696, 271), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 0), value, font=fnt, fill=(0, 0, 0))
        img.save(filename)
        os.system('sudo brother_ql -p usb://0x04f9:0x2042 -b pyusb --model QL-700 print -l 62x29 label.png')
    except Exception as E:
        print("Failed to print")
        print(E)
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

    def enable_start_button(self):
        self.ids.start_button.disabled = False

    def start(self):
        self.ids.start_button.disabled = True
        Timer(2, lambda: self.enable_start_button()).start()
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
                    command = "MC " + str(value) + "\r"
                    serialConnection.write(command.encode())
                    print_label(self.output_label)
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

    def update(self):
        try:
            data = urllib.urlopen("https://www.google.com")
        except Exception as e:
            print(e)
            popup = NoConnectionPopup()
            popup.open()

        try:
            update_check = git("pull")
            if "Already up to date." in update_check or "Already up-to-date." in update_check:
                popup = NoUpdatesPopup()
                popup.open()
            else:
                popup = UpdatingPopup()
                popup.open()

                def pip_install_and_shutdown():
                    os.system('pip install -r requirements.txt & reboot')

                threading.Timer(3.0, pip_install_and_shutdown).start()

        except Exception as e:
            print("failed to update")
            print(e)

        pass


class ListScreen(Screen):
    def read_file(self):
        self.manager.current = 'main'

    def button_call_back(self, value):
        self.manager.current = 'main'
        pass

    pass


class NoConnectionPopup(Popup):
    pass


class NoUpdatesPopup(Popup):
    pass


class UpdatingPopup(Popup):
    pass


class ScreenManagement(ScreenManager):
    try:
        host_name = os.popen('hostname -I').read()
    except:
        host_name = "Could not get ip"
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
    # os.system('python ' + os.getcwd() + '/WebApp/main.py &')
    CutterApp().run()
