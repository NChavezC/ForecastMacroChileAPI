import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta

class DataPoint(BaseModel):
    date: str
    value: float

class Data(BaseModel):
    data: List[DataPoint]


app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

memory_db = {"data": []}

@app.get("/", tags=["Docs"])
def get_docs():
    return RedirectResponse("/docs")

@app.post("/sarima", tags=["Models"])
def forecast_sarima(data: Data):
    #Set Periods of Forecast
    periods = 4
    # Convert input to DataFrame
    df = pd.DataFrame([{"date": d.date, "value": d.value} for d in data.data])

    # Convert date column to datetime format (Ensure correct parsing for DD-MM-YYYY format)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    
    # Sort by date in case the input is unordered
    df = df.sort_values("date")
    df.set_index("date", inplace=True)

    # Fit ARIMA(1,0,1) model
    model = SARIMAX(df["value"], order=(2,0,2), seasonal_order=(3, 0, 3, 12), freq="MS")
    fitted_model = model.fit()

    # Forecast next periods
    forecast_values = fitted_model.forecast(steps=periods)

    # Generate future dates based on the last available date
    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=30 * i) for i in range(1, periods + 1)]  # Assuming monthly data

    # Prepare response in required format
    forecast_data = [{"date": date.strftime("%d-%m-%Y"), "value": float(value)} for date, value in zip(future_dates, forecast_values)]
    print(forecast_data)

    return forecast_data

@app.post("/arima", tags=["Models"])
def forecast_arima(data: Data):
    #Set Periods of Forecast
    periods = 4
    # Convert input to DataFrame
    df = pd.DataFrame([{"date": d.date, "value": d.value} for d in data.data])

    # Convert date column to datetime format (Ensure correct parsing for DD-MM-YYYY format)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    
    # Sort by date in case the input is unordered
    df = df.sort_values("date")
    df.set_index("date", inplace=True)

    # Fit ARIMA(1,0,1) model
    model = ARIMA(df["value"], order=(2, 0, 2))
    fitted_model = model.fit()

    # Forecast next periods
    forecast_values = fitted_model.forecast(steps=periods)

    # Generate future dates based on the last available date
    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=30 * i) for i in range(1, periods + 1)]  # Assuming monthly data

    # Prepare response in required format
    forecast_data = [{"date": date.strftime("%d-%m-%Y"), "value": float(value)} for date, value in zip(future_dates, forecast_values)]
    print(forecast_data)

    return forecast_data



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)