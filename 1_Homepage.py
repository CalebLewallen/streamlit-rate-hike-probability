import streamlit as st
import calc_helper as ch
import get_data as gd
import plotly.express as px

policy_decisions = ch.get_fomc_decision_data()[3]
trade_date = gd.get_futures_data()[0]

st.set_page_config(
    page_title="Rate Hike Probabilities",
    page_icon="📈"
)

# with st.sidebar():
#     st.image(r"https://caleblewallen.com/content/images/2023/02/Logo--3-.png")

st.title("Fed Rate Hike Probabilities")

st.image(r"https://images.unsplash.com/photo-1452696193712-6cabf5103b63?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&h=400&q=80")

st.markdown("One of the most sought after questions during any tightening or loosening cycle is what the next policy decision is going to be from the FOMC. \
            Every armchair economist takes to Twitter and LinkedIn leading up to each meeting about why their contrarian viewpoint will hold true. Since I'm not \
            as smart as those individuals, I instead have to rely on what the market says about each meeting. To do this, we only need to look as far as a single \
            futures market, and apply some statistical principals.")

st.divider()

col1, col2 = st.columns(2)

col1.metric("Next Policy Decision", policy_decisions['Policy Decision'][0])
col2.metric("Policy Decision Confidence", "{0:.0%}".format(policy_decisions['Decision Confidence'][0]))

st.write("Punch line first. Below are the market implied policy moves by the FOMC for all of the meetings that are currently scheduled past today, along with the confidence level for the meeting. \
         Notice that the further into the future the meeting is, the confidence level decreases. This should intuitively make sense, since we're less and less sure about events into the future, both \
         from a time perspective *and* the fact each meeting's policy decision is influenced by what happens prior. Data comes from the CME Group and was last updated on " + trade_date + ".")

st.header("Predicted FOMC Decisions")
st.dataframe(policy_decisions, use_container_width=True)

fig = px.bar(policy_decisions, x='Meeting', y='Policy Range Midpoint', color='Decision Confidence',
             color_continuous_scale='blues')
fig.update_xaxes(type='category')
fig.update_yaxes(range=[4, 5.5])
st.plotly_chart(fig)