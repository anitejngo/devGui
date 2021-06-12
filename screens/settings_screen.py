from kivy.uix.screenmanager import Screen
import os
import urllib
#from sh import git
import threading
from kivy.uix.popup import Popup
import GlobalShared


class NoConnectionPopup(Popup):
    pass


class NoUpdatesPopup(Popup):
    pass


class UpdatingPopup(Popup):
    pass


class SettingsScreen(Screen):
    def root_motor(self):
        serial_connection = GlobalShared.SERIAL_CONNECTION
        command = "CODE:MRM \r\n"
        serial_connection.write(command.encode())
        print("Sending manual rooting command")

    def update(self):
        '''
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
'''
