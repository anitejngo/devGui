from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
import os
import urllib
import threading
from services import reset_motor_to_root_position, on_windows
if not on_windows():
    from sh import git

class NoConnectionPopup(Popup):
    pass


class NoUpdatesPopup(Popup):
    pass


class UpdatingPopup(Popup):
    pass


class SettingsScreen(Screen):
    host_name = StringProperty("ip adresa")

    def root_motor(self):
        reset_motor_to_root_position()

    def get_host_name(self):
        self.host_name = socket.gethostbyname(socket.gethostname()) if on_windows() else  str(check_output(['hostname', '-I']))

    def update(self):
        if on_windows():
            print('No update on windows')
        else:    
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

