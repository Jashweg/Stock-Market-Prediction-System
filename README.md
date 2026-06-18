# Stock Market Prediction Dashboard

An AI-powered web application that forecasts the next day's closing direction of a stock. Built with a custom FastAPI backend, Scikit-Learn for machine learning, and a beautiful Vanilla HTML/CSS/JS frontend featuring a dark mode glassmorphism UI.

## Project Description

This project aims to leverage historical stock market data to predict whether a given stock's price will close higher or lower on the following day. By fetching real-time and historical data via the **Yahoo Finance API**, the system computes various technical indicators—such as Simple Moving Average (SMA), Exponential Moving Average (EMA), Relative Strength Index (RSI), and Moving Average Convergence Divergence (MACD). These indicators serve as the primary features fed into a **Random Forest Classifier** to uncover hidden patterns and trends in price action. 

The frontend provides an intuitive, premium dashboard where users can search for any company dynamically, visualize historical price data through interactive candlestick charts, and instantly generate AI-driven forecasts.

### Model Accuracy Note
Predicting daily stock market movements is notoriously complex due to market volatility and external factors. The Random Forest model implemented here serves as a baseline approach. When evaluated on standard test splits across various tickers over a multi-year period, the model generally achieves an **accuracy score of ~53% to 56%** for next-day direction forecasting. It is highly recommended to use this tool for educational purposes and pattern analysis rather than direct financial advice!

## Features
- **Machine Learning Forecasts**: Trains a Random Forest Classifier on historical data to predict if the price will go UP or DOWN tomorrow.
- **Interactive Charting**: Uses Plotly.js to display beautiful candlestick charts of historical data.
- **Smart Search**: Autocomplete functionality for company names via Yahoo Finance.
- **Custom UI**: Zero frameworks on the frontend, purely custom Vanilla CSS and JS.
- **Technical Indicators**: Automatically computes SMA, EMA, RSI, and MACD for prediction features.

## Tech Stack
- **Backend**: Python, FastAPI, Uvicorn, Pandas, Scikit-Learn, yfinance
- **Frontend**: HTML5, CSS3, JavaScript, Plotly.js

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd stock-market-prediction
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   python -m uvicorn main:app --port 8000
   ```

4. Open your browser and navigate to:
   `http://localhost:8000/static/index.html`

## Author
Made by **Jashweg G Raval**
