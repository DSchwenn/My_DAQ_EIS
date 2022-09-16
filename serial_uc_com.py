
import serial.tools.list_ports
import serial
import threading

import time

class SerialuCCom(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.serial = None
        self.stopSerialRead = False
        self.dataBuffer = []
        self.n_buffer = 0
        self.lastData = [0,0,0,0,0,0]
        self.inBuffer = []
        self.pauseReading = False
        self.isStarted = False
    
    def getPortList(self):
        portLst = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            portLst.append(port.device)
        if(len(ports)<1):
            portLst.append("No ports")
            return (portLst,False)
        return (portLst,True)

    def startSerialReading(self,port):
        # open connection if not opened yet
        # check if opened -> if not return False
        if( self.serial is None ):
            if( self.openConnection(port) == False ):
                return False
        # empty buffer
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.timeout = 5
        self.pauseReading = False
        if(not self.isStarted):
            self.start()
            self.isStarted = True
        return True

    def stopSerialReading(self):
        self.pauseReading = True
        self.resetData()

    def run(self):
        print("Start serial...")
        # read and store in data buffer
        # starts after new line with start sending - ends with newline; 1st = ms; next n = data n
        # Serial channels: ix
        # implement  datSer = self.ser_com.getData(self.ni_reader.bufferSize(),self.sampleInfo.getprocessSR())
        while( not self.stopSerialRead ):
            #for i in range(self.serial.in_waiting):
            #    b = self.serial.read()
            while(self.pauseReading):
                time.sleep(0.05)

            while(self.serial.in_waiting>0):
                # Read serial buffer
                lne = self.serial.readline()
                #print(lne)
                # check for complete data
                if( b'\n' not in lne ):
                    self.stopSerialRead = True
                    print("Serial read timeout - ending reading thread.")
                elif(lne[0] == 0x02):
                    # if ready, convert data and store to data buffer
                    numLst = lne[1:-1].split(b',')
                    nums = [int(s) for s in numLst if s.isdigit()]
                    self.dataBuffer.append(nums)
                    self.lastData = nums
                    self.n_buffer+=1
                    # if 1st character is 0x02 and last is \n, split along ",", convert numeric parts and store in buffer
            
            # pause...
            time.sleep(0.05)
        print("Exit serial...")

    def getData(self,daqBufferSize,calculateSampleRate):
        # return last data if buffer is empty
        if(len(self.dataBuffer)<1):
            dat = self.lastData
        elif(len(self.dataBuffer)<2):
            #  1 in buffer-> return and pop -> after last Data is returned
            dat = self.dataBuffer[0]
            self.dataBuffer = []
            self.n_buffer = 0
        else:
            #dt1 = daqBufferSize/calculateSampleRate
            #dt2 = self.dataBuffer[-1][0]-self.dataBuffer[0][0]
            dat = self.dataBuffer.pop(0)
            self.n_buffer -= 1

        # ...meh... TODO? interpolate buffered data accordingly:  (NN is ok)
        #  1st column is time in ms, daqBufferSize/calculateSampleRate is timeframe on which data in buffer is spread
        
        #  N in buffer: 
        # always returns one set of data
        return dat
    # TODO: after this: implement data distribution in ni data handler
    # Implement data sending opn uC


    def resetData(self):
        self.dataBuffer = []
        self.n_buffer = 0

    def openConnection(self,port):
        self.serial = serial.Serial()
        self.serial.baudrate = 115200
        self.serial.port = port
        try:
            self.serial.open()
        except serial.serialutil.SerialException:
            self.serial = None
            return False
            
        if(not self.serial.is_open):
           self.serial = None
        return self.serial.is_open


    
    def closeConnection(self):
        if( self.serial is None ):
            return
        if(self.serial.is_open):
            self.serial.close()
        self.serial = None
        self.pauseReading = True

    def killConnection(self):
        self.closeConnection()
        self.stopSerialRead = True



    def sendMessage(self,port,frequency,waveform,onOffRatio,leftRightPhase,brightR,brightG,brightB,stdF,stdOOR,stdBgt,flashMs):
        if( self.serial is None ):
            if( self.openConnection(port) == False ):
                return False
            else:
                time.sleep(0.15)
        txt = str((int)(frequency*100)) + "," + str(waveform) + "," + str((int)(onOffRatio*100)) + "," + str((int)(leftRightPhase*100)) + "," + str(brightR) + "," + str(brightG) + "," + str(brightB) + "," + str((int)(stdF)) + "," + str((int)(stdOOR)) + "," + str((int)(stdBgt)) + "," + str(flashMs) + "\n"

        print(txt)
        try:
            self.serial.write(txt.encode('utf-8'))
        except serial.serialutil.SerialException:
            self.closeConnection()
            return False
        return True

