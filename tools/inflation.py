import datetime as dt
import pandas as pd

from pension_simulator import MONTH_MAP


def get_python_date(input: str):
    month_input = input[5:]
    month_input = month_input[0].upper() + month_input[1:].lower()
    if month_input not in MONTH_MAP:
        raise ValueError(f'{month_input} not in {MONTH_MAP.keys()}')
    return dt.date(int(input[:4]), MONTH_MAP[month_input], 1)

inflation_data = pd.read_csv(r'data/uk_cpih_timeseries.csv')
inflation_data['Date'] = inflation_data['year_month_date'].apply(get_python_date)
inflation_data = inflation_data.drop('year_month_date', axis = 1)

inflation_data['UK CPIH Index'] = inflation_data['uk_cpih']
inflation_data = inflation_data.drop("uk_cpih", axis=1)
inflation_data['Inflation Rate (%)'] = round((inflation_data['UK CPIH Index'] / inflation_data['UK CPIH Index'].shift(12) - 1) * 100, 2)

inflation_dict = {
    row['Date']: row["UK CPIH Index"]
    for _, row in inflation_data.iterrows()
}