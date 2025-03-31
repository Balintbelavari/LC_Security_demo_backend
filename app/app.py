import os
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizer, BertForSequenceClassification
from pymongo import MongoClient
from datetime import datetime
from google_drive_downloader import GoogleDriveDownloader as gdd

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

FILE_ID = "https://drive.google.com/file/d/1otmqu9wV5Mb8U-BTnMTKLa91hCQcotyR/view?usp=share_link"  # Google Drive file ID
DESTINATION_PATH = "app/bert_large_spam_model/model.safetensors"

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

# Google Drive model download function
def download_model_from_google_drive():
    try:
        print("Starting download of the model file from Google Drive...")
        gdd.download_file_from_google_drive(file_id=FILE_ID, dest_path=DESTINATION_PATH)
        print(f"Model file downloaded successfully to {DESTINATION_PATH}")
    except Exception as e:
        print(f"Error downloading the model: {e}")

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
