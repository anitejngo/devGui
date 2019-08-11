from PIL import Image, ImageDraw, ImageFont
from kivy.uix.screenmanager import Screen
import os


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


class ListScreen(Screen):
    def read_file(self):
        self.manager.current = 'main'

    def button_call_back(self, value):
        self.manager.current = 'main'
        pass

    pass
