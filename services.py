from serial import Serial


def connect_to_arduino(serial_port):
    return Serial(serial_port, 9600, timeout=0, writeTimeout=0)
