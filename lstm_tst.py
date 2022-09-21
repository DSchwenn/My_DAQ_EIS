
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import MinMaxScaler, StandardScaler

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

# Separate data recording for training
# Normalization: what does make sense? Phase min/max; Acc/ HR min/max; FFT ABS relative (division)? Source FFT...?
# save normalization method with model?
# Normalize per input step somehow?
# CuDNNLSTM for faster training?
# thread for regular training on new dataset
# script to create and save NN model for UI to load (input size must correspond to selected channel)
# limit training set by time?
# class/ function called to train in thread (CUDA?)
# script to re-train with recorded data

# https://stackabuse.com/time-series-analysis-with-lstm-using-pythons-keras-library/

apple_training_complete = pd.read_csv(r'AAPL.csv')
#apple_training_processed = apple_training_complete.iloc[:, 1:2].values
apple_training_processed = apple_training_complete.iloc[:, [1,4]].values

# Data Normalization


scaler = MinMaxScaler(feature_range = (0, 1))
apple_training_scaled = scaler.fit_transform(apple_training_processed)


# # create scaler
# scaler = StandardScaler()
# # fit and transform in one step
# apple_training_scaled = scaler.fit_transform(apple_training_processed)
# # inverse transform
# #apple_training_scaled = scaler.inverse_transform(apple_training_scaled)


# Convert Training Data to Right Shape
use_last_n = 60
features_set = []
labels = []
for i in range(3000,4800):
    features_set.append(apple_training_scaled[i-use_last_n:i, :])
    labels.append(apple_training_scaled[i, 0])

features_set, labels = np.array(features_set), np.array(labels)

features_set = np.reshape(features_set, (features_set.shape[0], features_set.shape[1], features_set.shape[2]))



# Training The LSTM
model = Sequential()

# Creating LSTM and Dropout Layers
model.add(LSTM(units=50, return_sequences=True, input_shape=(features_set.shape[1], features_set.shape[2])))
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True)) # ,activation='relu'
model.add(Dropout(0.2))

model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))

model.add(LSTM(units=50))
model.add(Dropout(0.2))


# Creating Dense Layer

model.add(Dense(units = 2)) # ,activation='softmax'


# Model Compilation

model.compile(optimizer = 'adam', loss = 'mean_squared_error')  # learning rate lr=1e-3, decay=1e-5; loss='sparse_categorical_crossentropy'

# Algorithm Training

model.fit(features_set, labels, epochs = 10, batch_size = 32)

## Testing LSTM
apple_testing_complete = pd.read_csv(r'AAPL.csv')
apple_testing_processed = apple_testing_complete.iloc[:, [1,4]].values

# # Converting Test Data to Right Format
# apple_total = pd.concat((apple_training_complete['Open'], apple_testing_complete['Open']), axis=0)
# test_inputs = apple_total[len(apple_total) - len(apple_testing_complete) - use_last_n:].values
# test_inputs = test_inputs.reshape(-1,1)


test_inputs = scaler.transform(apple_testing_processed)

test_features = []
for i in range(3000, 5500):
    test_features.append(test_inputs[i-use_last_n:i, :])

test_features = np.array(test_features)
test_features = np.reshape(test_features, (test_features.shape[0], test_features.shape[1], test_features.shape[2]))

# Making Predictions

predictions = model.predict(test_features)

predictions = scaler.inverse_transform(predictions)

plt.figure(figsize=(10,6))
plt.plot(apple_testing_processed[3000:,:], label='Actual Apple Stock Price')
plt.plot(predictions, label='Predicted Apple Stock Price')
plt.title('Apple Stock Price Prediction')
plt.xlabel('Date')
plt.ylabel('Apple Stock Price')
plt.legend()
plt.show()