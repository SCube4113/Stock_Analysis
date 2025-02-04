import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class ChartBuilder:
    @staticmethod
    def create_price_chart(df):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.03, 
                           row_heights=[0.7, 0.3])

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ), row=1, col=1)

        # Add volume bar chart
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color='rgba(0,255,135,0.3)'
        ), row=2, col=1)

        # Calculate and add moving averages
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='20 Day MA',
            line=dict(color='#f6d854')
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA50'],
            name='50 Day MA',
            line=dict(color='#f25f5c')
        ), row=1, col=1)

        # Update layout
        fig.update_layout(
            title_text="Price History & Volume",
            xaxis_rangeslider_visible=False,
            height=800,
            template="plotly_dark",
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

        return fig

    @staticmethod
    def create_comparison_chart(historical_data_dict):
        if not historical_data_dict:
            return go.Figure()

        fig = go.Figure()
        colors = ['#00ff87', '#f6d854', '#f25f5c', '#8338ec', '#3a86ff']

        for i, (symbol, df) in enumerate(historical_data_dict.items()):
            if df.empty or 'Close' not in df.columns:
                continue

            try:
                # Ensure we have valid data
                if len(df) > 0:
                    initial_price = df['Close'].iloc[0]
                    if pd.notnull(initial_price) and initial_price != 0:
                        normalized_prices = ((df['Close'] - initial_price) / initial_price) * 100

                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=normalized_prices,
                            name=symbol,
                            line=dict(color=colors[i % len(colors)]),
                            hovertemplate="<b>%{x}</b><br>" +
                                        "%{y:.2f}% change<br>" +
                                        f"<b>{symbol}</b><extra></extra>"
                        ))
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                continue

        fig.update_layout(
            title="Stock Price Comparison (% Change)",
            xaxis_title="Date",
            yaxis_title="Price Change (%)",
            height=600,
            template="plotly_dark",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

        return fig