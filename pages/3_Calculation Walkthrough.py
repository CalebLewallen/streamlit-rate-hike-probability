import streamlit as st
import calc_helper as ch
from streamlit_extras.switch_page_button import switch_page
import fed_funds_probability as ffp
import pandas as pd
import format_helper as fh
import get_data as gd
# import graphviz

st.set_page_config(
    page_title="Calculation Walkthrough",
    page_icon="🧮",
    layout="wide"
)

policy_decisions = ch.get_fomc_decision_data()[3]


### PAGE TITLE AND SETUP ###
with st.container():

    # This column setup lets me control the width of text content and allow tables to go full width
    col1_1, col1_2, col1_3 = st.columns([1, 4, 1])

    col1_2.title("Calculating Policy Decision Probabilities")

    col1_2.image(r"https://images.unsplash.com/photo-1605870445919-838d190e8e1b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1400&h=400&q=80")

    col1_2.markdown("What follows is an explanation of how to use fed fund futures data to calculate the probability of a FOMC policy decision \
                at a given meeting. You need to have an understanding on how Fed Funds Futures contracts work before building \
                a probability tree. You can read the explanation on the Fed Funds Futures page if you haven't already.")

    # Fed Funds walkthrough page
    go_to_calculation_explanation = col1_2.button("Go To Fed Funds Futures Page")
    if go_to_calculation_explanation:
        switch_page("Fed Funds Futures")

    st.divider()


### COLLECT CME GROUP FED FUNDS DATA ###
with st.container():

    col2_1, col2_2, col2_3 = st.columns([1, 4, 1])

    col2_2.subheader("Step 1: Collect Futures Data")
    col2_2.markdown("Below is a table of futures data. You can get this data from the CME Group. This data is publicly available on a delayed basis. That's totally fine, we're not trading on this information, \
                we're just trying to get a pulse on how likely the market thinks a rate hike is.")
    col2_2.markdown("[CME Group - Fed Funds Futures Data](https://www.cmegroup.com/markets/interest-rates/stirs/30-day-federal-fund.quotes.html)")
    col2_2.markdown("Expand the table below to see all of the available data. We're primarily going to be concerned with the \'last\' and \'expirationDate\' columns")

    st.dataframe(ch.get_fomc_decision_data()[0])
    st.markdown("*Source: CME Group*")
    st.divider()


### GET FOMC MEETING DATES ###
with st.container():

    col3_1, col3_2, col3_3 = st.columns([1, 4, 1])

    col3_2.subheader("Step 2: Get FOMC Meeting Dates")
    col3_2.markdown("Policy Decisions are typically going to happen on predetermined meeting dates (outside of black swan events that require immediate action), so we'll need \
                to cross-reference our futures data with our FOMC meeting dates to figure out when we can expect a policy change to occur.")

    fomc_meetings = pd.DataFrame(ffp.retrieve_fomc_meeting_dates(), columns=['FOMC Meeting Dates'])
    col3_2.table(fomc_meetings)

col4_1, col4_2, col4_3 = st.columns([1, 4, 1])
col4_2.markdown("You can get this data from the [FOMC's website](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm). Note that decisions are announced on the second day of the meeting, therefore you \
            only need to collect the second date of each meeting.")

st.divider()


### MAP OUT PROJECTED RATE MOVEMENTS ###

current_effr = gd.get_effr()

with st.container():
    col5_1, col5_2, col5_3 = st.columns([1, 4, 1])
    col5_2.subheader("Step 3: Build Projected Rate Movements")
    col5_2.markdown("This step involves taking our futures pricing and calculating the implied rates and rate movements that occur in a given month. Our goal is to calculate Fed Funds at the start of the month vs the end, and then seeing the difference between the two. We're going to make a few assumptions when we work with this data:")

    col5_2.markdown("- The Beginning Rate for a month is simply the Ending Rate for the prior month. The exception to this is when there is no Fed Meetings.")
    col5_2.markdown("- Rate movements only occur in months with Fed Meetings. Since we know the rate at the beginning of the month and the implied rate per the futures data, we can calculate the end rate with:")
    col5_2.markdown("$r_{ending} = ((r_{implied} / days_{total}) - (r_{begin} * days_{priortochange})) / days_{afterchange}$")
    col5_2.markdown("- We can only calculate probabilities as far out as we have planned FOMC Meetings. This means that as we approach the latter half of the year, we can only project out a couple of meetings until the FOMC publishes next year's meeting schedule.")

    col5_2.markdown("Current EFFR: " + str('{:.3f}'.format(current_effr)))

    st.dataframe(ch.get_fomc_decision_data()[1], use_container_width=True)

    st.divider()


### BUILD THE PROBABILITY TREE ###
with st.container():

    col6_1, col6_2, col6_3 = st.columns([1, 4, 1])

    col6_2.subheader("Step 4: Probability Tree")

    col6_2.markdown("Calculating the probability tree occurs in two stages. The first is in the \'Front Meeting\', which is just the very next meeting after today. This done by dividing the expected rate change by the expected policy move. \
                Historically, this is typically 25 bps, although in recent memory it has been by as much as 75bps at a time.")
    col6_2.markdown("$Policy Change Probability = Expected Rate Change / Expected Policy Move$")
    col6_2.markdown("As an example, if the front meeting has an expected rate change of 12.5 bps, and we expect that the FOMC's policy change is 25 bps change, then we would say there's a 50\% likelihood of a hike.")
    col6_2.markdown("As we move further down the probability tree, things get a little little more complex, but not all that much more. In concept, what we're trying to figure out is the probability that we land on one of the nodes in the chart below. \
                For example, in the n2 nodes below (representing 2 meetings ahead of today), what's the likelihood that we will have experienced 2 hikes (n2(++))? What about no hike and then a hike (n2(+))?")

    col7_1, col7_2, col7_3 = st.columns([1, 1, 1])
    col7_2.graphviz_chart('''
        digraph{
            "n0" -> "n1"
            "n0" -> "n1(+)"
            "n1" -> "n2"
            "n1" -> "n2(+)"
            "n1(+)" -> "n2(+)"
            "n1(+)" -> "n2(++)"
        }
    ''')

with st.container():

    col8_1, col8_2, col8_3 = st.columns([1, 4, 1])
    col8_2.markdown("The way we accomplish this is by first calculating the isolated probabilities of each meeting. In other words, what's the likelihood of a rate movement for a given meeting, based solely on the expected rate movement?")
    col8_2.markdown("Next, we'll use those isolated probabilities to figure out if the anticipated policy change is a hike or a cut, based on whether the isolated probabilities are positive or negative.")
    col8_2.markdown("The formula we'll use to calculate the probability of one of our nodes is: $(p_{hikeNow}*p_{noHikePreviousMonth}) + ([1 - p_{hikeNow}] * p_{hikePreviousMonth})$ where \'p\' is probability. If futures data indicates a \
                    cut, then you would simply reverse the direction of the formula.")
    
    # Add a gap between text and dataframe
    st.text("")

    # This will apply all the necessary styling to the probability tree df
    probability_tree_headers = ch.get_fomc_decision_data()[4]
    complete_probability_tree = ch.get_fomc_decision_data()[2].style.applymap(fh.highlight_nonzero_cells, subset=pd.IndexSlice[:, probability_tree_headers])
    st.dataframe(complete_probability_tree, use_container_width=True)
    st.divider()


### POLICY DECISION CHART ###
with st.container():

    col9_1, col9_2, col9_3 = st.columns([1, 4, 1])

    col9_2.subheader("Policy Decision Prediction")

    col9_2.markdown("This is probably the most straightforward of the concepts we've talked over today. Now that we have our probability tree built, we can start with deducing the project policy decisions.")
    col9_2.markdown("We'll begin by marking the FF range we're currently in. We'll add up all of the probabilities above and below that range, excluding the value from the current range. Once the summed probabilities \
                exceeds a pre-defined threshold (in my case, 50%), then we'll mark a policy decision and move our mark up or down into a new FF range. From that, we'll repeat the process. You can tweak this \
                process according to your risk thresholds by adjusting the move threshold up or down.")

    col9_2.dataframe(policy_decisions, use_container_width=True)