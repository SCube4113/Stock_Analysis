import websocket
import json
import pandas as pd
from datetime import datetime
import streamlit as st
from threading import Thread
import time

class StockWebSocket:
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.current_symbols = set()
        
    def connect(self):
        self.ws = websocket.WebSocketApp(
            "wss://ws.finnhub.io?token=cugvb19r01qr6jndqv40cugvb19r01qr6jndqv4g",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
    def start(self):
        Thread(target=self.ws.run_forever).start()
        
    def subscribe(self, symbol):
        if self.is_connected and symbol not in self.current_symbols:
            self.ws.send(json.dumps({'type': 'subscribe', 'symbol': symbol}))
            self.current_symbols.add(symbol)
            
    def unsubscribe(self, symbol):
        if self.is_connected and symbol in self.current_symbols:
            self.ws.send(json.dumps({'type': 'unsubscribe', 'symbol': symbol}))
            self.current_symbols.remove(symbol)
            
    def on_message(self, ws, message):
        data = json.loads(message)
        if 'data' in data:
            for item in data['data']:
                if 'p' in item:  # price
                    symbol = item['s']
                    price = item['p']
                    timestamp = datetime.fromtimestamp(item['t']/1000)
                    
                    # Update Streamlit session state
                    if 'real_time_prices' not in st.session_state:
                        st.session_state.real_time_prices = {}
                    st.session_state.real_time_prices[symbol] = {
                        'price': price,
                        'timestamp': timestamp
                    }
                    
    def on_error(self, ws, error):
        print(f"Error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        print("WebSocket connection closed")
        
    def on_open(self, ws):
        self.is_connected = True
        print("WebSocket connection established")
