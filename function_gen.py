import numpy as np

class FunctionGen:


    def __init__(self,f_list,phase_list,amplitude_list,v_pp):
        arr1inds = np.argsort(f_list,0)
        self.f_list = f_list[arr1inds]
        #print(arr1inds,"->",self.f_list)
        self.phase_list = phase_list[arr1inds]
        self.amplitude_list = amplitude_list[arr1inds]
        self.sampleRate = None
        self.signal = None
        self.n_max = 8190
        self.n_min = 50
        self.max_sr = 20000 # overrules n_min
        self.v_pp = v_pp
        self.calculateSignal()

    def calculateSignal(self):
        if(np.size(self.f_list)<1):
            return

        f_mn = self.f_list[0]
        f_mx = self.f_list[-1]
        self.sampleRate = f_mx*5
        n_samples = self.sampleRate/f_mn
        #print([self.sampleRate,n_samples])
        if(n_samples>self.n_max):
            n_samples = self.n_max
            self.sampleRate = n_samples*f_mn
        elif( n_samples<self.n_min ):
            n_samples = self.n_min  
            self.sampleRate = n_samples*f_mn
        #print([self.sampleRate,n_samples])
        if( self.sampleRate > self.max_sr ):
            self.sampleRate = self.max_sr
            n_samples = self.sampleRate/f_mn
        n_samples = np.int32(np.floor(n_samples))
        #print([self.sampleRate,n_samples])
        
        self.signal = np.zeros(shape=(1, n_samples))
        tt = np.linspace(0,n_samples/self.sampleRate,n_samples)
        #print("Samples: ",n_samples,np.size(self.signal),self.sampleRate,f_mn)

        #for (f,p,a) in zip(self.f_list,self.phase_list,self.amplitude_list):
        for i  in range(np.size(self.f_list)):
            drad = np.radians(self.phase_list [i])
            #print("add to sig:",i,self.f_list[i],self.phase_list[i],self.amplitude_list[i])
            self.signal = self.signal + np.sin(drad+2*np.pi*self.f_list[i]*tt) * self.amplitude_list[i]
        
        mx = np.max(np.abs(self.signal))
        self.signal = self.signal / mx * self.v_pp


    def set_f_list(self,f_list):
        self.f_list = np.sort(f_list)
        self.calculateSignal()

    def set_v_pp(self,v_pp):
        self.v_pp = v_pp
        self.calculateSignal()

    def set_sample_rate(self,sr):
        self.sampleRate = sr
        self.calculateSignal()

    def getDataSize(self):
        if(self.signal is None):
            return 1
        return self.signal.size

    def getSignal(self):
        return self.signal

    def getSampleRate(self):
        return self.sampleRate

    def get_f_list(self):
        return self.f_list

    def getNofF(self):
        return len(self.f_list)


# import matplotlib.pyplot as plt

# ff = np.array( [500.,1000.,100.,4000.] )
# pp = np.array( [0.,120.,180.,90.] )
# aa = np.array( [0.7,0.8,0.5,1.] )
# fg = FunctionGen(ff,pp,aa,2.)
# sig = fg.getSignal()
# print(np.size(sig))
# print(fg.getSampleRate())
# plt.plot(np.linspace(0,1,np.size(sig)),sig[0,:])
# plt.show()

