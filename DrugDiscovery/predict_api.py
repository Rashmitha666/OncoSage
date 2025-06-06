from flask import Flask, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

model = joblib.load("./DrugDiscovery/Data PreProcessing/drug_model.pkl")
le_drug_name = joblib.load("./DrugDiscovery/Data PreProcessing/le_drug_name.pkl")

@app.route("/predict", methods=["POST"])

def predict():
    
    try:
        file = request.files["file"]
        user_df = pd.read_csv(file)

        
        for col in ["drug_target", "target_pathway", "feature_name", "tissue_type", "screening_set"]:
            le = joblib.load(f"./DrugDiscovery/Data PreProcessing/le_{col}.pkl")
            user_df[col] = le.fit_transform(user_df[col])

        predicted_class = model.predict(user_df)[0]
        predicted_drug = le_drug_name.inverse_transform([predicted_class])[0]
        
        return jsonify({"recommended_drug": predicted_drug})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
