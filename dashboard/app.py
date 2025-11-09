# dash_app.py
import dash
from dash import html, dcc, Input, Output
import dash_ag_grid as dag
import duckdb
from config import DB_PATH

# Начальная загрузка магазинов
con = duckdb.connect(DB_PATH, read_only=True)
stores = sorted(con.execute("SELECT DISTINCT Store FROM predictions").df()["Store"])
con.close()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Rossmann Predictions Dashboard"),

    html.Div([
        html.Label("Select Store"),
        dcc.Dropdown(id="store-select",
                     options=[{"label": s, "value": s} for s in stores],
                     value=stores[0])
    ], style={"width": "30%", "display": "inline-block"}),

    html.Div([
        html.Label("Select Date"),
        dcc.Dropdown(id="date-select")
    ], style={"width": "30%", "display": "inline-block", "marginLeft": "20px"}),

    html.Br(),
    dag.AgGrid(
        id="grid",
        columnDefs=[],
        rowData=[],
        className="ag-theme-alpine",
        style={"height": "700px", "width": "100%"}
    )
])


# ✅ Динамическая подгрузка дат для выбранного Store
@app.callback(
    Output("date-select", "options"),
    Output("date-select", "value"),
    Input("store-select", "value")
)
def update_dates(store):
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(f"""
        SELECT DISTINCT Date
        FROM predictions
        WHERE Store = {store}
        ORDER BY Date
    """).df()
    con.close()

    if df.empty:
        return [], None

    dates = df["Date"].astype(str).tolist()
    return [{"label": d, "value": d} for d in dates], dates[0]


# ✅ Таблица обновляется по store + date
@app.callback(
    Output("grid", "rowData"),
    Output("grid", "columnDefs"),
    Input("store-select", "value"),
    Input("date-select", "value")
)
def update_table(store, date):
    if date is None:
        return [], []

    import requests
    url = f"http://127.0.0.1:8000/filter?store={store}&date={date}"
    data = requests.get(url).json()

    if not data:
        return [], []

    columns = [{"field": c} for c in data[0].keys()]
    return data, columns


if __name__ == "__main__":
    app.run(debug=True)
