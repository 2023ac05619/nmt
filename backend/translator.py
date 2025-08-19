import torch
import pandas as pd
from datasets import load_dataset, Dataset
from transformers import (
    MarianMTModel,
    MarianTokenizer,
    T5ForConditionalGeneration,
    T5Tokenizer,
)
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
import os
import warnings
import json
warnings.filterwarnings("ignore")


class UniversalTranslator:
    # Initialize the translator
    def __init__(self, model_path):
        self.model_path = model_path
        self.model_type = self._detect_model_type()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    # Detect the model type
    def _detect_model_type(self):
        config_path = os.path.join(self.model_path, "config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    architecture = config.get("architectures", [""])[0].lower()
                    if "marian" in architecture:
                        return "marian"
                    elif "t5" in architecture:
                        return "t5"
            except:
                pass # Ignore errors
            
        # If config file doesn't exist, check model name
        if "marian" in self.model_path.lower():
            return "marian"
        elif "t5" in self.model_path.lower():
            return "t5"
        # Default to T5
        return "t5"
    
    # Load the model
    def _load_model(self):
        if self.model_type == "marian":
            self.tokenizer = MarianTokenizer.from_pretrained(self.model_path)
            self.model = MarianMTModel.from_pretrained(self.model_path)
        else:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
            self.model_type = "t5"
        
        self.model.to(self.device)
        self.model.eval()
    
    # Translate text
    def translate(self, text, src_lang='en', tgt_lang='hi'):
        if self.model_type == "marian":
            input_text = text
        else:
            lang_map = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada'}
            input_text = f"translate {lang_map[src_lang]} to {lang_map[tgt_lang]}: {text}"
        
        # Tokenize and generate
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=128,
                num_beams=4,
                length_penalty=0.6,
                early_stopping=True,
                do_sample=False,
            )
        
        # Decode and return
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation.strip()