import streamlit as st
import requests
import pandas as pd

#API_URL = "https://cloudcore-churn.onrender.com"
API_URL = st.secrets["API_URL"]

st.title("CloudCore — Customer Churn Risk")

if st.button("Refresh"):
    st.rerun()

try: 
    response = requests.get(API_URL).json()
    #force data to always be a list
    if isinstance (response, dict):
        data = [response] if response else []
    elif isinstance (response, list):
        data = response
    else: 
        data = []
        
    # Handle both a list of records and a single dict
    if not data: 
        st.info("No scored customers yet. Waiting for Zapier to send data")
    else: 
        df = pd.DataFrame(data)
         #show what columns exist 
        #st.write("Columns found:", df.columns.tolist())
        #st.write("Sample data:", df.head())

        if "Churn Risk" in df.columns:
            col1, col2, col3 = st.columns(3)
            col1.metric("High Risk", len(df[df["Churn Risk"] == "High"]))
            col2.metric("Medium Risk", len(df[df["Churn Risk"] == "Medium"]))
            col3.metric("Low Risk", len(df[df["Churn Risk"] == "Low"]))

            st.subheader("Pending Review — High Risk")
            st.dataframe(df[df["Churn Risk"] == "High"])

            st.subheader("All Customers")
            st.dataframe(df)

            st.bar_chart(df["Churn Risk"].value_counts())

        else: 
            st.warning("Churn Risk Column not found in data")
            st.dataframe(df)

except Exception as e:
    st.error(f"Could not connect to API: {e}")
