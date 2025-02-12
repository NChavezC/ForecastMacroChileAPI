import requests
import pandas as pd

# API URL
url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?user=gchavez@fen.uchile.cl&pass=qRSN5ktgn.K24SP&function=GetSeries&timeseries=F049.DES.TAS.INE9.10.M&firstdate=2000-01-01&lastdate=2024-12-31"

# Function to fetch data
def fetch_chile_unemployment():
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    data = response.json()
    
    if data.get("Codigo") != 0 or "Series" not in data or "Obs" not in data["Series"]:
        raise Exception("Invalid response format")

    observations = data["Series"]["Obs"]

    # Convert data into a DataFrame
    df = pd.DataFrame(observations)
    df = df.rename(columns={"indexDateString": "date", "value": "unemployment_value"})
    df["unemployment_value"] = pd.to_numeric(df["unemployment_value"], errors="coerce")  # Convert to float
    df = df[["date", "unemployment_value"]]  # Keep relevant columns

    return df

# Save to CSV
def save_to_csv(df, filename="../../public/chile_unemployment.csv"):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Run the script
if __name__ == "__main__":
    df = fetch_chile_unemployment()
    save_to_csv(df)
