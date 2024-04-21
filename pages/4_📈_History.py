from __future__ import annotations
import pandas as pd
import streamlit as st
import plotly.express as px
from enum import Enum

from pension_simulator import model_statics, simulate_pension_fund, calculate_fix_pension_from_fund, \
    calculate_all_taxes, convert_price_with_inflation

from tools import set_page_config
from tools.session import *
from tools.inflation import inflation_dict


class graph_choice(Enum):
    TOTAL_AMOUNT = 0
    MONTHLY_CONTRIB = 1
    FINAL_AMOUNT = 2
    REAL_AMOUNT = 3
    FINAL_MONTHLY = 4
    REAL_MONTHLY = 5
    FINAL_NET = 6
    REAL_NET = 7
    NUMBER = 8

    def get_string(self) -> str:
        names = self.name.split("_")
        return " ".join([
            n[0].upper() + n[1:].lower()
            for n in names
        ])
    
    def do_need_calculation(self) -> bool:
        return self.value not in [graph_choice.TOTAL_AMOUNT.value, graph_choice.MONTHLY_CONTRIB.value, graph_choice.NUMBER.value]

    @classmethod
    def get_list(self, filter_on_calculation = False) -> list[str]:
        return [
            graph_choice(n).get_string() 
            for n in range(graph_choice.NUMBER.value) 
            if (not filter_on_calculation) or (not graph_choice(n).do_need_calculation())
        ]
    
set_page_config()

st.title(":bar_chart: Historical Data")

if st.session_state.get('my_session', None) is None:
    reset_session()

if not is_session_loaded():
    st.text("you need to load a session first")

else:
    hist_data = session_get('historical_numbers')
    mn = session_get('model_numbers')
    ms = model_statics(
        forward_inflation_rate=mn['inflation_rate'],
        forward_market_rate=mn['market_rate'],
        working_number_years=mn['number_of_working_years'],
        retirement_number_years=mn['number_of_retirement_years'],
        contribution_increase_month_list=mn['contrib_increase_month'],
        annual_contribution_increase_rate =mn['contrib_increase']
    )

    df_data = pd.DataFrame(
        [
            [x, hist_data[x]['current_amount'], hist_data[x]['current_contrib']] 
            for x in hist_data.keys()
        ],
        index=hist_data.keys(),
        columns=['Date'] + graph_choice.get_list(filter_on_calculation=True)
    )

    final_date = list(df_data['Date'])[-1]

    df_data["simulate_pension"] = df_data.apply(
        lambda row: simulate_pension_fund(
            start_date=mn['start_date'],
            month_id=(row['Date'].year - mn['start_date'].year)*12 \
                + row['Date'].month - mn['start_date'].month,
            current_amount=row["Total Amount"],
            current_contribution=row["Monthly Contrib"],
            statics=ms,
        )[-1],
        axis = 1,
    )

    df_data[graph_choice.FINAL_AMOUNT.get_string()] = df_data['simulate_pension'].apply(lambda x: x.amount)
    df_data[graph_choice.REAL_AMOUNT.get_string()] = df_data['simulate_pension'].apply(lambda x: x.real_amount)
    df_data[graph_choice.REAL_AMOUNT.get_string()] = df_data.apply(
        lambda row: convert_price_with_inflation(
            inflation_dict,
            row[graph_choice.REAL_AMOUNT.get_string()],
            row['Date'],
            final_date,
        ),
        axis=1
    )
    df_data["inflation_fx"] = df_data.apply(lambda row: row[graph_choice.REAL_AMOUNT.get_string()] / row['simulate_pension'].real_amount, axis = 1)

    df_data[graph_choice.FINAL_MONTHLY.get_string()] = df_data['simulate_pension'].apply(
        lambda x: calculate_fix_pension_from_fund(
            x.amount, mn['number_of_retirement_years'], mn['market_rate']
        ),
    )
    df_data[graph_choice.REAL_MONTHLY.get_string()] = df_data[graph_choice.REAL_AMOUNT.get_string()].apply(
        lambda x: calculate_fix_pension_from_fund(
            x, mn['number_of_retirement_years'], mn['market_rate']
        ),
    )
    df_data['tax_rate'] = df_data[graph_choice.REAL_MONTHLY.get_string()].apply(
        lambda x: round(calculate_all_taxes(x * 12).loc["Total", "Tax Rate (%)"], 2)
    )
    df_data[graph_choice.FINAL_NET.get_string()] = df_data.apply(
        lambda row: row[graph_choice.FINAL_MONTHLY.get_string()] * (1-row['tax_rate']/100),
        axis=1,
    )
    df_data[graph_choice.REAL_NET.get_string()] = df_data.apply(
        lambda row: row[graph_choice.REAL_MONTHLY.get_string()] * (1-row['tax_rate']/100),
        axis=1,
    )
    
    df_data=df_data[['Date'] + graph_choice.get_list() + ['tax_rate'] + ['inflation_fx']]

    df_data = df_data.sort_index()

    radio_choice = st.radio(
        "Graph Choice: ", 
        graph_choice.get_list(), 
        index=0
    )

    graphs = {}
    
    def get_graph_by_graph_choice(text_input):
        i=0
        while graph_choice(i).get_string() != text_input:
            i += 1
        gc_i = graph_choice(i)
        title = gc_i.get_string()
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


    
    st.markdown('---')
    st.dataframe(df_data)