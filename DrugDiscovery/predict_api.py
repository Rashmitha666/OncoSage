import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
PREPROCESS_DIR = os.path.join(BASE_DIR, "Data PreProcessing")

DATA_DIR = os.path.join(BASE_DIR, "Data")

# Load model and resources
model = joblib.load(os.path.join(PREPROCESS_DIR, "drug_response_model.pkl"))
encoder = joblib.load(os.path.join(PREPROCESS_DIR, "feature_encoder.pkl"))
df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_data.csv"))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        user_df = pd.read_csv(file)
        user_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

        key_cols = ["drug_target", "target_pathway", "feature_name"]
        matched_rows = df.copy()
        for col in key_cols:
            matched_rows = matched_rows[matched_rows[col] == user_df.at[0, col]]

        matched_drug_names = matched_rows["drug_name"].unique().tolist()

        categorical_cols = ["drug_target", "target_pathway", "feature_name", "tissue_type", "screening_set"]
        numeric_cols = [col for col in user_df.columns if col not in categorical_cols]

        X_cat = encoder.transform(user_df[categorical_cols])
        X_num = user_df[numeric_cols].to_numpy()
        X_user = np.hstack((X_cat, X_num))

        predicted_ic50 = float(model.predict(X_user)[0])

        return jsonify({
            "predicted_ic50_effect_size": predicted_ic50,
            "matched_drug_names": matched_drug_names if matched_drug_names else "No matching drug found"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)