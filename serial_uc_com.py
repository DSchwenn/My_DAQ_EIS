
import serial.tools.list_ports
import serial

import time

class SerialuCCom:
    def __init__(self):
        self.serial = None
    
    def getPortList(self):
        portLst = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            portLst.append(port.device)
        if(len(ports)<1):
            portLst.append("No ports")
            return (portLst,False)
        return (portLst,True)

    def openConnection(self,port):
        self.serial = serial.Serial()
        self.serial.baudrate = 115200
        self.serial.port = port
        self.serial.open()
        if(not self.serial.is_open):
           self.serial = None
        return self.serial.is_open


    
    def closeConnection(self):
        if( self.serial is None ):
            return
        if(self.serial.is_open):
            self.serial.close()
        self.serial = None


    def sendMessage(self,port,frequency,waveform,onOffRatio,leftRightPhase,brightR,brightG,brightB):
        if( self.serial is None ):
            if( self.openConnection(port) == False ):
                return False
            else:
                time.sleep(0.15)
        txt = str((int)(frequency*100)) + "," + str(waveform) + "," + str((int)(onOffRatio*100)) + "," + str((int)(leftRightPhase*100)) + "," + str(brightR) + "," + str(brightG) + "," + str(brightB) + "\n"
        print(txt)
        self.serial.write(txt.encode('utf-8'))

        