import streamlit as st
import pandas as pd
from utils.data_fetcher import StockDataFetcher
from utils.chart_builder import ChartBuilder
from utils.metrics_calculator import MetricsCalculator
import plotly.graph_objects as go
import base64
from datetime import datetime, timedelta
import io
from utils.realtime.websocket_client import StockWebSocket
from utils.ml.price_predictor import PricePredictor
from utils.ml.trend_analyzer import TrendAnalyzer

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'stocks' not in st.session_state:
    st.session_state['stocks'] = []
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []

# Initialize WebSocket and ML models
if 'websocket' not in st.session_state:
    st.session_state.websocket = StockWebSocket()
    st.session_state.websocket.connect()
    st.session_state.websocket.start()

if 'price_predictor' not in st.session_state:
    st.session_state.price_predictor = PricePredictor()
    
if 'trend_analyzer' not in st.session_state:
    st.session_state.trend_analyzer = TrendAnalyzer()

# Initialize settings in session state if not present
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'default_market': 'Global',
        'theme': 'Light',
        'default_interval': '1d',
        'enable_alerts': False,
        'alert_threshold': 5
    }

def download_csv(df):
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()
    filename = f"stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

# Main app layout
st.title('📈 Stock Analysis Dashboard')

# Sidebar
with st.sidebar:
    st.header('Stock Selection')

    # Market selection dropdown
    market = st.selectbox(
        "Select Market",
        ["Global Stocks", "Indian Stocks (NSE/BSE)", "Cryptocurrency", "Commodities"],
        help="Choose market type for analysis"
    )

    # Stock search with autocomplete
    search_query = st.text_input(
        'Search:',
        help="""Start typing to search:
        Global Stocks: Try 'AAPL' or 'MSFT'
        Indian Stocks: Try 'RELIANCE' or 'TCS'
        Crypto: Try 'BTC' or 'ETH'
        Commodities: Try 'GOLD' or 'SILVER'""",
        key='stock_search'
    ).upper()

    # Show suggestions based on search
    if search_query:
        suggestions = StockDataFetcher.search_stock_symbols(search_query, market)
        for suggestion in suggestions:
            if st.button(f"{suggestion['symbol']} - {suggestion['name']}", key=suggestion['symbol']):
                if suggestion['symbol'] not in st.session_state['stocks']:
                    try:
                        # Define symbol here
                        symbol = StockDataFetcher.get_symbol_suffix(suggestion['symbol'], market)
                        test_data = StockDataFetcher.get_historical_data(symbol, '1mo', interval='1d')
                        if not test_data.empty:
                            st.session_state['stocks'].append(symbol)
                            st.success(f"Successfully added {symbol} to comparison")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Show example tickers based on selected market
    if market == "Global Stocks":
        st.caption("""
        Popular Global Stocks:
        AAPL, MSFT, GOOGL, AMZN
        """)
    elif market == "Indian Stocks (NSE/BSE)":
        st.caption("""
        Popular Indian Stocks:
        - NSE: RELIANCE, TCS, HDFCBANK, INFY
        - BSE: 500325 (RELIANCE), 532540 (TCS)
        """)
    elif market == "Cryptocurrency":
        st.caption("""
        Popular Cryptocurrencies:
        BTC-USD, ETH-USD, DOGE-USD, XRP-USD
        """)
    elif market == "Commodities":
        st.caption("""
        Popular Commodities:
        GC=F (Gold), SI=F (Silver), CL=F (Crude Oil)
        """)

    # Remove stock functionality
    if st.session_state['stocks']:
        st.write('Current Stocks:')
        for stock in st.session_state['stocks']:
            col1, col2 = st.columns([3, 1])
            col1.write(stock)
            if col2.button('Remove', key=f'remove_{stock}'):
                st.session_state['stocks'].remove(stock)
                st.rerun()

    # Timeframe selection
    st.header('Timeframe Settings')

    timeframe_type = st.radio(
        "Select Timeframe Type",
        ["Preset Periods", "Custom Range"],
        key="timeframe_type"
    )

    if timeframe_type == "Preset Periods":
        period = st.selectbox(
            'Select Time Period:',
            ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
            index=4,
            help="Select a preset time period"
        )
        interval = st.selectbox(
            'Select Interval:',
            ['1d', '1h', '30m', '15m', '5m', '1m'],
            index=0,
            help="Select data interval (some intervals only available for shorter periods)"
        )
        start_date = end_date = None
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now() - timedelta(days=180)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now()
            )
        interval = st.selectbox(
            'Select Interval:',
            ['1d', '1h', '30m', '15m', '5m', '1m'],
            index=0
        )
        period = None

# Main content
if st.session_state['stocks']:
    try:
        # Create tabs for different views
        tab1, tab2 = st.tabs(['Price Comparison', 'Metrics Comparison'])

        with tab1:
            # Fetch historical data for all stocks
            historical_data = {}
            with st.spinner('Fetching historical data...'):
                for symbol in st.session_state['stocks']:
                    try:
                        if timeframe_type == "Preset Periods":
                            data = StockDataFetcher.get_historical_data(
                                symbol, period=period, interval=interval
                            )
                        else:
                            data = StockDataFetcher.get_historical_data(
                                symbol,
                                start_date=start_date.strftime('%Y-%m-%d'),
                                end_date=end_date.strftime('%Y-%m-%d'),
                                interval=interval
                            )

                        if not data.empty:
                            historical_data[symbol] = data
                        else:
                            st.warning(f"No historical data available for {symbol}")
                    except Exception as e:
                        st.warning(f"Could not fetch data for {symbol}: {str(e)}")

                if historical_data:
                    fig = ChartBuilder.create_comparison_chart(historical_data)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("No valid data available for comparison")

        with tab2:
            # Fetch and display metrics for all stocks
            metrics_data = {}
            with st.spinner('Fetching metrics...'):
                for symbol in st.session_state['stocks']:
                    try:
                        stock_info = StockDataFetcher.get_stock_info(symbol)
                        if stock_info:
                            metrics_data[symbol] = {
                                'Current Price': MetricsCalculator.format_metric_value(stock_info.get('currentPrice'), 'price'),
                                'Market Cap': MetricsCalculator.format_large_number(stock_info.get('marketCap')),
                                'P/E Ratio': MetricsCalculator.format_metric_value(stock_info.get('trailingPE'), 'ratio'),
                                'Volume': MetricsCalculator.format_large_number(stock_info.get('volume')),
                                'Beta': MetricsCalculator.format_metric_value(stock_info.get('beta'), 'ratio')
                            }
                    except Exception as e:
                        st.warning(f"Could not fetch metrics for {symbol}: {str(e)}")

            # Create comparison table
            if metrics_data:
                df_metrics = pd.DataFrame(metrics_data)
                st.dataframe(df_metrics, use_container_width=True)

                # Download button for metrics
                st.markdown(download_csv(df_metrics), unsafe_allow_html=True)
            else:
                st.error("No metrics data available for comparison")

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info('👈 Add stock symbols in the sidebar to begin comparison analysis.')

def show_realtime_predictions():
    # Only show header and predictions if stocks are selected
    if st.session_state['stocks']:
        st.header("Real-Time Analysis & Predictions")
        
        # Real-time prices
        if 'real_time_prices' in st.session_state:
            for symbol, data in st.session_state.real_time_prices.items():
                currency_symbol = "₹" if symbol.endswith(('.NS', '.BO')) else "$"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{symbol} Price", f"{currency_symbol}{data['price']:.2f}")
                with col2:
                    st.text(f"Last Update: {data['timestamp'].strftime('%H:%M:%S')}")
                    
        # ML Predictions
        for symbol in st.session_state['stocks']:
            st.subheader(f"Analysis for {symbol}")
            
            currency_symbol = "₹" if symbol.endswith(('.NS', '.BO')) else "$"
            
            data = StockDataFetcher.get_historical_data(symbol, '1y')
            
            with st.spinner(f'Training ML models for {symbol}...'):
                st.session_state.price_predictor.train(data)
                predicted_price = st.session_state.price_predictor.predict(data)
                
                st.session_state.trend_analyzer.train(data)
                trend_analysis = st.session_state.trend_analyzer.predict_trend(data)
                st.success('Training completed!')
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Predicted Price (Next Day)", 
                    f"{currency_symbol}{predicted_price:.2f}",
                    delta=f"{((predicted_price - data['Close'].iloc[-1]) / data['Close'].iloc[-1] * 100):.2f}%"
                )
            with col2:
                confidence_pct = trend_analysis['confidence'] * 100
                st.metric(
                    "Trend Analysis",
                    trend_analysis['trend'],
                    f"Confidence: {confidence_pct:.2f}%"
                )
    else:
        # Center content vertically and horizontally
        st.markdown("""
            <style>
                .empty-state {
                    text-align: center;
                    padding: 40px;
                    margin-top: 100px;
                }
                .big-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                .message {
                    font-size: 20px;
                    color: #666;
                    margin-bottom: 15px;
                }
                .sub-message {
                    font-size: 16px;
                    color: #888;
                }
            </style>
            <div class="empty-state">
                <div class="big-icon">📈</div>
                <div class="message">Welcome to Real-Time Stock Analysis</div>
                <div class="sub-message">
                    To get started:<br>
                    1. Select your market (Global/Indian) in the sidebar<br>
                    2. Search for a stock symbol (e.g., INFY, TCS)<br>
                    3. Click on the stock to add it to analysis
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Add space before footer
    st.markdown("<br>" * 5, unsafe_allow_html=True)
    
    # Footer
    st.markdown(
        f"""
        <div style='position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 10px; background-color: transparent; border-top: 1px solid #ddd; color: #666;'>
            Data provided by Yahoo Finance | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_settings():
    st.header("Settings")
    
    # Market Preferences
    st.subheader("Market Preferences")
    st.session_state.settings['default_market'] = st.selectbox(
        "Default Market", 
        ["Global", "Indian (NSE/BSE)"],
        index=0 if st.session_state.settings['default_market'] == 'Global' else 1
    )
    
    # Display Settings
    st.subheader("Display Settings")
    st.session_state.settings['theme'] = st.selectbox(
        "Theme", 
        ["Light", "Dark"],
        index=0 if st.session_state.settings['theme'] == 'Light' else 1
    )
    
    st.session_state.settings['default_interval'] = st.selectbox(
        "Default Time Interval",
        ['1d', '5d', '1mo', '3mo', '6mo', '1y'],
        index=['1d', '5d', '1mo', '3mo', '6mo', '1y'].index(st.session_state.settings['default_interval'])
    )
    
    # Alert Settings
    st.subheader("Alert Settings")
    st.session_state.settings['enable_alerts'] = st.toggle(
        "Enable Price Alerts",
        st.session_state.settings['enable_alerts']
    )
    
    if st.session_state.settings['enable_alerts']:
        st.session_state.settings['alert_threshold'] = st.slider(
            "Price Change Threshold (%)", 
            0, 100, 
            st.session_state.settings['alert_threshold']
        )
    
    # Save Settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        # You can add any additional save logic here
        st.rerun()

# Update your page selection code
page = st.sidebar.selectbox(
    "Choose a feature",
    ["Dashboard", "Real-Time Analysis", "Settings"]
)

if page == "Dashboard":
    # Empty dashboard state with centered message
    st.markdown("""
        <style>
            .empty-state {
                text-align: center;
                padding: 40px;
                margin-top: 100px;
            }
            .big-icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
            .message {
                font-size: 20px;
                color: #666;
                margin-bottom: 15px;
            }
            .sub-message {
                font-size: 16px;
                color: #888;
            }
        </style>
        <div class="empty-state">
            <div class="big-icon">📊</div>
            <div class="message">Welcome to Stock Analysis Dashboard</div>
            <div class="sub-message">
                To get started:<br>
                1. Select your market (Global/Indian) in the sidebar<br>
                2. Search for a stock symbol (e.g., AAPL, INFY)<br>
                3. Click on the stock to add it to comparison<br>
                4. Switch to Real-Time Analysis for predictions
            </div>
        </div>
    """, unsafe_allow_html=True)
elif page == "Real-Time Analysis":
    show_realtime_predictions()
elif page == "Settings":
    show_settings()

# Footer
st.markdown("<br>" * 5, unsafe_allow_html=True)
st.markdown(
    f"""
    <div style='position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 10px; background-color: transparent; border-top: 1px solid #ddd; color: #666;'>
        Data provided by Yahoo Finance | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """,
    unsafe_allow_html=True
)

# In your search/add stock logic
suggestions = StockDataFetcher.search_stock_symbols(search_query, market)

# When fetching data
symbol = StockDataFetcher.get_symbol_suffix(symbol, market)
data = StockDataFetcher.get_historical_data(symbol, '1mo', interval='1d')