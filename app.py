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


def load_csv() -> pd.DataFrame:
    if not os.path.exists(OUTPUT_FILE):
        return pd.DataFrame()
    df = pd.read_csv(OUTPUT_FILE)
    return df if not df.empty else pd.DataFrame()


def save_csv(df: pd.DataFrame):
    df.to_csv(OUTPUT_FILE, index=False)


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

    # ── Upsert: replace existing row for this CustomerID, never append duplicates
    df = load_csv()
    if not df.empty and "CustomerID" in df.columns:
        df = df[df["CustomerID"].astype(str) != str(result["CustomerID"])]

    df = pd.concat([df, pd.DataFrame([result])], ignore_index=True)
    save_csv(df)

    return jsonify(result), 200


@app.route("/results", methods=["GET"])
def results():
    df = load_csv()
    if df.empty:
        return jsonify([])

    # Deduplicate on CustomerID, keeping the most recent score (last occurrence)
    if "CustomerID" in df.columns:
        df = df.drop_duplicates(subset=["CustomerID"], keep="last")

    return jsonify(df.to_dict(orient="records"))


@app.route("/count", methods=["GET"])
def count():
    """Diagnostic — returns unique customer count and raw CSV row count."""
    df = load_csv()
    if df.empty:
        return jsonify({"unique_customers": 0, "raw_rows_in_csv": 0})

    raw = len(df)
    unique = df["CustomerID"].nunique() if "CustomerID" in df.columns else raw
    return jsonify({"unique_customers": unique, "raw_rows_in_csv": raw})


@app.route("/reset", methods=["POST"])
def reset():
    """
    Clears scored_output.csv entirely for a clean reload.
    Optionally protected — set RESET_TOKEN in Render env vars.
    Call this before running loadAllExistingCustomers for a fresh start.
    """
    token = os.environ.get("RESET_TOKEN", "")
    if token:
        provided = (request.get_json(silent=True) or {})
        if provided.get("token") != token:
            return jsonify({"error": "Unauthorized"}), 401

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        return jsonify({"status": "scored_output.csv cleared"}), 200
    return jsonify({"status": "Nothing to clear"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
