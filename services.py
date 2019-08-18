from serial import Serial
import csv
from PIL import Image, ImageDraw, ImageFont
import os


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


def print_label(value):
    try:
        filename = 'label.png'
        fnt = ImageFont.truetype('/assets/Lato-Regular.ttf', 200)
        img = Image.new('RGB', (696, 271), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 0), value, font=fnt, fill=(0, 0, 0))
        img.save(filename)
        os.system('sudo brother_ql -p usb://0x04f9:0x2042 -b pyusb --model QL-700 print -l 62x29 label.png')
    except Exception as E:
        print("Failed to print")
        print(E)
        pass


def shut_down_rasp():
    os.system('sudo shutdown -h now')
