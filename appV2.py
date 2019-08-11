import os
from kivy.lang import Builder
from kivy.app import App
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.storage.jsonstore import JsonStore
from screens import main_screen, list_screen, settings_screen

os.environ['KIVY_GL_BACKEND'] = 'gl'
sm = ScreenManager()
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
serialConnection = None
serialBuffer = ''
store = JsonStore('config.json')


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
