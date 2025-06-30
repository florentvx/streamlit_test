import streamlit as st
import datetime as dt
from .callback import init_queue
from .session import get_session

def set_page_config():
    st.set_page_config(
        page_title='Pension Calculator',
        page_icon=":green_book:",
        layout="wide",
    )

def get_month_id(start_date: dt.date, end_date: dt.date):
    year_diff = (st.session_state.today_date.year - st.session_state.start_date.year)
    month_diff = st.session_state.today_date.month - st.session_state.start_date.month
    delta = -1 if st.session_state.today_date.day < 15 else 0
    return year_diff * 12 + month_diff + delta

def get_next_contribution_month(start_date: dt.date, month_id: int):
    new_month = start_date.month+month_id
    year_delta = int(new_month / 12)
    end_month = new_month - 12 * year_delta + 1
    return dt.date(start_date.year + year_delta, end_month, 1)

__all__ = ["init_queue", "get_session", "set_page_config", "get_month_id", "get_next_contribution_month"]