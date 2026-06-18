from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import pandas as pd

def train_model(df):
    """Trains a Random Forest model on the provided dataframe."""
    # Features to use for prediction
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 
                'SMA_20', 'SMA_50', 'EMA_20', 'RSI_14', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Daily_Return']
    
    # Ensure all features exist in the dataframe
    features = [f for f in features if f in df.columns]
    
    if len(features) == 0:
        return None, 0.0, None

    X = df[features]
    y = df['Target']
    
    # Time series split: don't shuffle, so we train on past and test on future
    # Using 80% of data for training
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Initialize and train the model
    # Random Forest is a robust choice for baseline classification
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    
    return model, accuracy, report

def predict_tomorrow(model, latest_data):
    """Predicts whether the price will go up or down tomorrow using the latest data row."""
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 
                'SMA_20', 'SMA_50', 'EMA_20', 'RSI_14', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Daily_Return']
    
    features = [f for f in features if f in latest_data.index]
    
    # Ensure it's a 2D array
    X_latest = pd.DataFrame([latest_data[features]])
    
    prediction = model.predict(X_latest)[0]
    probabilities = model.predict_proba(X_latest)[0]
    
    return prediction, probabilities
