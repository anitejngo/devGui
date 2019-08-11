from kivy.uix.screenmanager import Screen


class ListScreen(Screen):
    def read_file(self):
        self.manager.current = 'main'

    def button_call_back(self, value):
        self.manager.current = 'main'
        pass

    pass
