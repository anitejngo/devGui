from serial import Serial
from PIL import Image, ImageDraw, ImageFont
import os
import serial.tools.list_ports

def getArduino():
    return "/dev/"+os.popen("dmesg | egrep ttyACM | cut -f3 -d: | tail -n1").read().strip() 

def connect_to_cutter():
    try:
        usb_device=getArduino()
        print("============= FOUND USB DEVICE")
        print(usb_device)
        print("=============")
        return open_serial_to_cutter(usb_device)
    except Exception as E:
        print("Could not connect to:" + usb_device)
        print(E)


def open_serial_to_cutter(serial_port):
    return Serial(serial_port, 9600, timeout=0, writeTimeout=0)


def construct_serial_message(message):
    return (message + ' \r\n').encode()


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
