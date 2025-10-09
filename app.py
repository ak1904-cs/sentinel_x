import streamlit as st
from nlp_engine import calculate_risk

st.title("🛡️ Sentinel-X: Counter-Terrorism OSINT Analysis")
st.write("Enter any text, post, or message below:")

text = st.text_area("Text to analyze:", height=150)

if st.button("Analyze"):
    if text.strip():
        risk = calculate_risk(text)
        st.success(f"⚠️ Risk Score: {risk}")
        if risk > 0.7:
            st.error("High Risk – possible extremist content.")
        elif risk > 0.4:
            st.warning("Medium Risk – monitor closely.")
        else:
            st.info("Low Risk – seems normal.")
    else:
        st.warning("Please enter some text to analyze.")
