from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.express as px
from enum import Enum

from pension_simulator import model_statics, simulate_pension_fund

from tools.session import *
from tools import set_page_config


class graph_choice(Enum):
    TOTAL_AMOUNT = 0
    MONTHLY_CONTRIB = 1
    FINAL_AMOUNT = 2
    NUMBER = 3

    def get_string(self) -> str:
        names = self.name.split("_")
        return " ".join([
            n[0].upper() + n[1:].lower()
            for n in names
        ])
    
    def do_need_calculation(self) -> bool:
        return self.value == graph_choice.FINAL_AMOUNT.value

    @classmethod
    def get_list(self) -> list[str]:
        return [graph_choice(n).get_string() for n in range(graph_choice.NUMBER.value)]
    
set_page_config()

st.title(":bar_chart: Historical Data")

if st.session_state.get('my_session', None) is None:
    reset_session()

if not is_session_loaded():
    st.text("you need to load a session first")

else:
    hist_data = session_get('historical_numbers')

    df_data = pd.DataFrame(
        [
            [x, hist_data[x]['current_amount'], hist_data[x]['current_contrib'], 0] 
            for x in hist_data.keys()
        ],
        index=hist_data.keys(),
        columns=['Date'] + graph_choice.get_list()
    )
    st.dataframe(df_data)
    
    st.markdown('---')
    radio_choice = st.radio(
        "Graph Choice: ", 
        graph_choice.get_list(), 
        index=0
    )

    graphs = {}
    mn = session_get('model_numbers')
    ms = model_statics(
        forward_inflation_rate=mn['inflation_rate'],
        forward_market_rate=mn['market_rate'],
        working_number_years=mn['number_of_working_years'],
        retirement_number_years=mn['number_of_retirement_years'],
        contribution_increase_month_list=mn['contrib_increase_month'],
        annual_contribution_increase_rate =mn['contrib_increase']
    )
    def get_graph_by_graph_choice(text_input):
        i=0
        while graph_choice(i).get_string() != text_input:
            i += 1
        gc_i = graph_choice(i)
        title = gc_i.get_string()
        if gc_i.do_need_calculation():
            df_data[title] = df_data.apply(
                lambda row: simulate_pension_fund(
                        start_date=mn['start_date'],
                        month_id=(row['Date'].year - mn['start_date'].year)*12 \
                            + row['Date'].month - mn['start_date'].month,
                        current_amount=row["Total Amount"],
                        current_contribution=row["Monthly Contrib"],
                        statics=ms,
                    )[-1].amount,
                axis = 1,
            )
        graphs[title] = px.line(
            df_data, 
            x="Date", 
            y=title,
            title=f"<b>{title}</b>",
            template="plotly",
        )
        return graphs[title]

    left_col, midd_col, right_col = st.columns([0.25,0.5,0.25])
    midd_col.plotly_chart(get_graph_by_graph_choice(radio_choice), use_container_width=True)

