import math

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import yaml

import pension_simulator as pension

st.set_page_config(
    page_title='My Data',
    page_icon="🔵",
    layout="wide",
)

st.header("my 2023 data")
st.subheader("do i need a subheader? Really")


st.sidebar.header("sidebar")
option_ms = [f"{i}" for i in range(1,6)]
my_var = st.sidebar.multiselect(
    "select var",
    options=option_ms,
    default=[option_ms[0], option_ms[-1]]
)

st.title("💷 Tax Calculations")

my_amount = 100000

left_col, midd_col, right_col = st.columns([0.35,0.35,0.3])
with left_col:
    st.dataframe(pension.calculate_income_tax(my_amount))
with midd_col:
    st.dataframe(pension.calculate_national_insurance_tax(my_amount))
with right_col:
    st.dataframe(pension.calculate_all_taxes(my_amount))





st.markdown("---")

st.title(':pencil2:  Numbers')
#st.markdown("##")
st.text(sum(map(float,my_var)))

left_col, midd_col, right_col = st.columns([0.25,0.5,0.25])
with left_col:
    st.text("My Stars")
with midd_col:
    st.markdown(":star:" * 6)
with right_col:
    st.text("it was great right?")

st.markdown("---")


df = pd.DataFrame()
df['x'] = [i/100. for i in range(1000)]
df['y'] = df['x'].apply(lambda x: math.sin(x))
my_line_chart = px.line(
    df, 
    x="x", 
    y="y",
    title="<b>My Special Line Chart</b>",
    template="plotly",
)

midd_col.plotly_chart(my_line_chart, use_container_width=True)

st.markdown('---')

uploaded_file = st.file_uploader('Choose yaml file:', type='yaml')
if uploaded_file is not None:
    st.markdown("---")
    my_file = yaml.safe_load(uploaded_file)
    #random use case
    hist_infl = my_file['historical_inflation']
    df = pd.DataFrame()
    df["year"] = hist_infl.keys()
    df['rate'] = df['year'].apply(lambda x: hist_infl[x])
    #st.dataframe(df)
    fig_inf = px.bar(
        df,
        x="year",
        y='rate',
        color='rate',
        color_continuous_scale=['green', 'yellow', 'red'],
        template='plotly_white',
        title=f'<b>Inflation Rate</b>'
    )
    st.plotly_chart(fig_inf)

    popo = yaml.dump(my_file)
    st.download_button(label="redownload yaml", file_name='new_yaml.yaml', mime = 'application/x-yaml', data=popo)
    
    



# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
