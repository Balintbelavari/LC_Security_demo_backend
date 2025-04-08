from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.responses import FileResponse  # type: ignore
from pathlib import Path  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel  # type: ignore
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
import joblib  # type: ignore
from datetime import datetime
from dotenv import load_dotenv  # type: ignore
import os
import pymongo # type: ignore
import gspread # type: ignore
from google.oauth2 import service_account # type: ignore
import base64
import json
from cryptography.fernet import Fernet  # type: ignore
import torch # type: ignore
from transformers import AutoTokenizer,BertTokenizer, BertForSequenceClassification, AutoModelForSequenceClassification # type: ignore

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

secret_key = os.getenv("SECRET_KEY").encode() # Secret key for Fernet
encrypted_mongo_uri = os.getenv("MONGO_URI_ENCRYPTED").encode()  # Encrypted Mongo URI
fernet = Fernet(secret_key)
mongo_uri = fernet.decrypt(encrypted_mongo_uri).decode()
client = AsyncIOMotorClient(mongo_uri)

google_credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64") # Base64 encoded Google credentials
google_credentials_json = base64.b64decode(google_credentials_base64).decode("utf-8") # Decode base64 into utf-8 string
credentials_info = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(
    credentials_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)
db = client["model_v0_1_1"]
collection = db["predictions"]

# Google Sheets API setup
client_gs = gspread.authorize(credentials)
sheet = client_gs.open("mongodb_export").sheet1

# Load model and vectorizer
model_traditional = joblib.load(os.path.join(BASE_DIR, "model1.pkl"))
vectorizer_traditional = joblib.load(os.path.join(BASE_DIR, "vectorizer1.pkl"))

# Load BERT-based model
# model_path = os.path.join(BASE_DIR, "quantized_bert_spam")
# tokenizer = BertTokenizer.from_pretrained(model_path)
# model_bert = BertForSequenceClassification.from_pretrained(model_path)

model_name = "Anurag3703/bert-spam-classifier"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model_bert = AutoModelForSequenceClassification.from_pretrained(model_name)

model_bert.eval()

# FastAPI app
app = FastAPI()

# ✅ Enable CORS for React frontend (localhost:3000 for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://lc-security-backend-d51e9de3f86b.herokuapp.com/", "http://127.0.0.1:8001s"],  # React dev server, heroku hosting, local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve React frontend
frontend_build_path = Path(os.getenv("FRONTEND_BUILD_PATH"))

@app.get("/")
async def serve_frontend():
    """Serves the React app's index.html file."""
    index_path = frontend_build_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "Frontend build not found. Run npm run build in the frontend folder."}

# ✅ Predict Endpoint
class Message(BaseModel):
    message: str
    use_bert: bool

@app.post("/predict")
async def predict(message: Message):
    try:
        if message.use_bert:
            # Use BERT-based model for prediction
            inputs = tokenizer(
                message.message,
                return_tensors="pt",
                truncation=True,
                max_length=512,
            )
            with torch.no_grad():
                output = model_bert(**inputs)
            prediction_num = torch.argmax(output.logits).item()
            prediction_text = "Spam" if prediction_num == 1 else "Ham"
        else:
            # Use traditional model for prediction
            message_bow = vectorizer_traditional.transform([message.message])
            prediction_text = model_traditional.predict(message_bow)[0]

        # Store prediction in MongoDB
        result = {
            "message": message.message,
            "prediction": prediction_text,
            "timestamp": datetime.now().isoformat()
        }
        await db.predictions.insert_one(result)

        # Update Google Sheet
        new_row = [message.message, prediction_text]
        sheet.append_row(new_row)

        return {"prediction": prediction_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="root_files")
    app.mount("/static", StaticFiles(directory=frontend_build_path / "static"), name="static")


# ✅ Properly Close MongoDB on Shutdown
@app.on_event("shutdown")
async def shutdown():
    await client.close()

# ✅ Run FastAPI (for local development)
if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
print("main.py ran successfully")