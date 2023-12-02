import math

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import yaml

from tools import set_page_config


set_page_config()

NO_NAME_SESSION = "<INPUT YOUR SESSION NAME HERE>"
session_name = st.session_state.get('name', None)
if session_name is None:
    st.session_state['name'] = NO_NAME_SESSION

st.header("My Pension Calcultor & Simulator")

if st.session_state['name'] == NO_NAME_SESSION:
    st.subheader("To Start a session: \n - either name the session below \n - or drop your session's YAML below.")


new_name = st.text_input(label="Session Name: ", value=st.session_state['name'])
st.session_state['name'] = new_name


st.sidebar.header("sidebar")
option_ms = [f"{i}" for i in range(1,6)]
my_var = st.sidebar.multiselect(
    "select var",
    options=option_ms,
    default=[option_ms[0], option_ms[-1]]
)

uploaded_file = None
uploader_shown = False
if st.session_state['name'] == NO_NAME_SESSION:
    uploaded_file = st.file_uploader('Choose yaml file:', type='yaml')
    uploader_shown = True
    
if uploaded_file is not None:
    st.markdown("---")
    st.session_state = yaml.safe_load(uploaded_file)
    # #random use case
    # hist_infl = my_file['historical_inflation']
    # df = pd.DataFrame()
    # df["year"] = hist_infl.keys()
    # df['rate'] = df['year'].apply(lambda x: hist_infl[x])
    # #st.dataframe(df)
    # fig_inf = px.bar(
    #     df,
    #     x="year",
    #     y='rate',
    #     color='rate',
    #     color_continuous_scale=['green', 'yellow', 'red'],
    #     template='plotly_white',
    #     title=f'<b>Inflation Rate</b>'
    # )
    # st.plotly_chart(fig_inf)


def log_out():
    st.session_state.clear()
    st.session_state['name'] = NO_NAME_SESSION

if st.session_state['name'] != NO_NAME_SESSION:
    popo = yaml.dump(st.session_state)
    st.download_button(label="Download Session", file_name=f'pension_simulator_{st.session_state["name"]}.yaml', mime = 'application/x-yaml', data=popo)
    st.button("Log Out", on_click=log_out)
    if uploader_shown:
        st.experimental_rerun()

st.markdown('---')

if st.session_state['name'] != NO_NAME_SESSION:
    st.title(":pencil2: My yaml data")

    st.text(
        '\n'.join([
            f'{k}: {v}'
            for (k,v) in st.session_state.items()
        ])
    )

    st.markdown('-----')

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


# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
