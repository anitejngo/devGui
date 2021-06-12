from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty
from functools import partial
from kivy.clock import Clock
import socket
from subprocess import check_output
import GlobalShared
from services import construct_serial_message, print_label, on_windows
import csv

#[{"id": "1", "value":"100"},{'id': "2", "value":"200"},{'id': "3", "value":"300"}]
measurements = []
LATEST_CUT = {"id": "" ,"value":""}
OFFSET= '0'


class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_label, 0.5)
    
    last_list_cut = StringProperty()
    host_name = StringProperty()

    def update_label(self, object):
        global LATEST_CUT
        global OFFSET
        OFFSET = self.manager.offset_label
        self.last_list_cut =  str(LATEST_CUT["value"])
        if on_windows():
            self.host_name = socket.gethostbyname(socket.gethostname())
        else:
            self.host_name = check_output(['hostname', '-I'])

    def loadFile(self):
        global measurements
        try:
            temp_measures = []
            file_location = ''
            if on_windows():
                file_location = 'orders\stok.csv'
            else:
                file_location = '../orders/stock.csv'

            with open(file_location, "r") as f:
                reader = csv.DictReader(f, delimiter=",")
                for index, row in enumerate(reader):
                    if row["Length"] and row["Length"] != 'Length' and not "x" in row["Repeat"]:
                        length = row['Length']   
                        repeat = row["Repeat"]
                        for x in range(int(repeat)):
                            measurements.append({"id": str(index),"value": str(length)})
          
            
        except Exception as e:
            print("Fail to open csv")
            print(e)

        pass



class RVMeasurements(RecycleView):
    def __init__(self, **kwargs):
        super(RVMeasurements, self).__init__(**kwargs)
        Clock.schedule_interval(self.refresh_data, 1)
        self.genData(measurements)

    def refresh_data(self,object):
        global measurements
        print(measurements)
        self.genData(measurements)

    def genData(self, data):
        self.data = [{'text': ("DONE        -       " if "done" in x else "") + str(x["value"]), 'on_release':  partial(self.on_press, x)} for x in data]

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
            if LATEST_CUT['value'] is "0":
                serial_connection.write(construct_serial_message('CODE:MC 0'))
            else:
                value = float(LATEST_CUT["value"]) - float(OFFSET)
                if value > -1:
                    serial_connection.write(construct_serial_message("CODE:MC " + str(value)))
                    print_label(str(value))
                else:
                    print('Not valid input')
        else:
            print("no serial connection")


   

      


