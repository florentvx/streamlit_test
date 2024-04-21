import logging
import math
import asyncio
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
import yaml

from tools import set_page_config, init_queue
from tools.session import *


#put_in_queue, my_callback_loop = init_queue("HOME")

set_page_config()

if st.session_state.get('my_session', None) is None:
    reset_session()

st.header("My Pension Calcultor & Simulator")

if not is_session_loaded():
    st.subheader("To Start a session: \n - either name the session below \n - or drop your session's YAML below.")

def change_name():
    session_set('name', st.session_state.new_name)

new_name = st.text_input(
    label="Session Name: ", 
    value=session_get('name'), 
    on_change=change_name, 
    key='new_name',
)

# st.sidebar.header("sidebar")
# option_ms = [f"{i}" for i in range(1,6)]
# my_var = st.sidebar.multiselect(
#     "select var",
#     options=option_ms,
#     default=[option_ms[0], option_ms[-1]]
# )

uploaded_file = None
uploader_shown = False
if not is_session_loaded():
    uploaded_file = st.file_uploader('Choose yaml file:', type='yaml')
    uploader_shown = True
    
if uploaded_file is not None:
    st.markdown("---")
    full_session_set(yaml.safe_load(uploaded_file))

if is_session_loaded():
    my_yaml_data_to_download = yaml.dump(get_session())
    st.download_button(
        label="Download Session", 
        file_name=f'pension_simulator_{"".join(e for e in session_get("name") if e.isalnum())}.yaml',
        mime = 'application/x-yaml',
        data=my_yaml_data_to_download
    )
    st.button("Log Out", on_click=reset_session)
    if uploader_shown:
        st.rerun()

st.markdown('---')

if is_session_loaded():
    st.title(":pencil2: My yaml data")

    st.text(
        '\n'.join([
            f'{k}: {v}' if not isinstance(v, dict) else f'{k}: ' + (
                '\n - ' + '\n - '.join([
                    f'{vk}: {vv}' for (vk, vv) in v.items()
                ])
            )
            for (k,v) in get_session().items()
        ])
    )

    st.markdown('-----')

# st.title(':pencil2:  Numbers')
# #st.markdown("##")
# st.text(sum(map(float,my_var)))

# left_col, midd_col, right_col = st.columns([0.25,0.5,0.25])
# with left_col:
#     st.text("My Stars")
# with midd_col:
#     st.markdown(":star:" * 6)
# with right_col:
#     st.text("it was great right?")

# st.markdown("---")

# df = pd.DataFrame()
# df['x'] = [i/100. for i in range(1000)]
# df['y'] = df['x'].apply(lambda x: math.sin(x))
# my_line_chart = px.line(
#     df, 
#     x="x", 
#     y="y",
#     title="<b>My Special Line Chart</b>",
#     template="plotly",
# )

# midd_col.plotly_chart(my_line_chart, use_container_width=True)

# hide streamlit style
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)



# do_rerun=False
# try:
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     do_rerun = asyncio.run(my_callback_loop())
# except Exception as e:
#     logging.error(e)
#     do_rerun = False
# finally:
#     print(f"Closing loop - dorerun {do_rerun}")
#     loop.close()
#     if do_rerun:
#         st.rerun()

