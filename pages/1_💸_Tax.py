import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
import pension_simulator as pension
import plotly.express as px
from PIL import Image

from tools import set_page_config

set_page_config()

st.title("💷 Tax Calculations")

if "gross_pay" not in st.session_state:
    st.session_state['gross_pay'] = 0.0

left_col_input, _ = st.columns([0.3,0.7])
with left_col_input:
    #my_amount = st.slider("Gross Pay:", min_value=0.0,max_value=300000.0, value = 50000.0)
    my_amount = st.number_input(
        "Gross Pay:", 
        min_value=1000, 
        max_value=1000000, 
        value=40000 if st.session_state['gross_pay'] == 0.0 else st.session_state['gross_pay'], 
        step=1000,
        format='%i'
    )

st.session_state['gross_pay'] = my_amount

left_col, midd_col, right_col = st.columns([0.35,0.35,0.3])
income_tax = pension.calculate_income_tax(my_amount)
ni_tax = pension.calculate_national_insurance_tax(my_amount)
summary_tax = pension.calculate_all_taxes(my_amount)
with left_col:
    st.dataframe(income_tax)
with midd_col:
    st.dataframe(ni_tax)
with right_col:
    st.dataframe(summary_tax)
pie_array = [
    ["Income Tax", income_tax.loc["Total Income Tax", 'Tax Amount']],
    ["NI Tax", ni_tax.loc["Total NI Tax", 'Tax Amount']],
]
pie_array += [["Net Revenue", my_amount - pie_array[0][1] - pie_array[1][1]]]
pie_df = pd.DataFrame(pie_array, columns=["Name", "Value"])
pie_chart = px.pie(pie_df, values="Value", names="Name")

_,mid2,_ = st.columns([0.3, 0.4, 0.3])

with mid2:
    st.plotly_chart(pie_chart)

    image = Image.open('images/tax.jpg')
    st.image(image, caption="my picture", use_column_width=True)



st.markdown("---")

# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
