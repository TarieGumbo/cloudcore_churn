from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

OUTPUT_FILE = "scored_output.csv"

def score_customer(row: dict) -> dict:
    df = pd.DataFrame([row])

    # Clean exactly as in Code_v2.ipynb
    df["Payment Delay"] = df["Payment Delay"].str.lower().str.strip()
    df["Usage Drop"] = pd.to_numeric(df["Usage Drop"], errors="coerce")
    df["Number of Support Tickets"] = pd.to_numeric(df["Number of Support Tickets"], errors="coerce")

    # Step 1: Default = Low
    df["Churn Risk"] = "Low"

    # Step 2: Medium risk
    df.loc[
        (df["Usage Drop"] > 0.15) &
        (df["Number of Support Tickets"] > 2),
        "Churn Risk"
    ] = "Medium"

    # Step 3: High risk
    df.loc[
        (df["Usage Drop"] > 0.30) &
        (df["Number of Support Tickets"] > 3) &
        (df["Payment Delay"] == "yes"),
        "Churn Risk"
    ] = "High"

    return df.to_dict(orient="records")[0]


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "CloudCore churn API is running"})


@app.route("/score", methods=["POST"])
def score():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    # Validate required fields
    required = ["CustomerID", "Usage Drop", "Number of Support Tickets", "Payment Delay"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result = score_customer(data)

    # Append to CSV (create if it doesn't exist)
    df_result = pd.DataFrame([result])
    if os.path.exists(OUTPUT_FILE):
        df_result.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        df_result.to_csv(OUTPUT_FILE, index=False)

    return jsonify(result), 200


@app.route("/results", methods=["GET"])
def results():
    if not os.path.exists(OUTPUT_FILE):
        return jsonify([])
    df = pd.read_csv(OUTPUT_FILE)
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
