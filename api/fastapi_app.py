from fastapi import FastAPI
import duckdb
import pandas as pd
from config import DB_PATH
import uvicorn

app = FastAPI()

con = duckdb.connect(DB_PATH, read_only=True)

@app.get("/filter")
def filter_predictions(store: int, date: str):

    query = f"""
        SELECT *
        FROM predictions
        WHERE Store = {store}
        AND Date = '{date}'
    """

    df = con.execute(query).df()

    if df.empty:
        return []

    # 1. date to string (ISO)
    if "Date" in df.columns:
        df["Date"] = df["Date"].astype(str)

    # 2. Convert all categorical columns to string
    for col in df.columns:
        if pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].astype(str)

    # 3. Convert all integer columns to object before fillna("None")
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype(object)

    # 4. Safe fillna
    df = df.fillna("None")

    return df.to_dict(orient="records")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

