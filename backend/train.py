# backend/train.py

import os
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer
)

def main():
    
    # Defining the model, source language, and target language
    model_name = "ai4bharat/indictrans2-en-indic-1B"
    src_lang = "en"
    tgt_lang = "hi"
    
    # Define the paths for your training and validation data
    train_file = "corpus/train_combine.tsv"
    valid_file = "corpus/valid_combine.tsv"
    output_dir = "results/indictrans2-finetuned-en-hi"
    
    print("Loading and preparing data...")
    
    # Ensure the output directory exists
    if not os.path.exists("corpus"):
        os.makedirs("corpus")

    # Create dummy data files if they don't exist.
    if not os.path.exists(train_file):
        print("Creating dummy training data...")
        train_data = {
            'english_sentence': ["Hello, how are you?", "This is a test.", "I love to code."],
            'hindi_sentence': ["नमस्ते, आप कैसे हैं?", "यह एक परीक्षण है।", "मुझे कोड करना पसंद है।"]
        }
        pd.DataFrame(train_data).to_csv(train_file, sep="\t", index=False)

    if not os.path.exists(valid_file):
        print("Creating dummy validation data...")
        valid_data = {
            'english_sentence': ["Good morning.", "What is your name?"],
            'hindi_sentence': ["सुप्रभात।", "तुम्हारा नाम क्या है?"]
        }
        pd.DataFrame(valid_data).to_csv(valid_file, sep="\t", index=False)

    # Load the datasets
    train_dataset = Dataset.from_pandas(pd.read_csv(train_file, sep="\t"))
    valid_dataset = Dataset.from_pandas(pd.read_csv(valid_file, sep="\t"))

    # Load Tokenizer and Model
    print(f"Loading tokenizer and model for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)

    # Preprocess the Data
    def preprocess_function(examples):
        prefix = f"{src_lang}: "
        inputs = [prefix + ex for ex in examples["english_sentence"]]
        targets = [str(ex) for ex in examples["hindi_sentence"]]

        model_inputs = tokenizer(inputs, max_length=128, truncation=True)
        labels = tokenizer(text_target=targets, max_length=128, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    print("Preprocessing datasets...")
    tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True)
    tokenized_valid_dataset = valid_dataset.map(preprocess_function, batched=True)

    # Set Up the Trainer
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=3,
        predict_with_generate=True,
        fp16=True,  # Use mixed-precision training if a GPU is available
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_valid_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    # Start Fine-Tuning
    print("Starting fine-tuning...")
    trainer.train()

    # Save the Model
    print(f"Fine-tuning complete. Saving model to {output_dir}")
    trainer.save_model(output_dir)

if __name__ == "__main__":
    main()