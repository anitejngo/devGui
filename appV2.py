import os
os.environ['KIVY_GL_BACKEND'] = 'gl'
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.config import Config
from functools import partial
from serial import *
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty

Builder.load_string('''
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')


class ScrollableLabel(ScrollView):
    text = StringProperty('')


Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

serialPort = ""
try:
    serialPort = "/dev/ttyUSB0"
    baudRate = 9600
    ser = Serial(serialPort, baudRate, timeout=0, writeTimeout=0)
    serBuffer = ""
except:
    try:
        serialPort = "/dev/cu.usbserial-A600IP7D"
        baudRate = 9600
        ser = Serial(serialPort, baudRate, timeout=0, writeTimeout=0)
        serBuffer = ""
    except:
        print("faild to find arduino")
        sys.exit()


class YourApp(App):
    def __init__(self, **kwargs):
        super(YourApp, self).__init__(**kwargs)

        refresh_time = 0.5
        Clock.schedule_interval(self.read_serial, refresh_time)

    def read_serial(self, object):
        while True:
            c = ser.read()  # attempt to read a character from Serial
            # was anything read?
            if len(c) == 0:
                break

            # get the buffer from outside of this function
            global serBuffer

            # check if character is a delimeter
            if c == b'\r':
                c = ''  # don't want returns. chuck it
            if c == b'\n':
                serBuffer += "\n"  # add the newline to the buffer

                # add the line to the TOP of the log
                print(serBuffer)
                self.logger.text = serBuffer + '\r' + self.logger.text
                serBuffer = ""  # empty the buffer
            else:
                serBuffer += str(c)[2:-1]  # add to the buffer

    def start(self, object):
        value = self.output_label.text
        if int(value) > -1:
            command = "MC " + value + "\r"
            ser.write(command.encode())
            self.output_label.text = "0"
            self.last_cut.text = value
        else:
            self.logger.text = "Not valid input" + '\r' + self.logger.text

    def button_call_back(self, value, object):
        if value == '<':
            current_value = self.output_label.text
            if current_value != '0' and len(current_value) > 1:
                self.output_label.text = current_value[:-1]
            else:
                self.output_label.text = "0"
        else:
            current_value = self.output_label.text
            if current_value == '0':
                current_value = ""
            self.output_label.text = current_value + str(value)

    def build(self):

        root_widget = BoxLayout(orientation='vertical')
        label_widget = BoxLayout(orientation='horizontal')
        command_widget = BoxLayout(orientation='vertical', padding=[0, 50, 0, 0])
        log_widget = BoxLayout(orientation='vertical')

        self.output_label = Label(size_hint_y=1, text="0", font_size='50sp')
        self.last_cut = Label(size_hint_y=1, text="0", font_size='30sp')

        button_symbols = ('1', '2', '3',
                          '4', '5', '6',
                          '7', '8', '9',
                          '<', '0')

        button_grid = GridLayout(cols=3, size_hint_y=2)
        for symbol in button_symbols:
            dynamic_button = Button(text=symbol)
            dynamic_button.bind(
                on_press=partial(self.button_call_back, symbol))
            button_grid.add_widget(dynamic_button)

        start_button = Button(text='start', size_hint_y=None,
                              height=100)
        start_button.bind(
            on_press=partial(self.start))

        self.logger = ScrollableLabel(text="")

        log_widget.add_widget(self.logger)

        label_widget.add_widget(self.output_label)
        label_widget.add_widget(self.last_cut)
        root_widget.add_widget(label_widget)
        root_widget.add_widget(button_grid)
        command_widget.add_widget(start_button)
        command_widget.add_widget(log_widget)
        root_widget.add_widget(command_widget)

        return root_widget


YourApp().run()
