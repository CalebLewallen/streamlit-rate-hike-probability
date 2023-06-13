import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="Calculation Walkthrough",
    page_icon="🧮",
    layout="centered"
)

st.title("What are Fed Funds Futures?")

st.image(r"https://images.unsplash.com/photo-1618044733300-9472054094ee?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&h=400&q=80")

st.markdown("Fed Funds Futures are contracts against the value of Fed Funds. They're quoted as a price instead of a rate, like we're typically used to seeing. It's okay through, in order to covert to a rate, simply subtract the contract price from 100.")
st.markdown("For example, if the contract you're viewing is priced at 94.88, then the implied rate in that contract is:")
st.latex("100 - 94.88 = 5.12")

st.subheader("Contract Data")
st.markdown("Contracts for Fed Funds Futures are quote monthly, and have an expiry on the last day of every single month. When you get quoted a series of these contracts, they'll look something like this:")

df = {'Quote Code': ["ZQM3","ZQN3","ZQQ3","ZQU3","ZQV3","ZQX3","ZQZ3"],
    'Expiry Month':["06/01/2023","07/01/2023","08/01/2023","09/01/2023","10/01/2023","11/01/2023","12/01/2023"],
        'Price': [5.12,5.175,5.285,5.275,5.25,5.145,5.055]
}

fed_funds_quotes_table = pd.DataFrame(df)
st.table(fed_funds_quotes_table)

st.markdown("I know what you're thinking, \"But isn't fed funds and overnight rate? How is the contract monthly?\" I'm glad you asked.")

st.subheader("Contract Pricing")
st.markdown("Fed Funds futures are quoted as the ***average*** fed funds settlement over a given month. So if FF is 5.125\% for the first half of the month, and 5.375\% for the last half, then the contract will settle at 5.25\%.")

month_array = {'Day': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30],
            'Daily Rate': [5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.125,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375,5.375],
            'Settlement Rate': [5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25,5.25]
            }

month_df = pd.DataFrame(month_array)
chart_x_axis_name = 'Day of Month'

monthly_line_chart = px.line(month_df, x=month_df['Day'], y=[month_df['Daily Rate'], month_df['Settlement Rate']])

st.plotly_chart(monthly_line_chart, use_container_width=True)



st.subheader("FOMC Meetings")
st.markdown("Ok, so how does this help us calculate the odds of a policy move? The FOMC has an iron grip over the front end of the yield curve. \
            They decide what the overnight rate is going to be and uses a trading desk in downtown Manhattan to keep settlement prices within a given range. \
            With this in mind, knowing that only a Fed action can influence those contract rates up or down by more than a bp or two, we can start piecing together the expected path of hike.\
            Go to the Calculation Walkthrough page to see for info.")

go_to_calculation_explanation = st.button("Go To Calculation Walkthrough Page")
if go_to_calculation_explanation:
    switch_page("Calculation Walkthrough")