from serial import Serial
import csv


def connect_to_arduino(serial_port):
    return Serial(serial_port, 9600, timeout=0, writeTimeout=0)


def parse_csv_cutting_list(path_to_csv):
    input_dict = csv.DictReader(open(path_to_csv))
    dict_you_want = []

    # remove empty data
    for data in input_dict:
        if data['Layout'] not in ['', '#', 'Layout']:
            dict_you_want.append(data)

    # merge cuttings to
    layouts = []
    temp = []
    for data in dict_you_want:
        if 'of' in data['Layout']:
            temp = [data]
            layouts.append(temp)
        else:
            temp.append(data)

    return layouts
