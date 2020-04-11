import os
import GlobalShared
from screens import main_screen, list_screen, offset_screen, settings_screen
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from services import connect_to_arduino

os.environ['KIVY_GL_BACKEND'] = 'gl'
sm = ScreenManager()
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
serialBuffer = ''
store = JsonStore('config.json')


def connect_to_cutter():
    try:
        return connect_to_arduino('/dev/ttyUSB0')
    except Exception as E:
        print("Could not connect rasp arduino!")
        print(E)
        try:
            return connect_to_arduino('/dev/cu.usbserial-A600IP7D')
        except Exception as E:
            print("Could not connect mac arduino 1")
            print(E)
            try:
                return connect_to_arduino('/dev/cu.usbserial-A4011SC4')
            except Exception as E:
                print(E)
                print("Could not connect mac arduino 2")


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
        GlobalShared.SERIAL_CONNECTION = connect_to_cutter()
        refresh_time = 0.5
        Clock.schedule_interval(self.read_serial, refresh_time)

    def read_serial(self, object):
        if GlobalShared.SERIAL_CONNECTION:
            try:
                serial_message = GlobalShared.SERIAL_CONNECTION.readline()  # attempt to read a character from Serial
                if serial_message:
                    print("Serial message:")
                    print(serial_message)
                    if "CODE:MIR" in serial_message:
                        GlobalShared.MOTOR_IS_ROOTED = True

            except:
                GlobalShared.MOTOR_IS_ROOTED = False
                GlobalShared.SERIAL_CONNECTION = connect_to_cutter()

        else:
            GlobalShared.MOTOR_IS_ROOTED = False
            GlobalShared.SERIAL_CONNECTION = connect_to_cutter()

    def build(self):
        return Builder.load_file("screens/kivy.kv")


if __name__ == '__main__':
    # os.system('python ' + os.getcwd() + '/WebApp/main.py &')
    CutterApp().run()
