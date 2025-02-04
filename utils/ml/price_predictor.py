import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

class PricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, data, lookback=60):
        scaled_data = self.scaler.fit_transform(data['Close'].values.reshape(-1, 1))
        X, y = [], []
        
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
            
        return np.array(X), np.array(y)
        
    def build_model(self, lookback=60):
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
        
    def train(self, data, epochs=50, batch_size=32, lookback=60):
        X, y = self.prepare_data(data, lookback)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        self.model = self.build_model(lookback)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        
    def predict(self, data, lookback=60):
        last_sequence = data['Close'].values[-lookback:]
        scaled_sequence = self.scaler.transform(last_sequence.reshape(-1, 1))
        X = scaled_sequence.reshape(1, lookback, 1)
        
        predicted_scaled = self.model.predict(X)
        predicted_price = self.scaler.inverse_transform(predicted_scaled)[0][0]
        
        return predicted_price
        
    def save_model(self, path):
        self.model.save(path + 'model.h5')
        joblib.dump(self.scaler, path + 'scaler.pkl')
        
    def load_model(self, path):
        self.model = load_model(path + 'model.h5')
        self.scaler = joblib.load(path + 'scaler.pkl')
