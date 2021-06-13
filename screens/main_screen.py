from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from threading import Timer
from services import shut_down_rasp
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
import GlobalShared
from services import construct_serial_message, print_label, reset_motor_to_root_position


class ShutDownPopup(Popup):
    def __init__(self, **kwargs):
        super(ShutDownPopup, self).__init__(**kwargs)   
        Window.bind(on_request_close=self.shut_down)

    def shut_down(self, *args):
        shut_down_rasp()   
        Window.close()      
    
    def close(self):
        self.dismiss()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        refresh_time = 0.5
        Clock.schedule_interval(self.check_connection, refresh_time)

    output_label = StringProperty("0")
    last_cut = StringProperty("0")
    serial_connection = BooleanProperty(True if GlobalShared.SERIAL_CONNECTION else False)
    motor_is_rooted = BooleanProperty(GlobalShared.MOTOR_IS_ROOTED)

    def check_connection(self, object):
        self.serial_connection = True if GlobalShared.SERIAL_CONNECTION else False
        self.motor_is_rooted = GlobalShared.MOTOR_IS_ROOTED

    def open_shut_down_popup(self):
        popup = ShutDownPopup()
        popup.open()

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

    def root_cutter(self):
        reset_motor_to_root_position()

    def start(self):
        serial_connection = GlobalShared.SERIAL_CONNECTION
        try:
            self.ids.start_button.disabled = True
            Timer(2, lambda: self.enable_start_button()).start()
            if serial_connection:
                value = self.output_label
                if value is "0":
                    serial_connection.write(construct_serial_message('CODE:MC 0'))
                    self.output_label = "0"
                    self.last_cut = "0"
                else:
                    last_cut = value
                    value = float(value) - float(self.manager.offset_label)
                    if value > -1:
                        serial_connection.write(construct_serial_message("CODE:MC " + str(value)))
                        print_label(str(last_cut))
                        self.output_label = "0"
                        self.last_cut = last_cut
                    else:
                        print('Not valid input')
            else:
                print("no serial connection")
        except Exception as e:
            print("Serial error")
            print(e)

    pass
