from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from threading import Timer
from services import connect_to_arduino, print_label, shut_down_rasp
from kivy.uix.popup import Popup


class ShutDownPopup(Popup):
    pass


serialConnection = None
try:
    serialConnection = connect_to_arduino('/dev/ttyUSB0')
except Exception as E:
    print("Could not connect rasp arduino!")
    try:
        serialConnection = connect_to_arduino('/dev/cu.usbserial-A600IP7D')
    except Exception as E:
        print("Could not connect mac arduino 1")

        try:
            serialConnection = connect_to_arduino('/dev/cu.usbserial-A4011SC4')
        except Exception as E:
            print("Could not connect mac arduino 2")


class MainScreen(Screen):
    output_label = StringProperty("0")
    last_cut = StringProperty("0")

    def open_shut_down_popup(self):
        popup = ShutDownPopup()
        popup.open()
        pass

    def shut_down(self):
        shut_down_rasp()
        pass

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

    def start(self):
        try:
            self.ids.start_button.disabled = True
            Timer(2, lambda: self.enable_start_button()).start()
            if serialConnection:
                value = self.output_label
                if value is "0":
                    command = "MC 0\r\n"
                    serialConnection.write(command.encode())
                    self.output_label = "0"
                    self.last_cut = "0"
                else:
                    last_cut = value
                    value = float(value) - float(self.manager.offset_label)
                    if value > -1:
                        command = "MC " + str(value) + "\r\n"
                        serialConnection.write(command.encode())
                        # printing removed temp
                        #print_label(self.output_label)
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
