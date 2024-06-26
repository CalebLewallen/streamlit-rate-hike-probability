import streamlit as st
from PIL import Image

st.set_page_config(
        page_title="Calculation Walkthrough",
        page_icon="files/Fibonacci.png",
        layout="centered"
)

st.header("About the Author")

with st.container():

    col1, col2 = st.columns([2,5])

    col2.markdown("""
                  Caleb is an experienced professional with a diverse background spanning nearly a decade. Beginning his
    career on the trading desk of an interest rate strategy advisor, he quickly established himself as an
    analyst/quant and eventually took on the responsibility of running the trading desk. He played a pivotal role in
    the founding of LoanBoss, a SaaS product, where he initially led product development before transitioning to
    the head of product strategy. He then took charge of a new team, assuming the role of head of data
    strategy to establish and lead a team in optimizing data practices as they expanded into new customer
    segments. Caleb is now working for Wells Fargo, where he is building an operational data capability within the
    bank. You can connect with Caleb on [LinkedIn](https://www.linkedin.com/in/caleb-lewallen-b8699365/)."""
    )
    
    col2.markdown("See some of Caleb's writing at https://caleblewallen.com/")

    bio_image = Image.open("files/caleb.png")

    col1.image(bio_image, caption='Caleb Lewallen', width=180)



with st.container():
    
    st.subheader("Source Code")

    st.markdown("You can view the source code for this site at the following repo: [streamlit-rate-hike-probability](https://github.com/CalebLewallen/streamlit-rate-hike-probability)")