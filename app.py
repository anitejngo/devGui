from tkinter import Tk, Label, Button, Entry, Text, Scrollbar, RIGHT, Y, END
from serial import *
import numbers

serialPort = "/dev/cu.usbserial-A600IP7D"
baudRate = 9600
ser = Serial(serialPort, baudRate, timeout=0, writeTimeout=0)
serBuffer = ""


class GUI:
    def __init__(self, master):
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)

        self.label = Label(master, text="Duzina:")
        self.input = Entry(root)

        self.start_button = Button(master, text="Start", command=self.start)
        self.clear_button = Button(master, text="Obrisi", command=self.clear)

        scrollbar = Scrollbar(root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log = Text(root, width=60, height=10, borderwidth=2, relief="groove")
        self.log.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log.yview)

        self.close_button = Button(master, text="Izlaz", command=master.quit)

        self.label.pack()
        self.input.pack()
        self.input.focus_set()
        self.start_button.pack()
        self.clear_button.pack()
        self.log.pack()
        self.close_button.pack()
        root.after(500, self.read_serial)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        self.master.geometry(self._geom)
        self._geom = geom

    def start(self):
        value = self.input.get()
        if isinstance(int(value), numbers.Number):
            command = "MC " + value + "\r"
            ser.write(command.encode())
        else:
            print("not valid input")

    def clear(self):
        self.input.delete(0, END)

    def read_serial(self):
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
                self.log.insert('0.0', serBuffer)
                serBuffer = ""  # empty the buffer
            else:
                serBuffer += str(c)[2:-1]  # add to the buffer

        root.after(100, self.read_serial)


root = Tk()
my_gui = GUI(root)
root.mainloop()
