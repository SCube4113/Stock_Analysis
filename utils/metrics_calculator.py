import pandas as pd
import numpy as np

class MetricsCalculator:
    @staticmethod
    def calculate_technical_indicators(df):
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['20dSTD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['MA20'] + (df['20dSTD'] * 2)
        df['Lower_Band'] = df['MA20'] - (df['20dSTD'] * 2)

        return df

    @staticmethod
    def format_large_number(num):
        """
        Format large numbers with proper handling for invalid inputs
        """
        if not isinstance(num, (int, float)) or pd.isna(num):
            return 'N/A'

        try:
            if num >= 1e12:
                return f'${num/1e12:.2f}T'
            elif num >= 1e9:
                return f'${num/1e9:.2f}B'
            elif num >= 1e6:
                return f'${num/1e6:.2f}M'
            else:
                return f'${num:,.2f}'
        except Exception:
            return 'N/A'

    @staticmethod
    def format_metric_value(value, metric_type='number'):
        """
        Format metric values with proper error handling
        """
        if pd.isna(value) or value is None:
            return 'N/A'

        try:
            if metric_type == 'price':
                return f"${float(value):.2f}"
            elif metric_type == 'percentage':
                return f"{float(value):.2f}%"
            elif metric_type == 'ratio':
                return f"{float(value):.2f}"
            else:
                return str(value)
        except (ValueError, TypeError):
            return 'N/A'