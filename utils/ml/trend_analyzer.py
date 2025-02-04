import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class TrendAnalyzer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        
    def create_features(self, df):
        # Technical indicators as features
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = self.calculate_rsi(df['Close'])
        df['MACD'] = self.calculate_macd(df['Close'])
        
        # Create target variable (1 for uptrend, 0 for downtrend)
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        return df
        
    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def calculate_macd(self, prices, fast=12, slow=26):
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        return exp1 - exp2
        
    def prepare_data(self, df):
        df = self.create_features(df)
        df = df.dropna()
        
        features = ['SMA_20', 'SMA_50', 'RSI', 'MACD']
        X = df[features]
        y = df['Target']
        
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y
        
    def train(self, df):
        X_scaled, y = self.prepare_data(df)
        self.model.fit(X_scaled, y)
        
    def predict_trend(self, df):
        df = self.create_features(df)
        features = ['SMA_20', 'SMA_50', 'RSI', 'MACD']
        X = df[features].tail(1)
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)
        probability = self.model.predict_proba(X_scaled)
        
        return {
            'trend': 'Uptrend' if prediction[0] == 1 else 'Downtrend',
            'confidence': probability[0][prediction[0]]
        }
