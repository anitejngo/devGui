from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore


store = JsonStore('config.json')


class OffsetScreen(Screen):
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
