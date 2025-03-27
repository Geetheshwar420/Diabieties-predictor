from flask import Flask, render_template, request, jsonify
import os
import numpy as np
import tensorflow as tf
import pickle
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS

# ✅ Initialize Flask
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
CORS(app)  # ✅ Allow frontend to call API from different origins

# ✅ Paths to Model & Scaler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "glucose_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# ✅ Check if Model and Scaler exist
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found: {MODEL_PATH}")

if not os.path.exists(SCALER_PATH):
    raise FileNotFoundError(f"❌ Scaler file not found: {SCALER_PATH}")

# ✅ Load Model & Scaler
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
model.compile(optimizer="adam", loss="mean_squared_error")

with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

# ✅ Expected Feature Count
NUM_FEATURES = 72

# ✅ Route to Serve Frontend Page
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Prediction API
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # ✅ Validate JSON Structure
        if not data or "glucose_values" not in data:
            return jsonify({"error": "Missing 'glucose_values' in request"}), 400

        glucose_values = data["glucose_values"]

        # ✅ Ensure Correct Input Length
        if not isinstance(glucose_values, list) or len(glucose_values) != 10:
            return jsonify({"error": "Input must be a list of exactly 10 glucose readings"}), 400

        # ✅ Convert Input to NumPy Array
        input_data = np.array(glucose_values, dtype=np.float32).reshape(1, -1)

        # ✅ Pad Input to Match Model's Feature Count
        padded_input = np.zeros((1, NUM_FEATURES))
        padded_input[0, :10] = input_data

        # ✅ Normalize Input
        normalized_input = scaler.transform(padded_input)

        # ✅ Reshape for LSTM Model (Batch, Time Steps, Features)
        reshaped_input = normalized_input.reshape(1, 10, NUM_FEATURES)

        # ✅ Make Prediction
        prediction = model.predict(reshaped_input)

        # ✅ Convert Prediction Back to Original Scale
        predicted_glucose = scaler.inverse_transform(prediction)[0][:10]

        # ✅ Convert `ndarray` to List (Fix JSON Serialization Issue)
        predicted_glucose = predicted_glucose.tolist()

        return jsonify({"predicted_glucose_levels": predicted_glucose})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Start Flask Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Use Render's PORT variable
    app.run(debug=True, host="0.0.0.0", port=port)
