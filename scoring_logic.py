import pandas as pd

def load_data(filepath="MOCK_Data_v2.xlsx"):
    return pd.read_excel(filepath)

def score_customers(data):
    data["Payment Delay"] = data["Payment Delay"].str.lower().str.strip()

    # Step 1: Default = Low
    data["Churn Risk"] = "Low"

    # Step 2: Medium risk
    data.loc[
        (data["Usage Drop"] > 0.15) &
        (data["Number of Support Tickets"] > 2),
        "Churn Risk"
    ] = "Medium"

    # Step 3: High risk
    data.loc[
        (data["Usage Drop"] > 0.30) &
        (data["Number of Support Tickets"] > 3) &
        (data["Payment Delay"] == "yes"),
        "Churn Risk"
    ] = "High"

    return data

if __name__ == "__main__":
    df = load_data()
    df = score_customers(df)
    print(df["Churn Risk"].value_counts())
