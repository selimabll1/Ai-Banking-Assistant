import pandas as pd
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset

# 1. Charger les données
df = pd.read_csv("chatbot/chatbot.csv")  # Adjust path if necessary
label_encoder = LabelEncoder()
df["label_id"] = label_encoder.fit_transform(df["Label"])

# 2. Tokenization: Preparing the tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def tokenize(batch):
    # Tokenizing the 'Text' column and applying padding, truncation, and max_length
    return tokenizer(batch["Text"], padding="max_length", truncation=True, max_length=64)

# Convert the DataFrame to a Hugging Face Dataset object
dataset = Dataset.from_pandas(df)

# Map the tokenizer function to the dataset
dataset = dataset.map(tokenize, batched=True)

# Rename the 'label_id' column to 'labels' as expected by HuggingFace
dataset = dataset.rename_column("label_id", "labels")

# Set the format for PyTorch
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# 3. Model Initialization: Load DistilBERT model
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=len(label_encoder.classes_))

# 4. Training Configuration: Set up the training arguments
training_args = TrainingArguments(
    output_dir="chatbot/model",  # Where to save the model
    per_device_train_batch_size=8,  # Batch size per device (GPU)
    num_train_epochs=3,  # Number of training epochs
    logging_dir="./logs",  # Directory for logs
    logging_steps=10,  # How often to log the progress
    save_strategy="no",  # Don't save checkpoints every epoch
)

# 5. Trainer Setup: Configure the Trainer object
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,  # Pass the dataset for training
)

# 6. Train the model
trainer.train()

# Save the model and tokenizer
model.save_pretrained("chatbot/model")
tokenizer.save_pretrained("chatbot/model")
