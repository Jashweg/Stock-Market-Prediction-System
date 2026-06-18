from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
import requests
import os

from data_fetcher import fetch_data, preprocess_data
from model import train_model, predict_tomorrow

app = FastAPI(title="Stock Prediction API")

# Mount static files to serve the frontend robustly on Vercel
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
def search_ticker(q: str = Query(..., min_length=1)):
    """Search for companies using Yahoo Finance autocomplete API."""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=6&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'quotes' in data:
            for quote in data['quotes']:
                if 'symbol' in quote and 'shortname' in quote:
                    results.append({
                        "symbol": quote['symbol'],
                        "name": quote['shortname'],
                        "exchange": quote.get('exchDisp', '')
                    })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")

class PredictionRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

class PredictionResponse(BaseModel):
    ticker: str
    prediction: str
    confidence: float
    accuracy: float
    message: str
    chart_data: dict

@app.post("/api/predict", response_model=PredictionResponse)
def predict_stock(request: PredictionRequest):
    try:
        # Fetch Data
        raw_data = fetch_data(request.ticker, request.start_date, request.end_date)
        
        if raw_data.empty:
            raise HTTPException(status_code=400, detail=f"Failed to fetch data for {request.ticker}. Check symbol and date range.")
            
        # Preprocess Data
        processed_data = preprocess_data(raw_data)
        
        if processed_data.empty or len(processed_data) < 50:
             raise HTTPException(status_code=400, detail="Not enough data to compute technical indicators. Try a longer date range.")
             
        # Train Model
        model, accuracy, report = train_model(processed_data)
        
        if model is None:
             raise HTTPException(status_code=500, detail="Failed to train model.")
             
        # Predict Tomorrow
        latest_data = processed_data.iloc[-1]
        prediction_val, probabilities = predict_tomorrow(model, latest_data)
        
        direction = "UP" if prediction_val == 1 else "DOWN"
        confidence = probabilities[1] if prediction_val == 1 else probabilities[0]
        
        # Prepare chart data
        chart_data = {
            "dates": processed_data.index.strftime('%Y-%m-%d').tolist(),
            "open": processed_data['Open'].tolist(),
            "high": processed_data['High'].tolist(),
            "low": processed_data['Low'].tolist(),
            "close": processed_data['Close'].tolist(),
        }
        
        return PredictionResponse(
            ticker=request.ticker.upper(),
            prediction=direction,
            confidence=round(confidence * 100, 2),
            accuracy=round(accuracy * 100, 2),
            message="Prediction successful.",
            chart_data=chart_data
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
