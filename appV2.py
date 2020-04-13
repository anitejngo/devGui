import os
import GlobalShared
from screens import main_screen, offset_screen, settings_screen
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from services import connect_to_cutter

os.environ['KIVY_GL_BACKEND'] = 'gl'
sm = ScreenManager()
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
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
        refresh_time = 0.5
        Clock.schedule_interval(self.read_serial, refresh_time)

    def read_serial(self, object):
        if GlobalShared.SERIAL_CONNECTION:
            try:
                serial_message = GlobalShared.SERIAL_CONNECTION.readline()
                if serial_message:
                    print("Serial message: " + serial_message)
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
    CutterApp().run()
