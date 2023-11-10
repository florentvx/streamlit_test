import pandas as pd
import streamlit as st
import datetime as dt
from pension_simulator import model_statics, simulate_pension_fund, simulate_pension_struct, calculate_fix_pension_from_fund, calculate_all_taxes

st.set_page_config(
    layout="wide",
)

st.title("💷 Pension Calculations")

left_form, _,right_form = st.columns([0.45, 0.1, 0.45])

with left_form:
    st.subheader("My current numbers")
    left_left_form, right_left_form = left_form.columns([0.5,0.5])
    with left_left_form:
        start_date=st.date_input("Start Date", value=dt.date(2017,8,1), help="Your carreer start date")
        crt_amount=st.number_input("Total Amount", value=100000.00)
    with right_left_form:
        today_date = st.date_input("Today date", value=dt.date.today())
        crt_contrib=st.number_input("Current Monthly Contribution", value=1000.00)
    
with right_form:
    st.subheader("My Model parameters", help="These parameters should be set from the start to reasonable values and hardly ever retouched in the future")
    left_right_form, right_right_form = right_form.columns([0.5,0.5])
    with left_right_form:
        fwd_inflation = st.number_input("Inflation Prevision (Yearly %)", value=2.00) / 100.0
        ctb_inc=st.number_input("my Contribution Increases (Yearly %)", value=5.00) / 100.0
    with right_right_form:
        fwd_market_rate = st.number_input("ROI Prevision (Yearly %)", value=3.00, help="Return Over Investement") / 100.0
        nb_wk_yrs=st.number_input("Number Of Working Years", value=40)
        nb_ret_yrs=st.number_input("Number Of Retirement Years", value=35)
    ctb_inc_mth=st.multiselect(
        'Contribution Increase Month',
        ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        ['Jan'],
    )
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
    

    

st.markdown("---")

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
