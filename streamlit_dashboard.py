import streamlit as st
import requests

API_URL = "https://cloudcore-churn.onrender.com/results"

st.title("CloudCore — Customer Churn Risk")

if st.button("Refresh"):
    st.rerun()

data = requests.get(API_URL).json()
df = pd.DataFrame(data)

if df.empty:
    st.info("No scored customers yet.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("High Risk", len(df[df["Churn Risk"] == "High"]))
    col2.metric("Medium Risk", len(df[df["Churn Risk"] == "Medium"]))
    col3.metric("Low Risk", len(df[df["Churn Risk"] == "Low"]))

    st.subheader("Pending Review — High Risk")
    st.dataframe(df[df["Churn Risk"] == "High"])

    st.subheader("All Customers")
    st.dataframe(df)

    st.bar_chart(df["Churn Risk"].value_counts())
