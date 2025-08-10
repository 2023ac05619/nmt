# backend/translator.py

import torch
import re
from transformers import pipeline
from .config import MODEL_CONFIGS, TRANSLITERATIONS

class NMTTranslator:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.models = {}

    def load_model(self, lang_pair):
        if lang_pair not in self.models:
            if lang_pair not in MODEL_CONFIGS:
                raise ValueError(f"Translation pair {lang_pair} not supported")

            model_name = MODEL_CONFIGS[lang_pair]
            print(f"Loading model for {lang_pair}...")
            try:
                self.models[lang_pair] = pipeline(
                    'translation',
                    model=model_name,
                    tokenizer=model_name,
                    device=self.device
                )
                print(f"Loaded model for {lang_pair}")
            except Exception as e:
                print(f"Failed to load {lang_pair}: {e}")
                raise

    def _preprocess_text(self, text, src_lang):
        text = text.strip()
        if src_lang == 'en':
            for eng, native in TRANSLITERATIONS.items():
                text = re.sub(rf'\b{eng}\b', native, text, flags=re.IGNORECASE)
        return text

    def translate(self, text, src_lang, tgt_lang):
        if not text.strip():
            return {"error": "Empty text provided"}

        if src_lang == tgt_lang:
            return {"translation": text}

        lang_pair = f"{src_lang}-{tgt_lang}"

        try:
            self.load_model(lang_pair)
            preprocessed_text = self._preprocess_text(text, src_lang)
            result = self.models[lang_pair](preprocessed_text)
            return {"translation": result[0]['translation_text']}
        except Exception as e:
            return {"error": str(e)}