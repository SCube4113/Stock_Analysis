import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

class StockDataFetcher:
    @staticmethod
    def get_symbol_suffix(symbol: str, market: str) -> str:
        """Add appropriate suffix based on market type"""
        if market == "Indian Stocks (NSE/BSE)":
            if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
                return f"{symbol}.NS"  # Default to NSE
        elif market == "Cryptocurrency":
            if not symbol.endswith('-USD'):
                return f"{symbol}-USD"
        elif market == "Commodities":
            if not symbol.endswith('=F'):
                return f"{symbol}=F"
        return symbol

    @staticmethod
    def search_stock_symbols(query: str, market: str) -> list:
        """Search for symbols based on market type"""
        suggestions = []
        
        if market == "Global Stocks":
            # Basic global stock suggestions
            global_stocks = {
                'AAPL': 'Apple Inc.',
                'MSFT': 'Microsoft Corporation',
                'GOOGL': 'Alphabet Inc.',
                'AMZN': 'Amazon.com Inc.',
                'META': 'Meta Platforms Inc.',
                'TSLA': 'Tesla Inc.',
                'NVDA': 'NVIDIA Corporation',
            }
            suggestions.extend([
                {'symbol': sym, 'name': name, 'exchange': 'NASDAQ/NYSE'}
                for sym, name in global_stocks.items()
                if query in sym or query.lower() in name.lower()
            ])

        elif market == "Indian Stocks (NSE/BSE)":
            # Indian stock suggestions
            indian_stocks = {
                'RELIANCE.NS': 'Reliance Industries',
                'TCS.NS': 'Tata Consultancy Services',
                'INFY.NS': 'Infosys Limited',
                'HDFCBANK.NS': 'HDFC Bank Limited',
                'WIPRO.NS': 'Wipro Limited',
                'TATAMOTORS.NS': 'Tata Motors Limited',
            }
            suggestions.extend([
                {'symbol': sym, 'name': name, 'exchange': 'NSE'}
                for sym, name in indian_stocks.items()
                if query in sym.replace('.NS', '') or query.lower() in name.lower()
            ])

        elif market == "Cryptocurrency":
            # Crypto suggestions
            crypto = {
                'BTC-USD': 'Bitcoin USD',
                'ETH-USD': 'Ethereum USD',
                'USDT-USD': 'Tether USD',
                'BNB-USD': 'Binance Coin USD',
                'XRP-USD': 'Ripple USD',
                'DOGE-USD': 'Dogecoin USD',
            }
            suggestions.extend([
                {'symbol': sym, 'name': name, 'exchange': 'Crypto'}
                for sym, name in crypto.items()
                if query in sym.replace('-USD', '') or query.lower() in name.lower()
            ])

        elif market == "Commodities":
            # Commodity suggestions
            commodities = {
                'GC=F': 'Gold Futures',
                'SI=F': 'Silver Futures',
                'CL=F': 'Crude Oil Futures',
                'NG=F': 'Natural Gas Futures',
                'ZC=F': 'Corn Futures',
                'ZW=F': 'Wheat Futures',
            }
            suggestions.extend([
                {'symbol': sym, 'name': name, 'exchange': 'Commodities'}
                for sym, name in commodities.items()
                if query in sym.replace('=F', '') or query.lower() in name.lower()
            ])

        return suggestions[:10]  # Limit to top 10 suggestions

    @staticmethod
    def get_historical_data(symbol: str, period: str = '1mo', interval: str = '1d') -> pd.DataFrame:
        """Fetch historical data for any market type"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
                
            return df
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    @staticmethod
    def get_current_price(symbol: str) -> float:
        """Get current price for any market type"""
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info.get('regularMarketPrice', 0.0)
        except:
            return 0.0

    @staticmethod
    def get_market_status(market: str) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        
        if market == "Cryptocurrency":
            # Crypto markets are always open
            return True
            
        elif market == "Indian Stocks (NSE/BSE)":
            # NSE/BSE market hours (IST: 9:15 AM - 3:30 PM, Mon-Fri)
            if now.weekday() >= 5:  # Weekend
                return False
            india_time = now + timedelta(hours=5, minutes=30)  # Convert to IST
            market_open = india_time.replace(hour=9, minute=15)
            market_close = india_time.replace(hour=15, minute=30)
            return market_open <= india_time <= market_close
            
        elif market == "Global Stocks":
            # US market hours (EST: 9:30 AM - 4:00 PM, Mon-Fri)
            if now.weekday() >= 5:  # Weekend
                return False
            est_time = now - timedelta(hours=4)  # Convert to EST
            market_open = est_time.replace(hour=9, minute=30)
            market_close = est_time.replace(hour=16, minute=0)
            return market_open <= est_time <= market_close
            
        elif market == "Commodities":
            # Simplified check for commodities (actual hours vary by commodity)
            if now.weekday() >= 5:  # Weekend
                return False
            return True
            
        return False

    @staticmethod
    def _try_fetch_data(symbol, period='1mo'):
        """Helper method to try fetching data for a symbol with detailed error logging"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if not data.empty:
                return True, None
            return False, "No data available"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_valid_symbol(symbol):
        """Get the valid symbol with appropriate suffix for Indian stocks"""
        # If already has suffix, return as is
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return symbol

        # Special cases for Indian stocks
        special_cases = {
            'IRCTC': ['IRCTC.NS', 'IRCTC.BO'],
            'NIFTY50': ['^NSEI'],
            'SENSEX': ['^BSESN']
        }

        if symbol in special_cases:
            for special_symbol in special_cases[symbol]:
                success, error = StockDataFetcher._try_fetch_data(special_symbol)
                if success:
                    return special_symbol

        # For Indian stocks, try both exchanges
        if any(char.isdigit() for char in symbol) or any(s in symbol for s in ['&', '-']):
            # Try NSE first (more common)
            nse_symbol = f"{symbol}.NS"
            success, error = StockDataFetcher._try_fetch_data(nse_symbol)
            if success:
                return nse_symbol

            # Try BSE if NSE fails
            bse_symbol = f"{symbol}.BO"
            success, error = StockDataFetcher._try_fetch_data(bse_symbol)
            if success:
                return bse_symbol

            return nse_symbol  # Default to NSE if both fail

        return symbol  # For global stocks, return as is

    @staticmethod
    def get_stock_info(symbol):
        """Fetch stock info with proper suffix handling for Indian stocks"""
        try:
            ticker_symbol = StockDataFetcher.get_valid_symbol(symbol)
            stock = yf.Ticker(ticker_symbol)
            info = stock.info

            # If NSE fails, try BSE
            if (not info or len(info) == 0) and ticker_symbol.endswith('.NS'):
                bse_symbol = symbol.replace('.NS', '.BO')
                stock = yf.Ticker(bse_symbol)
                info = stock.info

            # Verify we have valid info
            if not info or len(info) == 0:
                raise Exception(f"No valid information found for {symbol}")

            return info
        except Exception as e:
            raise Exception(f"Error fetching stock info for {symbol}: {str(e)}")

    @staticmethod
    def get_key_metrics(symbol):
        try:
            ticker_symbol = StockDataFetcher.get_valid_symbol(symbol)
            stock = yf.Ticker(ticker_symbol)
            info = stock.info

            # If NSE fails, try BSE
            if (not info or len(info) == 0) and ticker_symbol.endswith('.NS'):
                bse_symbol = symbol.replace('.NS', '.BO')
                stock = yf.Ticker(bse_symbol)
                info = stock.info

            if not info or len(info) == 0:
                raise Exception(f"No metrics data available for {symbol}")

            metrics = {
                'Market Cap': info.get('marketCap', 'N/A'),
                'PE Ratio': info.get('trailingPE', 'N/A'),
                'Volume': info.get('volume', 'N/A'),
                'Avg Volume': info.get('averageVolume', 'N/A'),
                'Dividend Yield': info.get('dividendYield', 'N/A'),
                'Beta': info.get('beta', 'N/A')
            }
            return pd.DataFrame([metrics]).T
        except Exception as e:
            raise Exception(f"Error fetching key metrics for {symbol}: {str(e)}")

    @staticmethod
    def is_indian_stock(symbol):
        """Check if the symbol is an Indian stock"""
        return (
            symbol.endswith('.NS') or 
            symbol.endswith('.BO') or 
            symbol in ['IRCTC', 'NIFTY50', 'SENSEX'] or
            any(char.isdigit() for char in symbol) or
            any(s in symbol for s in ['&', '-'])
        )