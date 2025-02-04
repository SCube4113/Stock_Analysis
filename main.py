import streamlit as st
import pandas as pd
from utils.data_fetcher import StockDataFetcher
from utils.chart_builder import ChartBuilder
from utils.metrics_calculator import MetricsCalculator
import plotly.graph_objects as go
import base64
from datetime import datetime, timedelta
import io

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

    # Market selection
    market = st.radio(
        "Select Market",
        ["Global", "Indian (NSE/BSE)"],
        help="Choose between global markets or Indian stock exchanges"
    )

    # Stock search with autocomplete
    search_query = st.text_input(
        'Search Stock:',
        help="""Start typing to search for stocks.
        For Indian stocks: Try company names or symbols like 'RELIANCE' or 'TCS'
        For Global stocks: Try 'AAPL' or 'MSFT'""",
        key='stock_search'
    ).upper()

    # Show suggestions based on search
    if search_query:
        with st.spinner('Searching...'):
            suggestions = StockDataFetcher.search_stock_symbols(search_query, market)
            if suggestions:
                st.session_state['search_results'] = suggestions
                for suggestion in suggestions:
                    if st.button(
                        f"{suggestion['symbol']} - {suggestion['name']} ({suggestion['exchange']})",
                        key=f"btn_{suggestion['symbol']}"
                    ):
                        if suggestion['symbol'] not in st.session_state['stocks']:
                            try:
                                # Verify data availability
                                test_data = StockDataFetcher.get_historical_data(suggestion['symbol'], '1mo')
                                if not test_data.empty:
                                    st.session_state['stocks'].append(suggestion['symbol'])
                                    st.success(f"Successfully added {suggestion['symbol']} to comparison")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("No matching stocks found. Try a different search term.")

    # Show example stocks based on selected market
    if market == "Indian (NSE/BSE)":
        st.caption("""
        Popular Indian Stocks:
        - NSE: RELIANCE, TCS, HDFCBANK, INFY
        - BSE: 500325 (RELIANCE), 532540 (TCS)
        """)
    else:
        st.caption("""
        Popular Global Stocks:
        AAPL, MSFT, GOOGL, AMZN
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

# Footer
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 20px;'>
    Data provided by Yahoo Finance | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)