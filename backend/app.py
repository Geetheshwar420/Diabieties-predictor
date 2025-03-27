from flask import Flask, render_template, request, jsonify
import os
import numpy as np
import tensorflow as tf
import pickle
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS

# ✅ Initialize Flask
app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
CORS(app)  # ✅ Allow frontend to call API

# ✅ Paths to Model & Scaler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "glucose_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

# ✅ Ensure model file exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found: {MODEL_PATH}")

# ✅ Load Model & Scaler
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
model.compile(optimizer="adam", loss="mean_squared_error")

with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

# ✅ Expected Feature Count
NUM_FEATURES = 72

# ✅ Route to Serve HTML Page
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Prediction API
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json.get("glucose_values")
        if not data or len(data) != 10:
            return jsonify({"error": "Enter exactly 10 glucose readings"}), 400

        # ✅ Convert Input to NumPy Array
        input_data = np.array(data, dtype=np.float32).reshape(1, 10)

        # ✅ Pad Input with Zeros to Match 72 Features
        padded_input = np.zeros((10, NUM_FEATURES))
        padded_input[:, :10] = input_data

        # ✅ Normalize Input
        normalized_input = scaler.transform(padded_input)

        # ✅ Reshape for LSTM Model
        reshaped_input = normalized_input.reshape(1, 10, NUM_FEATURES)

        # ✅ Make Prediction
        prediction = model.predict(reshaped_input)

        # ✅ Convert Prediction Back to Original Scale
        predicted_glucose = scaler.inverse_transform(prediction)[0][:10]

        # ✅ Fix: Convert `ndarray` to `list` (Avoid JSON Serialization Error)
        predicted_glucose = predicted_glucose.tolist()

        return jsonify({"predicted_glucose_levels": predicted_glucose})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Start Flask Server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
