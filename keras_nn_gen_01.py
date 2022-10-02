

from sklearn.preprocessing import MinMaxScaler, StandardScaler

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, CuDNNLSTM
from keras.layers import Dropout
from keras import optimizers, losses, metrics


from datetime import datetime

class KerasNNGenerator():
    def __init__(self):
        self.nn_model = None
        self.path = ".\\NNModelData\\"
        self.filename = ""
        self.cellnum = 64
        self.layernum = 4
        self.dropout = 0.2
        self.inputShape = [0,0]
        self.outNum = 0
        

    def createNeuralNet(self, inputShape, outputNum):
        # inputShape: [timesamples, inputs]
        self.inputShape = inputShape
        self.outNum = outputNum

        # Training The LSTM
        model = Sequential()
        

        # Creating LSTM and Dropout Layers
        if(self.layernum>1 ):
            model.add(LSTM(units=self.cellnum , return_sequences=True, input_shape=(inputShape[0], inputShape[1])))
        else:
            model.add(LSTM(units=self.cellnum , input_shape=(inputShape[0], inputShape[1])))
        model.add(Dropout(self.dropout))

        if(self.layernum>2 ):
            for i in range(1,self.layernum-1):
                    model.add(LSTM(units=self.cellnum , return_sequences=True)) # ,activation='relu'
                    model.add(Dropout(0.2))
        
        if(self.layernum>1 ):
            model.add(LSTM(units=self.cellnum)) # ,activation='relu'
            model.add(Dropout(0.2))

        # Creating Dense Layer
        model.add(Dense(units = outputNum)) # ,activation='softmax'

        # Model Compilation
        #model.compile(optimizer = 'adam', loss = 'mean_squared_error')
        model.compile(optimizer=optimizers.Adam(learning_rate=1e-3,decay=1e-5),
              loss=losses.MeanSquaredError()) 
              #metrics=[metrics.BinaryAccuracy(),metrics.FalseNegatives()])

        self.nn_model = model


    def setCellNumber(self,num):
        self.cellnum = num

    def setLayerNumber(self,num):
        self.layernum = num

    def setDropoutNumber(self,num):
        self.dropout = num


    def saveNeuralNet(self):
        if(self.nn_model is None):
            return

        self.filename = self.generateFileName()
        self.nn_model.save(self.filename)
        return self.filename


    def generateFileName(self):
        now = datetime.now() 
        date_time = now.strftime("%Y%m%d_%H%M%S")
        fn = self.path + date_time + str(self.layernum ) + "_" + str(self.cellnum ) + "_" + str(self.dropout ) + "_" + str(self.inputShape) + "_" + str(self.outNum) + ".nn_model"
        return fn

    
    
