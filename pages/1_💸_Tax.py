import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
import pension_simulator as pension
import plotly.express as px
from PIL import Image

from tools import set_page_config

if "gross_pay" not in st.session_state:
    st.session_state['gross_pay'] = 40000

if "tax_events" not in st.session_state.keys():
    st.session_state['tax_events'] = {}
if 'input' not in st.session_state["tax_events"].keys(): 
    st.session_state['tax_events']['input'] = st.session_state['gross_pay']


def on_change_my_amount():
    st.session_state['tax_events']['input'] = st.session_state.gross_pay_input

def push_gross_pay():
    st.session_state['gross_pay'] = st.session_state['tax_events']['input']

def restore_gross_pay():
    st.session_state['tax_events']['input'] = st.session_state['gross_pay']


set_page_config()

st.title("💷 Tax Calculations")


left_col_input, _ = st.columns([0.35,0.65])
with left_col_input:
    my_amount = st.number_input(
        "Gross Pay:", 
        min_value=1000, 
        max_value=1000000, 
        value=st.session_state['tax_events']['input'], 
        step=1000,
        format='%i',
        on_change=on_change_my_amount,
        key='gross_pay_input'
    )
    zone_button_left, zone_button_mid, zone_button_right = left_col_input.columns([0.25,0.25,0.5])
    with zone_button_left:
        push_button = st.button(
            "Push", 
            key="push_button", 
            on_click=push_gross_pay,
            disabled=st.session_state['tax_events']['input'] == st.session_state['gross_pay'],
            use_container_width=True,
        )
    with zone_button_mid:
        restore_button = st.button(
            "Restore", 
            key="restore_button", 
            on_click=restore_gross_pay,
            disabled=st.session_state['tax_events']['input'] == st.session_state['gross_pay'],
            use_container_width=True,
        )
    with zone_button_right:
        if push_button:
            st.write(f'Gross Pay pushed: {st.session_state["gross_pay"]}')
        if restore_button:
            st.write(f'Gross Pay restored: {st.session_state["gross_pay"]}')

st.markdown('')

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
