from tkinter import Tk, Label, Button, Text
from serial import *
import sys

serialPort = ""
try:
    serialPort = "/dev/ttyUSB0"
    baudRate = 9600
    ser = Serial(serialPort, baudRate, timeout=0, writeTimeout=0)
    serialBuffer = ""
except:
    try:
        serialPort = "/dev/cu.usbserial-A600IP7D"
        baudRate = 9600
        ser = Serial(serialPort, baudRate, timeout=0, writeTimeout=0)
        serialBuffer = ""
    except:
        print("faild to find arduino")
        sys.exit()


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.geometry('800x480')
        self.master.attributes("-fullscreen", True)

        self.label = Label(master, text="Duzina:", font=("Courier", 20))
        self.input_label = Label(master, text="0", font=("Courier", 20))

        self.start_button = Button(master, text="Start", command=self.start, width=10)
        self.clear_button = Button(master, text="Obrisi", command=self.clear, width=10)

        self.one_button = Button(master, text="1", command=lambda: self.button_press(1), width=10)
        self.two_button = Button(master, text="2", command=lambda: self.button_press(2), width=10)
        self.three_button = Button(master, text="3", command=lambda: self.button_press(3), width=10)

        self.four_button = Button(master, text="4", command=lambda: self.button_press(4), width=10)
        self.five_button = Button(master, text="5", command=lambda: self.button_press(5), width=10)
        self.six_button = Button(master, text="6", command=lambda: self.button_press(6), width=10)

        self.seven_button = Button(master, text="7", command=lambda: self.button_press(7), width=10)
        self.eight_button = Button(master, text="8", command=lambda: self.button_press(8), width=10)
        self.nine_button = Button(master, text="9", command=lambda: self.button_press(9), width=10)

        self.del_button = Button(master, text="<", command=self.delete, width=10)
        self.zero_button = Button(master, text="0", command=lambda: self.button_press(0), width=10)
        self.clear_button = Button(master, text="Clear", command=self.clear, width=10)

        self.log = Text(root, width=90, height=10, borderwidth=2, relief="groove")

        self.label.grid(row=1, column=1, pady=(5, 0))
        self.input_label.grid(row=1, column=2, pady=(5, 0))

        self.one_button.grid(row=2, column=1, padx=(10, 10), pady=(20, 20))
        self.two_button.grid(row=2, column=2, padx=(10, 10), pady=(20, 20))
        self.three_button.grid(row=2, column=3, padx=(10, 10), pady=(20, 20))

        self.four_button.grid(row=3, column=1, padx=(10, 10), pady=(20, 20))
        self.five_button.grid(row=3, column=2, padx=(10, 10), pady=(20, 20))
        self.six_button.grid(row=3, column=3, padx=(10, 10), pady=(20, 20))

        self.seven_button.grid(row=4, column=1, padx=(10, 10), pady=(20, 20))
        self.eight_button.grid(row=4, column=2, padx=(10, 10), pady=(20, 20))
        self.nine_button.grid(row=4, column=3, padx=(10, 10), pady=(20, 20))

        self.del_button.grid(row=5, column=1, padx=(10, 10), pady=(20, 20))
        self.zero_button.grid(row=5, column=2, padx=(10, 10), pady=(20, 20))
        self.clear_button.grid(row=5, column=3, padx=(10, 10), pady=(20, 20))

        self.start_button.grid(row=6, column=2, padx=(30, 10), pady=(20, 20))
        self.log.grid(row=7, column=1, columnspan=3, padx=(50, 10))

        root.after(500, self.read_serial)

    def start(self):
        value = self.input_label.cget("text")
        if int(value) > -1:
            command = "MC " + value + "\r"
            ser.write(command.encode())
        else:
            self.log.insert('0.0', "Not valid input")

    def clear(self):
        self.input_label.config(text="0")

    def delete(self):
        current_value = self.input_label.cget("text")
        if current_value != '0' and len(current_value) > 1:
            self.input_label.config(text=current_value[:-1])
        else:
            self.input_label.config(text="0")

    def button_press(self, value):
        current_value = self.input_label.cget("text")
        if current_value == '0':
            current_value = ""
        self.input_label.config(text=current_value + str(value))

    def read_serial(self):
        while True:
            c = ser.read()  # attempt to read a character from Serial
            # was anything read?
            if len(c) == 0:
                break

            # get the buffer from outside of this function
            global serialBuffer

            # check if character is a delimeter
            if c == b'\r':
                c = ''  # don't want returns. chuck it
            if c == b'\n':
                serBuffer += "\n"  # add the newline to the buffer

                # add the line to the TOP of the log
                self.log.insert('0.0', serBuffer)
                serBuffer = ""  # empty the buffer
            else:
                serBuffer += str(c)[2:-1]  # add to the buffer

        root.after(100, self.read_serial)


root = Tk()
my_gui = GUI(root)
root.mainloop()
