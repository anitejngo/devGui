import os
import GlobalShared
from screens import main_screen, offset_screen, settings_screen, list_screen
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from services import connect_to_cutter, on_windows

if on_windows():
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    Config.set('graphics','show_cursor','1')
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'fullscreen', '0')
else:
    os.environ['KIVY_GL_BACKEND'] = 'gl'
    Config.set('graphics','show_cursor','0')
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')

sm = ScreenManager()

Config.write()
serialBuffer = ''
store = JsonStore('config.json')


class ScreenManagement(ScreenManager):
    if store.exists('offset_label'):
        offset_label = StringProperty(store.get('offset_label')['value'])
    else:
        store.put('offset_label', value='0')
        offset_label = StringProperty("0")


class CutterApp(App):
    def __init__(self, **kwargs):
        super(CutterApp, self).__init__(**kwargs)
        GlobalShared.SERIAL_CONNECTION = connect_to_cutter()
        print("-----------")
        print("Connected to:")
        print(GlobalShared.SERIAL_CONNECTION)
        
        Clock.schedule_interval(self.read_serial, 1)

    def read_serial(self, object):
        if GlobalShared.SERIAL_CONNECTION:
            try:
                serial_message = str(GlobalShared.SERIAL_CONNECTION.readline())
                if serial_message:
                    if "CODE:MIR" in serial_message:
                        GlobalShared.MOTOR_IS_ROOTED = True

            except Exception as E:
                print("---------------------")
                print("Failed to read serial port msg")
                print(E)
                print("---------------------")
                GlobalShared.MOTOR_IS_ROOTED = False
                GlobalShared.SERIAL_CONNECTION = connect_to_cutter()

        else:
            GlobalShared.MOTOR_IS_ROOTED = False
            GlobalShared.SERIAL_CONNECTION = connect_to_cutter()

    def build(self):
        return Builder.load_file("screens/kivy.kv")


if __name__ == '__main__':
    CutterApp().run()
