import streamlit as st
import calc_helper as ch
import get_data as gd

policy_decisions = ch.get_fomc_decision_data()[3]
trade_date = gd.get_futures_data()[0]

st.set_page_config(
    page_title="Rate Hike Probabilities",
    page_icon="📈"
)

st.title("Fed Rate Hike Probabilities")

col1, col2 = st.columns(2)

col1.metric("Next Policy Decision", policy_decisions['Policy Decision'][0])
col2.metric("Policy Decision Confidence", "{0:.0%}".format(policy_decisions['Decision Confidence'][0]))

st.write("This will calculate the rate hike probabilities for the rest of 2023 based on futures data from ", trade_date)

st.header("Predicted FOMC Decisions")
st.dataframe(policy_decisions)