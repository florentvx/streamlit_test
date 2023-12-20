import pandas as pd
import streamlit as st
import datetime as dt
from pension_simulator import model_statics, simulate_pension_fund, simulate_pension_struct, \
                                calculate_fix_pension_from_fund, calculate_all_taxes

from tools import set_page_config
from tools.session import *

def push_current_numbers_data():
    session_set(
        'current_numbers', 
        {
            'date': today_date,
            'current_amount': crt_amount,
            'current_contrib': crt_contrib,
        }
    ) 

def push_model_parameters_data():
    session_set(
        'model_parameters',
        {
            'update_time': dt.datetime.now(),
            'start_date': start_date,
        }
    )

session_init(
    'current_numbers',
    {
        'date': dt.date.today(),
        'current_amount': 100000.0,
        'current_contrib': 1000.0,
    }
)

set_page_config()

st.title(":blue_book: Pension Calculations")

left_form, _,right_form = st.columns([0.4, 0.05, 0.55])

with left_form:
    st.subheader("My Current Numbers")
    my_current_numbers : dict = session_get('current_numbers')
    crt_nb_container = left_form.container(border=True)
    with crt_nb_container:
        today_date = st.date_input(
            "Today date",
            value=my_current_numbers['date']
        )
        crt_amount=st.number_input(
            "Total Amount", 
            value=my_current_numbers['current_amount']
        )
        crt_contrib=st.number_input(
            "Current Monthly Contribution",
            value=my_current_numbers['current_contrib']
        )
        if is_session_loaded():
            zone_button_left, zone_button_right = crt_nb_container.columns([0.5,0.5])
            with zone_button_left:
                push_button = st.button(
                    "Push To Session State", 
                    key="current_button",
                    on_click=push_current_numbers_data,
                    disabled=my_current_numbers['date'] == today_date \
                        and my_current_numbers['current_amount'] == crt_amount \
                        and my_current_numbers['current_contrib'] == crt_contrib
                )
            with zone_button_right:
                if push_button:
                    st.write(f'Current Numbers pushed: {my_current_numbers["date"]}')
            

    
with right_form:
    st.subheader(
        "My Model Parameters",
        help="These parameters should be set from the start to reasonable values and hardly ever retouched in the future"
    )
    rf_container = st.container(border=True)
    with rf_container:
        left_right_form, right_right_form = rf_container.columns([0.5,0.5])
        with left_right_form:
            start_date=st.date_input("Start Date", value=dt.date(2017,8,1), help="Your carreer start date")
            fwd_inflation = st.number_input("Inflation Prevision (Yearly %)", value=2.00) / 100.0
            nb_wk_yrs=st.number_input("Number Of Working Years", value=40)
            
        with right_right_form:
            ctb_inc=st.number_input("my Contribution Increases (Yearly %)", value=5.00) / 100.0
            fwd_market_rate = st.number_input("ROI Prevision (Yearly %)", value=3.00, help="Return Over Investement") / 100.0
            nb_ret_yrs=st.number_input("Number Of Retirement Years", value=35)
        ctb_inc_mth=st.multiselect(
            'Contribution Increase Month',
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            ['Jan'],
        )
        if st.session_state.get('name', NO_NAME_SESSION) != NO_NAME_SESSION:
            zone_button_left_2, zone_button_right_2 = rf_container.columns([0.5,0.5])
            with zone_button_left_2:
                push_button_2 = st.button("Push To Session State", key="model_button", on_click=push_model_parameters_data)
            with zone_button_right_2:
                if push_button_2:
                    st.write(f'Model Parameters pushed: {st.session_state["model_parameters"]["update_time"]}')

st.markdown("---")

ms = model_statics(
    forward_inflation_rate=fwd_inflation,
    forward_market_rate=fwd_market_rate,
    working_number_years=nb_wk_yrs,
    retirement_number_years=nb_ret_yrs,
    contribution_increase_month_list=ctb_inc_mth,
    annual_contribution_increase_rate=ctb_inc
)
res = simulate_pension_fund(
    start_date=start_date,
    month_id=(today_date.year - start_date.year)*12 + today_date.month - start_date.month,
    current_amount=crt_amount,
    current_contribution=crt_contrib,
    statics=ms,
)
res_final:simulate_pension_struct=res[-1]
res = pd.DataFrame()
res["Final Amount"] = [round(res_final.amount,2), round(res_final.real_amount,2)]
res["Fix Monthly"] = res["Final Amount"].apply(lambda x: round(calculate_fix_pension_from_fund(x, nb_ret_yrs, fwd_market_rate),2))
res.index = ["Nominal", "Real"]
tax_rate = round(calculate_all_taxes(res.loc["Real", "Fix Monthly"] * 12).loc["Total", "Tax Rate (%)"], 2)
res["Fix Monthly Net"] = res["Fix Monthly"].apply(lambda x: round(x * (1-tax_rate/100.0),2))

_,mid,_=st.columns(3)
with mid:
    st.subheader("My Results")
    st.dataframe(res.T, width=500)
    
    
# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
