import os
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from dotenv import load_dotenv
load_dotenv()

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, max_error, median_absolute_error

client = CogniteClient(
    api_key = os.environ["API_KEY"],
    project = "publicdata",
    client_name = "learn_module",
)

# Global Variables
login_status = client.login.status()
user = login_status.user
project = login_status.project
logged_in = login_status.logged_in

def compute_stats(y_true, y_pred):
    y_err = y_pred - y_true
    y_abs_err = np.abs(y_err)

    return {
        "mean absolute error": "{:.3f}".format(np.mean(y_abs_err)),
        "standard deviation of absolute error": "{:.3f}".format(np.std(y_abs_err)),
        "minimum absolute error": "{:.3f}".format(np.min(y_abs_err)),
        "maximum absolute error": "{:.3f}".format(np.max(y_abs_err)),
        "medium absolute error": "{:.3f}".format(median_absolute_error(y_true, y_pred)),
        "coefficient of determination": "{:.3f}".format(r2_score(y_true, y_pred)),
    }

def main():
    global last_update
    global df_historical
    global ts_names
    global df_forecast
    global df_statistics

    last_update = datetime.now()
    #print(f"Last update: {last_update}")
    
    train_end_date = last_update - timedelta(days = 365)
    train_beg_date = train_end_date - timedelta(days = 30)

    in_ts_names = ["pi:160192", "pi:160702", "pi:191092"]
    out_ts_name = "pi:160700"
    ts_names = in_ts_names + [out_ts_name]

    df_historical = client.datapoints.retrieve_dataframe(
        external_id = ts_names,
        start = train_beg_date,
        end = train_end_date,
        aggregates = ["average"],
        granularity = "1m",
        include_aggregate_name = False,
    )

    df_historical.fillna(method = "ffill", inplace = True)

    lin_reg = LinearRegression()
    lin_reg.fit(df_historical[in_ts_names].values, df_historical[out_ts_name].values)

    df_historical["Lin_Reg"] = lin_reg.predict(df_historical[in_ts_names].values)
    df_historical["Timestamp"] = df_historical.index + timedelta(days = 365)

    rnd_forest = RandomForestRegressor(
        n_estimators = 10,
        min_samples_split = 20,
        max_depth = 5,
    )
    rnd_forest.fit(df_historical[in_ts_names].values, df_historical[out_ts_name].values)

    df_historical["Rnd_Forest"] = rnd_forest.predict(df_historical[in_ts_names].values)

    #print(df_historical.head())

    test_beg_date = train_end_date
    test_end_date = test_beg_date + timedelta(hours = 1)

    df_forecast = client.datapoints.retrieve_dataframe(
        external_id = ts_names,
        start = test_beg_date,
        end = test_end_date,
        aggregates = ["average"],
        granularity = "1m",
        include_aggregate_name = False,
    )

    df_forecast.fillna(method = "ffill", inplace = True,)

    df_forecast["Lin_Reg"] = lin_reg.predict(df_forecast[in_ts_names].values)
    df_forecast["Rnd_Forest"] = rnd_forest.predict(df_forecast[in_ts_names].values)
    df_forecast["Timestamp"] = df_forecast.index + timedelta(days = 365)

    lin_reg_stats = compute_stats(df_forecast["pi:160700"], df_forecast["Lin_Reg"])
    rnd_forest_stats = compute_stats(df_forecast["pi:160700"], df_forecast["Rnd_Forest"])  

    #print(lin_reg_stats)
    #print(rnd_forest_stats)  

    df_statistics = pd.DataFrame(data = {
        "Statistic" : lin_reg_stats.keys(),
        "Linear Regression": lin_reg_stats.values(),
        "Random Forest": rnd_forest_stats.values(),
    })

    #print(df_statistics.head())

if __name__ == "__main__":
    main()
