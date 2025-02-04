# Stock Analysis Dashboard 📈

A real-time stock analysis dashboard built with Streamlit that allows users to compare multiple stocks, view technical metrics, and analyze historical price data. The application supports both global markets and Indian stock exchanges (NSE/BSE).

## Features

- Real-time stock data visualization
- Multiple stock comparison
- Technical metrics analysis
- Support for global and Indian markets
- Interactive charts with Plotly
- Downloadable data in CSV format
- Responsive design

## Installation

1. Clone the repository:
   bash
   git clone https://github.com/yourusername/stock-analysis-dashboard.git
   cd stock-analysis-dashboard

2. Create a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Dependencies

- Python >= 3.11
- numpy >= 2.2.2
- openai >= 1.61.0
- pandas >= 2.2.3
- plotly >= 6.0.0
- streamlit >= 1.41.1
- yfinance >= 0.2.52

## Running Locally

1. Ensure you're in the project directory with your virtual environment activated

2. Run the Streamlit app:

```bash
streamlit run main.py
```

3. Open your browser and navigate to `http://localhost:8501`

## Usage Examples

### Adding Stocks for Comparison

1. Use the sidebar search box to find stocks
2. Type company name or symbol (e.g., "AAPL" or "Apple")
3. Click on the suggested result to add to comparison

### Global Markets

Popular stocks you can try:

- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet)
- AMZN (Amazon)

### Indian Markets

Popular stocks you can try:

- RELIANCE.NS (Reliance Industries)
- TCS.NS (Tata Consultancy Services)
- HDFCBANK.NS (HDFC Bank)
- INFY.NS (Infosys)

### Analyzing Data

1. Select timeframe (preset periods or custom date range)
2. Compare price movements in the "Price Comparison" tab
3. View fundamental metrics in the "Metrics Comparison" tab
4. Download data using the CSV export option

## Project Structure

```
stock-analysis-dashboard/
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── style.css
│   └── generated-icon.png
├── utils/
│   ├── chart_builder.py
│   ├── data_fetcher.py
│   └── metrics_calculator.py
├── main.py
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

# Stock_Analysis
