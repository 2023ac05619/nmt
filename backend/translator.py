from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from config import MODEL_CONFIGS

class NMTTranslator:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        try:
            print(f"Loading model: {MODEL_CONFIGS['model_name']}...")
            self.model = MBartForConditionalGeneration.from_pretrained(MODEL_CONFIGS['model_name'])
            self.tokenizer = MBart50TokenizerFast.from_pretrained(MODEL_CONFIGS['model_name'])
            print("Model and tokenizer loaded successfully.")
        except Exception as e:
            print(f"CRITICAL: Failed to load model or tokenizer. Error: {e}")
            
    def translate(self, text: str, src_lang: str, tgt_lang: str):
        if not self.model or not self.tokenizer:
            return {"error": "Translator model is not available. Check server logs for details."}
            
        try:
            src_code = MODEL_CONFIGS['lang_codes'].get(src_lang)
            tgt_code = MODEL_CONFIGS['lang_codes'].get(tgt_lang)

            if not src_code or not tgt_code:
                return {"error": f"Invalid language configuration for {src_lang} or {tgt_lang}."}

            if tgt_code not in self.tokenizer.lang_code_to_id:
                 return {"error": f"The model does not support the target language code: {tgt_code}"}

            # Setting the source language
            self.tokenizer.src_lang = src_code
            
            # Encode the input text
            encoded_text = self.tokenizer(text, return_tensors="pt")
            
            # Generate the translation
            generated_tokens = self.model.generate(
                **encoded_text,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code]
            )
            
            # Decode the generated tokens
            translated_text = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
            
            return {"translation": translated_text}
            
        except Exception as e:
            error_message = f"An error occurred during translation: {str(e)}"
            print(error_message)
            return {"error": "An internal error occurred during translation."}
