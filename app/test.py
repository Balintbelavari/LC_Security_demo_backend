import torch
import transformers
from transformers import BertTokenizer, BertForSequenceClassification
import accelerator
print("torch version:", torch.__version__)
print("transformers version:", transformers.__version__)
print("accelerator version:", accelerator.__version__)

model_path = "/Users/balintbelavari/Suli/szakdoga/lc_security/demo_webapp/backend/app/quantized_bert_spam"

# Test loading tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

print("Tokenizer and model loaded successfully.")