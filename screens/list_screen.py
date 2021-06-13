from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty, ObjectProperty
from functools import partial
from kivy.clock import Clock
import socket
from subprocess import check_output
import GlobalShared
from services import construct_serial_message, print_label, on_windows
import csv
import os
import shortuuid
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

measurements = []
LATEST_CUT = {"id": "" ,"value":""}
OFFSET= '0'
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
        self.file_name = FILE_PATH.split("\\").pop() if FILE_PATH else "Izaberite Fajl"
        OFFSET = self.manager.offset_label
        self.last_list_cut =  str(LATEST_CUT["value"])

 
    def loadFile(self):
        self.open_file_popup()

    def open_file_popup(self):
        popup = OpenFilePopup(list_screen=ListScreen)
        popup.open()

    def calculate_from_csv(self):
        global measurements
        global LATEST_CUT
        global FILE_PATH
        LATEST_CUT = {"id": "" ,"value":""}
        measurements = []
        try:
            temp_measures = []
            with open(FILE_PATH, "r") as f:
                reader = csv.DictReader(f, delimiter=",")
                for index, row in enumerate(reader):
                    length = row['Length']   
                    repeat = row["Repeat"]
                    if 'x' in row['Repeat']:
                        measurements.append({"id": str(shortuuid.uuid()),"value": str(length)+" - "+str(repeat), 'layout':True})
                        layaout_repet = repeat[:-1]
                    if row["Length"] and row["Length"] != 'Length' and not "x" in row["Repeat"]:
                        for x in range(int(repeat)):
                            measurements.append({"id": str(shortuuid.uuid()),"value": str(length)})
            
            
        except Exception as e:
            print("Fail to open csv")
            print(e)
 
   


class RVMeasurements(RecycleView):
    def __init__(self, **kwargs):
        super(RVMeasurements, self).__init__(**kwargs)
        Clock.schedule_interval(self.refresh_data, 1)
        self.gen_data(measurements)

    def refresh_data(self,object):
        global measurements
        self.gen_data(measurements)

    def gen_data(self, data):
        done = "DONE        -       " 
        self.data = [{'text': "LAYOUT: "+x["value"] if 'layout' in x else (done if "done" in x else "") + str(x["value"]), 'on_release':  partial(self.on_press_layout, x) if 'layout' in x else partial(self.on_press,x), 'background_color': (1,0,0,1) if 'layout' in x else (0,1,0,1)} for x in data]

    def on_press_layout(self,x):
        pass

    def on_press(self,x):
        global LATEST_CUT
        global OFFSET
        LATEST_CUT  = x
        
        for n, i in enumerate(measurements):
            if i['id'] == x['id']:
                newVal = x
                newVal['done']='DONE'
                measurements[n] = newVal
        serial_connection = GlobalShared.SERIAL_CONNECTION
        if serial_connection:
            value = float(LATEST_CUT["value"]) - float(OFFSET)
            if value > -1:
                serial_connection.write(construct_serial_message("CODE:MC " + str(value)))
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
        except: pass      

        
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
