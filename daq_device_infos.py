from imp import init_frozen
import nidaqmx



class NiDevices():
    def __init__(self):
        self.system = nidaqmx.system.System.local()

    def getDevices(self):
        devLst = ["Select device"]
        for dev in self.system.devices:
            devLst.append(str(dev.name))
        return devLst

    def getDevice(self,ix):
        if( ix>=len(self.system.devices) or ix < 0 ):
            return ""
        return str(self.system.devices[ix].name)

    def getChannelList(self,ix):
        chDat = ["Select device..."]
        if( ix>=len(self.system.devices) or ix < 0 ):
            return chDat
        chDat = ["Select channel..."]

        device = self.system.devices[ix]

        chDat = []

        for ch in device.ai_physical_chans:
            chDat.append( str(ch.name)  )

        return chDat

    def getTerminalConfig(self,ix_device,ix_ch):
        chTerm = ["..."]
        if( ix_device>=len(self.system.devices) or ix_device < 0 ):
            return chTerm
        
        device = self.system.devices[ix_device]
        chs = device.ai_physical_chans

        chTerm = ["....."]
        if( ix_ch>=len(chs) or ix_ch < 0 ):
            return chTerm
        chTerm = []

        ch = chs[ix_ch]
        for term in ch.ai_term_cfgs:
            s1 = str(term)
            ix = s1.find('.')
            if( ix != -1 ):
                chTerm.append(s1[ix+1:])
            else:
                chTerm.append(s1)

        return chTerm



    def getDeviceInfo(self,ix):
        
        info = "Info:\n"

        if( ix>=len(self.system.devices) or ix < 0 ):
            info += "Select device..."
            return info

        device = self.system.devices[ix]
        info += "Device: " + str(device.name) + "\n"

        info += "Max sample rate: " + str(device.ai_max_multi_chan_rate) + "Hz\n"

        info += "Channels:\n"

        # ? device.ai_meas_types
        for ch in device.ai_physical_chans:
            info +=  str(ch.name) + "  "
            for term in ch.ai_term_cfgs:
                s1 = str(term)
                ix = s1.find('.')
                if( ix != -1 ):
                    info +=  s1[ix+1:] + ","
                else:
                    info +=  s1 + ","
            info =  info[0:-1]
            info += "\n"
        
        return info