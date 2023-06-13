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

    col2.markdown("Caleb is an experienced professional with a diverse background spanning nearly a decade. Beginning his \
    career on the trading desk of an interest rate strategy advisor, he quickly established himself as an \
    analyst/quant and eventually took on the responsibility of running the trading desk. He played a pivotal role in \
    the founding of LoanBoss, a SaaS product, where he initially led product development before transitioning to \
    the head of product strategy. He recently took charge of a new team, assuming the role of head of data \
    strategy to establish and lead a team in optimizing data practices as they expanded into new customer \
    segments. You can connect with Caleb on [LinkedIn](https://www.linkedin.com/in/caleb-lewallen-b8699365/).")

    bio_image = Image.open("files/caleb.png")

    col1.image(bio_image, caption='Caleb Lewallen', width=180)