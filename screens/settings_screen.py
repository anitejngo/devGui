from kivy.uix.screenmanager import Screen
import urllib
from sh import git
import threading
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
import os


class NoConnectionPopup(Popup):
    pass


class NoUpdatesPopup(Popup):
    pass


class UpdatingPopup(Popup):
    pass


store = JsonStore('config.json')


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
