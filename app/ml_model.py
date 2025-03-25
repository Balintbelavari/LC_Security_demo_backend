import joblib
from pathlib import Path

# Define paths to model files
MODEL_PATH = Path(__file__).parent.parent / "model.pkl"
VECTORIZER_PATH = Path(__file__).parent.parent / "vectorizer.pkl"

# Load the model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def predict_message(message: str) -> str:
    """Predict the label of the input message using the trained model."""
    message_bow = vectorizer.transform([message])
    prediction = model.predict(message_bow)[0]
    return prediction
