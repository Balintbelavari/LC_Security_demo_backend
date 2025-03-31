import os
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizer, BertForSequenceClassification
from pymongo import MongoClient
from datetime import datetime

# GitHub model download function
def download_file_from_github(github_url, save_path):
    response = requests.get(github_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File successfully downloaded to {save_path}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        
github_url = "https://github.com/Balintbelavari/LC_Security_demo_backend/blob/facd8c9a26384ef2edae63d1bf7d19be4466e2e2/app/bert_large_spam_model/model.safetensors"
save_path = "bert_large_spam_model/model.safetensors"

download_file_from_github(github_url, save_path)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load environment variables (if using .env file)
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["bert_large_spam_model"]  # Replace with your actual database name
collection = db["predictions"]  # Collection to store results

# Load the model & tokenizer
model = BertForSequenceClassification.from_pretrained("bert_large_spam_model")
tokenizer = BertTokenizer.from_pretrained("bert_large_spam_model")

# Prediction function
def predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return "Spam" if prediction == 1 else "Ham"

# Flask route to handle model download on startup
@app.before_first_request
def before_first_request():
    download_model_from_google_drive()

# API root
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Spam/Ham Prediction API!"})

# Predict endpoint
@app.route("/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Make prediction
    result = predict(text)

    # Store result in MongoDB
    prediction_data = {
        "message": text,
        "prediction": result,
        "timestamp": datetime.now().isoformat()
    }
    collection.insert_one(prediction_data)

    return jsonify({"prediction": result})

# Run app (for local testing)
if __name__ == "__main__":
    is_heroku = os.environ.get("DYNO") is not None  # Check if running on Heroku
    port = int(os.environ.get("PORT", 8000 if not is_heroku else 8080))  # Default 8000 locally, 8080 on Heroku
    app.run(host="0.0.0.0", port=port)
