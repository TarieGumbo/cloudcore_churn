from flask import Flask, request, jsonify
from scoring_logic import score_customers
import pandas as pd
import os

app = Flask(__name__)

OUTPUT_FILE = "scored_output.csv"

def score_customer(row: dict) -> dict:
    df = pd.DataFrame([row])
    df = score_customers(df)
    return df.to_dict(orient="records")[0]
    
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "CloudCore churn API is running"})


@app.route("/score", methods=["POST"])
def score():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    required = ["CustomerID", "Usage Drop", "Number of Support Tickets", "Payment Delay"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    result = score_customer(data)

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
    if df.empty:
        return jsonify([])
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
