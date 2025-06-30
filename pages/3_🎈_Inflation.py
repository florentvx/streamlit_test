import datetime as dt
import plotly.express as px
import streamlit as st

from pension_simulator import convert_price_with_inflation

from tools import *
from tools.inflation import inflation_data, inflation_dict

set_page_config()

st.title("🎈 Inflation", help='https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23')

cols_converter = st.columns([0.2]*5)
with cols_converter[0]:
    date_in = st.date_input("Input Date", dt.date(2020,1,1), min_value=dt.date(1989,1,1))
with cols_converter[1]:
    money_in = st.number_input("Amount of GBP", min_value=0.0, value=100.0)
with cols_converter[3]:
    date_out = st.date_input("Output Date", dt.date.today(), min_value=dt.date(1988,1,1))
with cols_converter[4]:
    st.write("Equivalent Amount")
    money_out = st.text(f"£ {round(convert_price_with_inflation(inflation_dict, money_in, date_in, date_out),2)}")


st.markdown('---')
radio_choice = st.radio("Graph Choice: ", ["Index", "Rate"], index=1)

my_line_chart = px.line(
    inflation_data, 
    x="Date", 
    y="UK CPIH Index",
    title="<b>UK CPIH</b>",
    template="plotly",
)

my_second_line_chart = px.line(
    inflation_data, 
    x="Date", 
    y="Inflation Rate (%)",
    title="<b>Year On Year Inflation Rate</b>",
    template="plotly",
)

left_col, midd_col, right_col = st.columns([0.25,0.5,0.25])
if radio_choice == "Index":
    midd_col.plotly_chart(my_line_chart, use_container_width=True)
elif radio_choice == "Rate":
    midd_col.plotly_chart(my_second_line_chart, use_container_width=True)
else:
    raise ValueError(f"radio choice not covered: {radio_choice}")
