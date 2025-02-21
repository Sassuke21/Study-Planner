from transformers import BertTokenizer, BertForMaskedLM
import torch

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')

# Function to use BERT for understanding user input and extracting key concepts
def get_bert_concept(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt")
    
    # Forward pass through the model
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract token IDs from the output and decode to words
    predictions = torch.argmax(outputs.logits, dim=-1)
    predicted_tokens = tokenizer.convert_ids_to_tokens(predictions[0])
    
    # Return the first token as the key concept (simplified)
    return predicted_tokens[0]
