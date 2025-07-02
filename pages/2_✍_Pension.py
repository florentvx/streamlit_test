import pandas as pd
import streamlit as st
import datetime as dt
import time
import logging

from pension_simulator import model_statics, simulate_pension_fund, simulate_pension_struct, \
                                calculate_fix_pension_from_fund, calculate_all_taxes

from tools import set_page_config, get_month_id, get_next_contribution_month
from tools.session import reset_session, session_init, session_get, session_set, is_session_loaded

PENSION_SESSION = 'pension_events'
NEW_DATE = 'New Date'

#region Initialization

if st.session_state.get('my_session', None) is None:
    reset_session()

session_init(
    'current_numbers',
    {
        'today_date': dt.date.today(),
        'current_amount': 100000.0,
        'current_contrib': 1000.0,
    }
)

session_init('historical_numbers', {})

session_init(
    'model_numbers',
    {
        'start_date': dt.date(2001,1,1),
        'inflation_rate': 0.02,
        'market_rate': 0.03,
        'number_of_working_years': 40,
        'number_of_retirement_years': 35,
        'contrib_increase': 0.05,
        'contrib_increase_month': ['Jan'],
    }
)

if PENSION_SESSION not in st.session_state.keys():
    st.session_state[PENSION_SESSION] = {
        **session_get('current_numbers').copy(),
        **session_get('model_numbers').copy(),
    }

#endregion

#region Functions: current numbers

def on_change_date():
    my_new_date = my_dates[st.session_state.date_selection]
    if my_new_date != NEW_DATE:
        histo_nb = session_get('historical_numbers')[my_new_date]
        st.session_state.today_date = histo_nb['today_date']
        on_change_today_date()
        st.session_state.current_amount = histo_nb['current_amount']
        on_change_current_amount()
        st.session_state.current_contrib = histo_nb['current_contrib']
        on_change_current_contrib()
    else:
        max_hist_date = max(list(session_get('historical_numbers').keys()))
        max_date = max(max_hist_date + dt.timedelta(days=1), dt.date.today())
        st.session_state.today_date = max_date
        max_hist_nb = session_get('historical_numbers')[max_hist_date]
        st.session_state.current_amount = max_hist_nb['current_amount']
        on_change_current_amount()
        st.session_state.current_contrib = max_hist_nb['current_contrib']
        on_change_current_contrib()
        on_change_today_date()
    
    session_set(
        "current_numbers", 
        {
            'today_date': st.session_state.today_date,
            'current_amount': st.session_state.current_amount,
            'current_contrib': st.session_state.current_contrib,
        }
    )

def on_change_today_date():
    session_set('today_date', st.session_state.today_date, PENSION_SESSION)
    if my_dates[st.session_state.date_selection] == NEW_DATE and st.session_state.today_date in session_get('historical_numbers').keys():
        # can happen with the following sequence:
        # - selection of NEW_DATE
        # - chose a date which was already populated
        st.session_state.date_selection = my_dates.index(st.session_state.today_date)
        on_change_date()

def on_change_current_amount():
    st.session_state.current_amount = round(st.session_state.current_amount, 2)
    session_set('current_amount', st.session_state.current_amount, PENSION_SESSION)

def on_change_current_contrib():
    st.session_state.current_contrib = round(st.session_state.current_contrib, 2)
    session_set('current_contrib', st.session_state.current_contrib, PENSION_SESSION)

def check_current_numbers_status():
    return session_get('today_date', PENSION_SESSION) == session_get('current_numbers')['today_date'] \
        and session_get('current_amount', PENSION_SESSION) == session_get('current_numbers')['current_amount'] \
        and session_get('current_contrib', PENSION_SESSION) == session_get('current_numbers')['current_contrib']

def push_current_numbers_data():
    session_set(
        'current_numbers', 
        {
            'today_date': session_get('today_date', PENSION_SESSION),
            'current_amount': session_get('current_amount', PENSION_SESSION),
            'current_contrib': session_get('current_contrib', PENSION_SESSION),
        }
    ) 
    my_date = session_get('today_date', PENSION_SESSION)
    hist_nb = session_get('historical_numbers')
    hist_nb[my_date] = session_get('current_numbers')
    print(session_get('historical_numbers'))

def restore_current_numbers_data():
    my_crt_nb = session_get('current_numbers')
    st.session_state.today_date = my_crt_nb['today_date']
    st.session_state.current_amount = my_crt_nb['current_amount']
    st.session_state.current_contrib = my_crt_nb['current_contrib']
    session_set('today_date', my_crt_nb['today_date'], PENSION_SESSION)
    session_set('current_amount', my_crt_nb['current_amount'], PENSION_SESSION)
    session_set('current_contrib', my_crt_nb['current_contrib'], PENSION_SESSION)
    
#endregion

#region Functions: model numbers
def on_change_start_date():
    session_set('start_date', st.session_state.start_date, PENSION_SESSION)

def on_change_inflation_rate():
    st.session_state.inflation_rate = round(st.session_state.inflation_rate, 2)
    session_set('inflation_rate', st.session_state.inflation_rate / 100.0, PENSION_SESSION)

def on_change_number_of_working_years():
    st.session_state.number_of_working_years = round(st.session_state.number_of_working_years, 0)
    session_set('number_of_working_years', st.session_state.number_of_working_years, PENSION_SESSION)

def on_change_contrib_increase():
    st.session_state.contrib_increase = round(st.session_state.contrib_increase, 2)
    session_set('contrib_increase', st.session_state.contrib_increase / 100.0, PENSION_SESSION)

def on_change_market_rate():
    st.session_state.market_rate = round(st.session_state.market_rate, 2)
    session_set('market_rate', st.session_state.market_rate / 100.0, PENSION_SESSION)

def on_change_number_of_retirement_years():
    st.session_state.number_of_retirement_years = round(st.session_state.number_of_retirement_years, 0)
    session_set('number_of_retirement_years', st.session_state.number_of_retirement_years, PENSION_SESSION)

def on_change_contrib_increase_month():
    session_set('contrib_increase_month', st.session_state.contrib_increase_month, PENSION_SESSION)

def check_model_numbers_status():
    model_numbers = session_get('model_numbers')
    return session_get('start_date', PENSION_SESSION) == model_numbers['start_date']\
        and session_get('inflation_rate', PENSION_SESSION) == model_numbers['inflation_rate']\
        and session_get('number_of_working_years', PENSION_SESSION) == model_numbers['number_of_working_years']\
        and session_get('contrib_increase', PENSION_SESSION) == model_numbers['contrib_increase']\
        and session_get('market_rate', PENSION_SESSION) == model_numbers['market_rate']\
        and session_get('number_of_retirement_years', PENSION_SESSION) == model_numbers['number_of_retirement_years']\
        and session_get('contrib_increase_month', PENSION_SESSION) == model_numbers['contrib_increase_month']

def push_model_numbers_data():
    session_set(
        'model_numbers',
        {
            'update_time': dt.datetime.now(),
            'start_date': session_get('start_date', PENSION_SESSION),
            'inflation_rate': session_get('inflation_rate', PENSION_SESSION),
            'number_of_working_years': session_get('number_of_working_years', PENSION_SESSION),
            'contrib_increase': session_get('contrib_increase', PENSION_SESSION),
            'market_rate': session_get('market_rate', PENSION_SESSION),
            'number_of_retirement_years': session_get('number_of_retirement_years', PENSION_SESSION),
            'contrib_increase_month': session_get('contrib_increase_month', PENSION_SESSION),
        }
    )

def restore_model_numbers_data():
    model_nb = session_get('model_numbers')
    st.session_state.start_date = model_nb['start_date']
    st.session_state.inflation_rate = model_nb['inflation_rate'] * 100.0
    st.session_state.number_of_working_years = model_nb['number_of_working_years']
    st.session_state.contrib_increase = model_nb['contrib_increase'] * 100.0
    st.session_state.market_rate = model_nb['market_rate'] * 100.0
    st.session_state.number_of_retirement_years = model_nb['number_of_retirement_years']
    st.session_state.contrib_increase_month = model_nb['contrib_increase_month']
    session_set('start_date', model_nb['start_date'], PENSION_SESSION)
    session_set('inflation_rate', model_nb['inflation_rate'], PENSION_SESSION)
    session_set('number_of_working_years', model_nb['number_of_working_years'], PENSION_SESSION)
    session_set('contrib_increase', model_nb['contrib_increase'], PENSION_SESSION)
    session_set('market_rate', model_nb['market_rate'], PENSION_SESSION)
    session_set('number_of_retirement_years', model_nb['number_of_retirement_years'], PENSION_SESSION)
    session_set('contrib_increase_month', model_nb['contrib_increase_month'], PENSION_SESSION)

#endregion

set_page_config()

st.title(":blue_book: Pension Calculations")

current_today = session_get('current_numbers')['today_date']
my_dates = list(session_get('historical_numbers').keys())
my_dates.sort(reverse=True)
my_dates = [NEW_DATE] + my_dates
if is_session_loaded():
    left_top, _ = st.columns([0.2, 0.8])
    with left_top:
        my_date_selection = st.empty()

left_form, _, right_form = st.columns([0.4, 0.05, 0.55])

#region Form: current_numbers
with left_form:
    st.subheader("My Current Numbers")
    crt_nb_container = left_form.container(border=True)
    with crt_nb_container:
        today_date = st.empty()
        crt_amount = st.empty()
        crt_contrib = st.empty()
        if is_session_loaded():
            zone_button_left, zone_button_mid, zone_button_right = crt_nb_container.columns([0.2,0.2,0.6])
            with zone_button_left:
                push_button = st.button(
                    "Push", 
                    key="current_push_button",
                    on_click=push_current_numbers_data,
                    disabled=check_current_numbers_status()\
                        and session_get('historical_numbers').get(session_get('today_date', PENSION_SESSION), None) == session_get('current_numbers'),
                    use_container_width=True,
                )
            with zone_button_mid:
                restore_button = st.button(
                    "Restore", 
                    key="current_restore_button",
                    on_click=restore_current_numbers_data,
                    disabled=check_current_numbers_status(),
                    use_container_width=True,
                )
            with zone_button_right:
                if push_button:
                    st.write(f'Current Numbers pushed: {session_get("current_numbers")["today_date"]}')
                if restore_button:
                    st.write(f'Current Numbers restored: {session_get("current_numbers")["today_date"]}')

#endregion

#region Form: model_numbers
with right_form:
    st.subheader(
        "My Model Parameters",
        help="These parameters should be set from the start to reasonable values and hardly ever retouched in the future"
    )
    my_model_numbers : dict = session_get('model_numbers')
    rf_container = st.container(border=True)
    with rf_container:
        left_right_form, right_right_form = rf_container.columns([0.5,0.5])
        with left_right_form:
            start_date = st.empty()
            fwd_inflation = st.empty()
            nb_wk_yrs = st.empty()
        with right_right_form:
            contrib_increase = st.empty()
            fwd_market_rate = st.empty()
            nb_ret_yrs = st.empty()
        ctb_inc_mth = st.empty()

        if is_session_loaded():
            zone_button_left_2, zone_button_mid_2, zone_button_right_2 = rf_container.columns([0.2,0.2,0.6])
            with zone_button_left_2:
                push_button_2 = st.button(
                    "Push", 
                    key="model_push_button",
                    on_click=push_model_numbers_data,
                    disabled=check_model_numbers_status(),
                    use_container_width=True,
                )
            with zone_button_mid_2:
                restore_button_2 = st.button(
                    "Restore", 
                    key="model_restore_button",
                    on_click=restore_model_numbers_data,
                    disabled=check_model_numbers_status(),
                    use_container_width=True,
                )
            with zone_button_right_2:
                if push_button_2:
                    st.write(f'Model Numbers pushed {my_model_numbers["update_time"]}')
#endregion

if is_session_loaded():
    my_date_selection.selectbox(
        "Past Entries: ",
        key="date_selection",
        options= list(range(len(my_dates))),
        index=my_dates.index(current_today) if (current_today in my_dates) else 0,
        disabled=len(my_dates)==1,
        on_change=on_change_date,
        format_func=lambda x: str(my_dates[x])
    )
    

#region Filling Placeholders: current numbers
today_date.date_input(
    "Today date",
    value=session_get('today_date', PENSION_SESSION),
    on_change=on_change_today_date,
    disabled=session_get('today_date', PENSION_SESSION) in session_get('historical_numbers').keys(),
    key='today_date'
)
crt_amount.number_input(
    "Total Amount", 
    value=session_get('current_amount', PENSION_SESSION),
    on_change=on_change_current_amount,
    key='current_amount'
)
crt_contrib.number_input(
    "Current Monthly Contribution",
    value=session_get('current_contrib', PENSION_SESSION),
    on_change=on_change_current_contrib,
    key='current_contrib'
)
#endregion

#region Filling Paceholders: model numbers
start_date.date_input(
    "Start Date", 
    value=session_get('start_date', PENSION_SESSION),
    on_change=on_change_start_date,
    key='start_date',
    help="Your carreer start date",
)
fwd_inflation.number_input(
    "Inflation Prevision (Yearly %)", 
    value=session_get('inflation_rate', PENSION_SESSION) * 100.0,
    on_change=on_change_inflation_rate,
    key='inflation_rate',
    help='yearly inflation rate used for future dates between today\'s date and start of retirement'
)
nb_wk_yrs.number_input(
    "Number Of Working Years", 
    value=session_get('number_of_working_years', PENSION_SESSION),
    on_change=on_change_number_of_working_years,
    key='number_of_working_years',
    help='total number of working years from beginning of carreer to its end'
)
contrib_increase.number_input(
    "My Contribution Increases (Yearly %)",
    value=session_get('contrib_increase', PENSION_SESSION) * 100.0,
    on_change=on_change_contrib_increase,
    key='contrib_increase',
    help='how much do my total contribution to my retirement is going to increase very year in average until my retirement'
)
fwd_market_rate.number_input(
    "ROI Prevision (Yearly %)", 
    value=session_get('market_rate', PENSION_SESSION) * 100.0,
    on_change=on_change_market_rate,
    key='market_rate',
    help="Return Over Investement",
)
nb_ret_yrs.number_input(
    "Number Of Retirement Years", 
    value=session_get('number_of_retirement_years', PENSION_SESSION),
    on_change=on_change_number_of_retirement_years,
    key='number_of_retirement_years',
    help='total number of years of retirement (with pension)\nwhat you could set it to 100 years old - retirement age\n if you started working at 25yo, this variable would be 35'
)
ctb_inc_mth.multiselect(
    'Contribution Increase Month',
    options=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    default=session_get('contrib_increase_month', PENSION_SESSION),
    on_change=on_change_contrib_increase_month,
    key='contrib_increase_month',
    help='on which month do you increase your pension contribution (maintaining your yearly contribution increase identical)',
)
#endregion

st.markdown("---")


_,mid,_=st.columns(3)
with mid:
    table_head = st.empty()
    table_result = st.empty()

    with st.spinner("Computing ..."):
        time.sleep(1.5)

#region Computation
ms = model_statics(
    forward_inflation_rate=st.session_state.inflation_rate / 100.0,
    forward_market_rate=st.session_state.market_rate / 100.0,
    working_number_years=st.session_state.number_of_working_years,
    retirement_number_years=st.session_state.number_of_retirement_years,
    contribution_increase_month_list=st.session_state.contrib_increase_month,
    annual_contribution_increase_rate = st.session_state.contrib_increase / 100.0
)

month_id = get_month_id(st.session_state.start_date, st.session_state.today_date)
res = simulate_pension_fund(
    start_date=st.session_state.start_date,
    month_id=month_id,
    current_amount=st.session_state.current_amount,
    current_contribution=st.session_state.current_contrib,
    statics=ms,
)
res_final:simulate_pension_struct=res[-1]
res = pd.DataFrame()
res["Final Amount"] = [round(res_final.amount,2), round(res_final.real_amount,2)]
res["Fix Monthly"] = res["Final Amount"].apply(
    lambda x: round(
        calculate_fix_pension_from_fund(
            x, 
            st.session_state.number_of_retirement_years, 
            st.session_state.market_rate / 100.0
        ),
        2
    )
)
res.index = ["Nominal", "Real"]
tax_rate = round(calculate_all_taxes(res.loc["Real", "Fix Monthly"] * 12).loc["Total", "Tax Rate (%)"], 2)
res["Fix Monthly Net"] = res["Fix Monthly"].apply(lambda x: round(x * (1-tax_rate/100.0),2))

#rendering
table_head.subheader("My Results")
table_result.dataframe(res.T, width=500)

#endregion
    
st.text(f"The next contribution month is: {get_next_contribution_month(st.session_state.start_date, month_id)}")

# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
