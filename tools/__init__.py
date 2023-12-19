import streamlit as st
from .callback import init_queue

NO_NAME_SESSION = "<INPUT YOUR SESSION NAME HERE>"

def set_page_config():
    st.set_page_config(
        page_title='My Data',
        page_icon=":green_book:",
        layout="wide",
    )
