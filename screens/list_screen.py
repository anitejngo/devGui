from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty, ObjectProperty
from functools import partial
from kivy.clock import Clock
import socket
from subprocess import check_output
import GlobalShared
from services import construct_serial_message, print_label, print_label_and_description, on_windows
import csv
import os
import shortuuid
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup



measurements = []
LATEST_CUT = {"id": "", "value": ""}
OFFSET = '0'
FILE_PATH = ''
TEMP_FILE_PATH = ""


class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_label, 0.5)

    last_list_cut = StringProperty()
    file_name = StringProperty()

    def update_label(self, object):
        global LATEST_CUT
        global OFFSET
        global FILE_PATH
        self.file_name = FILE_PATH.split(
            "\\").pop() if FILE_PATH else "Izaberite Fajl"
        OFFSET = self.manager.offset_label
        self.last_list_cut = str(LATEST_CUT["value"])

    def loadFile(self):
        self.open_file_popup()

    def open_file_popup(self):
        popup = OpenFilePopup(list_screen=ListScreen)
        popup.open()

    def calculate_from_csv(self):
        global measurements
        global LATEST_CUT
        global FILE_PATH
        LATEST_CUT = {"id": "", "value": ""}
        measurements = []
        try:
            temp_measures = []
            with open(FILE_PATH) as csv_file:
               for row in csv.reader(csv_file, delimiter=','):
                    firstCol = str(row[0])
                    if 'Layout' in firstCol:
                        pass
                    elif '#' in firstCol:
                        pass
                    elif 'of' in firstCol:
                        measurements.append({"id": str(shortuuid.uuid()), "value": str(row[10])+" - "+str(row[11]), 'layout': True})
                    elif '' == firstCol:
                        pass
                    else:
                        measurements.append({"id": str(shortuuid.uuid()), "value": str(row[10]), 'description':  str(row[5]) if str(row[5])!= 'nan' else 'nan'})

        except Exception as e:
            print("Fail to open csv")
            print(e)


class RVMeasurements(RecycleView):
    def __init__(self, **kwargs):
        super(RVMeasurements, self).__init__(**kwargs)
        Clock.schedule_interval(self.refresh_data, 1)
        self.gen_data(measurements)

    def refresh_data(self, object):
        global measurements
        self.gen_data(measurements)

    def if_has_property(self, x, property):
        return property in x

    def genrate_done_message(self):
        return "DONE        -       "

    def generate_layout_message(self, x):
        return "LAYOUT: " + x["value"]

    def generate_text(self, x):
        return self.generate_layout_message(x) if self.if_has_property(x, 'layout') else (self.genrate_done_message() if self.if_has_property(x, 'done') else "") + str(x["value"] + (("    |    " + str(x['description'])) if self.if_has_property(x, 'description') and str(x['description']) is not '' else ""))

    def generat_on_release(self, x):
        return partial(self.on_press_layout, x) if self.if_has_property(x, 'layout') else partial(self.on_press, x)

    def generate_background_color(self, x):
        return (1, 0, 0, 1) if self.if_has_property(x, 'layout') else (0, 1, 0, 1)

    def generate_description(self, x):
        return x['description'] if self.if_has_property(x, 'description') else ''

    def gen_data(self, data):
        self.data = [{'text': self.generate_text(x), 'on_release': self.generat_on_release(
            x), 'background_color': self.generate_background_color(x), ' ': self.generate_description(x)} for x in data]

    def on_press_layout(self, x):
        pass

    def on_press(self, x):
        global LATEST_CUT
        global OFFSET
        LATEST_CUT = x

        for n, i in enumerate(measurements):
            if i['id'] == x['id']:
                newVal = x
                newVal['done'] = 'DONE'
                measurements[n] = newVal
        serial_connection = GlobalShared.SERIAL_CONNECTION
        if serial_connection:
            value = float(LATEST_CUT["value"]) - float(OFFSET)
            if value > -1:
                serial_connection.write(
                    construct_serial_message("CODE:MC " + str(value)))
                if LATEST_CUT['description']:
                    print_label_and_description(
                        str(LATEST_CUT["value"]), str(LATEST_CUT["description"]))
                else:
                    print_label(str(LATEST_CUT["value"]))
            else:
                print('Not valid input')
        else:
            print("no serial connection")


class Filechooser(BoxLayout):
    def select(self, *args):
        try:
            global TEMP_FILE_PATH
            TEMP_FILE_PATH = args[1][0]
        except:
            pass


class OpenFilePopup(Popup):
    list_screen = ObjectProperty()

    def __init__(self, **kwargs):
        super(OpenFilePopup, self).__init__(**kwargs)

    def consume_file(self):
        global FILE_PATH
        global TEMP_FILE_PATH
        FILE_PATH = TEMP_FILE_PATH
        self.list_screen.calculate_from_csv(self.list_screen)
        self.dismiss()

    def close(self):
        self.dismiss()
