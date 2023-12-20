import streamlit as st
from .callback import init_queue
from .session import *


def set_page_config():
    st.set_page_config(
        page_title='My Data',
        page_icon=":green_book:",
        layout="wide",
    )
