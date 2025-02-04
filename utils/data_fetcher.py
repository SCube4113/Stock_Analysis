import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

class StockDataFetcher:
    @staticmethod
    def search_stock_symbols(query, market_type="both"):
        """Search for stock symbols based on user input"""
        try:
            # Define common Indian stock suffixes and indices
            indian_suffixes = [".NS", ".BO"]
            indian_indices = {
                "NIFTY": "^NSEI",
                "SENSEX": "^BSESN",
                "NIFTY50": "^NSEI",
                "BANKNIFTY": "^NSEBANK"
            }

            # First check if it's an index
            if market_type == "Indian (NSE/BSE)" or market_type == "both":
                for index_name, symbol in indian_indices.items():
                    if query.upper() in index_name:
                        try:
                            ticker = yf.Ticker(symbol)
                            info = ticker.info
                            if info:
                                return [{
                                    'symbol': symbol,
                                    'name': index_name,
                                    'exchange': 'NSE'
                                }]
                        except:
                            continue

            # Try different combinations for Indian stocks
            suggestions = []
            if market_type == "Indian (NSE/BSE)" or market_type == "both":
                for suffix in indian_suffixes:
                    try:
                        test_symbol = f"{query.upper()}{suffix}"
                        ticker = yf.Ticker(test_symbol)
                        info = ticker.info
                        if info and 'longName' in info:
                            suggestions.append({
                                'symbol': test_symbol,
                                'name': info['longName'],
                                'exchange': 'NSE' if suffix == '.NS' else 'BSE'
                            })
                    except:
                        continue

            # For global markets
            if market_type == "Global" or market_type == "both":
                try:
                    ticker = yf.Ticker(query.upper())
                    info = ticker.info
                    if info and 'longName' in info:
                        suggestions.append({
                            'symbol': query.upper(),
                            'name': info['longName'],
                            'exchange': info.get('exchange', 'UNKNOWN')
                        })
                except:
                    pass

            return suggestions
        except Exception as e:
            logging.error(f"Error searching symbols: {str(e)}")
            return []

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
    def get_historical_data(symbol, period='1y', start_date=None, end_date=None, interval='1d'):
        """
        Fetch historical data with custom date range and interval support
        """
        try:
            ticker_symbol = StockDataFetcher.get_valid_symbol(symbol)
            stock = yf.Ticker(ticker_symbol)

            # Try fetching data
            if start_date and end_date:
                hist = stock.history(start=start_date, end=end_date, interval=interval)
            else:
                hist = stock.history(period=period, interval=interval)

            # If NSE data fetch fails, try BSE
            if hist.empty and ticker_symbol.endswith('.NS'):
                bse_symbol = symbol.replace('.NS', '.BO')
                stock = yf.Ticker(bse_symbol)
                if start_date and end_date:
                    hist = stock.history(start=start_date, end=end_date, interval=interval)
                else:
                    hist = stock.history(period=period, interval=interval)

            # Verify we have valid data
            if hist.empty:
                raise Exception(f"No historical data available for {symbol}")

            return hist
        except Exception as e:
            raise Exception(f"Error fetching historical data for {symbol}: {str(e)}")

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