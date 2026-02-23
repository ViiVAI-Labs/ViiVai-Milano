## Copyrighted by ViiVAI Labs and Studio 2025

import serial
from time import sleep, time
import numpy as np


class CR_RP2040W:
    def __init__(self, port='/dev/tty.usbmodem101', baudrate=115200, timeout=1):
        self.timeout = timeout
        self.port = port
        try:
            self.HapticDevice = serial.Serial(port=port,baudrate=baudrate,timeout=self.timeout)
            print(f"Initialize Comfort Research Haptic Device. Connected to {port}")
            self.reset()
            
        except serial.SerialException as e:
            print(f"Error: {e}")
            self.HapticDevice = None
        
    def disconnect(self):
        if self.HapticDevice.is_open and self.HapticDevice:
            self.HapticDevice.close()
            print(f"serial port {self.port} closed")
    
    def reset(self):
        self.HapticDevice.flush()
        self.sendSerialStr('##09-') 

    def sendSerialStr(self, sstring, index=1): ## index is to print outputs
        msg = '' + sstring 
        if index: print(f'\n Writing {msg}')
        self.HapticDevice.write(msg.encode())

        if index: print(self.HapticDevice.readline())
        else: msg=self.HapticDevice.readline()
        msg=self.HapticDevice.readline()

        msg=msg[:-2].decode()
        if index: print(msg)
        self.HapticDevice.flushInput()

    def DirectHaptics(self, act_array, index=1):
        msg = '##20'
        for i, act in enumerate(act_array):
            msg += str(i) + ',' + str(int(act)) + ','
        msg += '-'
        self.sendSerialStr(msg, index=index) 



if __name__ == "__main__":
    print('stating the test code')
    start_time = time()

    HapticDevice = CR_RP2040W()
    sleep(0.2)

    act = 500*np.ones(6) # act = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
    HapticDevice.DirectHaptics(act)
    sleep(2)
    act = 0*np.ones(6)
    HapticDevice.DirectHaptics(act, index=0)
    HapticDevice.disconnect()

    print('program ends')
    print(time() - start_time)



