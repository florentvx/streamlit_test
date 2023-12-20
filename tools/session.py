from __future__ import annotations
import streamlit as st

MY_SESSION = 'my_session'
NO_NAME_SESSION = "<INPUT YOUR SESSION NAME HERE>"

def get_session() -> dict:
    return st.session_state[MY_SESSION]

def session_get(key, sub_category = None):
    return st.session_state[MY_SESSION if sub_category is None else sub_category].get(key, None)

def is_session_loaded() -> bool:
    return session_get('name') != NO_NAME_SESSION

def full_session_set(session):
    st.session_state[MY_SESSION] = session

def reset_session():
    st.session_state[MY_SESSION] = { 'name': NO_NAME_SESSION }

def session_set(key, value, sub_category = None):
    st.session_state[MY_SESSION if sub_category is None else sub_category][key] = value

def session_init(key, init_value):
    if key not in get_session().keys():
        session_set(key, init_value)