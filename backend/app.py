# Import Libraries
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from translator import UniversalTranslator

# Flask API Setup
app = Flask(__name__)
CORS(app)

# Global Variables
translator_cache = {}
LANGUAGES = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada'}
MODEL_PATHS = {
    'en_hi': 'results/marian_en_hi_finetuned',
    'hi_en': 'results/marian_hi_en_finetuned',
    'en_kn': 'results/marian_en_kn_finetuned',
    'kn_en': 'results/marian_kn_en_finetuned'
}

# Function to get model path
def get_model_path(src_lang, tgt_lang):
    language_pair = f"{src_lang}_{tgt_lang}"
    
    if language_pair in MODEL_PATHS and os.path.exists(MODEL_PATHS[language_pair]):
        return MODEL_PATHS[language_pair]
    
    for path in MODEL_PATHS.values():
        if os.path.exists(path):
            return path
        
    return None

# Function to get translator
def get_translator(src_lang, tgt_lang):
    cache_key = f"{src_lang}_{tgt_lang}"
    
    if cache_key in translator_cache:
        return translator_cache[cache_key]
    
    model_path = get_model_path(src_lang, tgt_lang)
    
    if not model_path:
        raise Exception(f"No model available for {src_lang} -> {tgt_lang} translation")
    
    try:
        translator = UniversalTranslator(model_path)
        translator_cache[cache_key] = translator
        return translator
    except Exception as e:
        raise Exception(f"Failed to load translator: {str(e)}")

# API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    model_status = {}
    # Check model paths
    for pair, path in MODEL_PATHS.items():
        model_status[pair] = {
            'path': path,
            'exists': os.path.exists(path),
            'cached': pair in translator_cache
        }
    # Check translator cache
    return jsonify({
        'status': 'healthy',
        'supported_languages': LANGUAGES,
        'model_status': model_status,
        'cached_translators': list(translator_cache.keys()),
        'device': 'cuda' if torch.cuda.is_available() else 'cpu'
    })

@app.route('/api/translate', methods=['POST'])
def translate_text():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided.'}), 400
            
        text = data.get('text', '').strip()
        src_lang = data.get('src_lang', 'en')
        tgt_lang = data.get('tgt_lang', 'hi')

        if not text:
            return jsonify({'error': 'No text provided for translation.'}), 400
        if src_lang not in LANGUAGES or tgt_lang not in LANGUAGES:
            return jsonify({'error': 'Unsupported language selected.'}), 400
        if src_lang == tgt_lang:
            return jsonify({'error': 'Source and target languages are the same.'}), 400

        start_time = time.time()
        
        try:
            translator = get_translator(src_lang, tgt_lang)
            translation = translator.translate(text, src_lang, tgt_lang)
        except Exception as e:
            return jsonify({'error': f'Translation failed: {str(e)}'}), 503
        
        end_time = time.time()

        return jsonify({
            'source_text': text,
            'source_language': src_lang,
            'source_language_name': LANGUAGES[src_lang],
            'target_language': tgt_lang,
            'target_language_name': LANGUAGES[tgt_lang],
            'translation': translation,
            'model_used': get_model_path(src_lang, tgt_lang),
            'processing_time': round(end_time - start_time, 3)
        })

    except Exception as e:
        return jsonify({'error': 'An internal server error occurred.'}), 500

def initialize_translators():
    print("Initializing translators...")
    
    common_pairs = [('en', 'hi'), ('hi', 'en'), ('en', 'kn'), ('kn', 'en')]
    
    for src_lang, tgt_lang in common_pairs:
        try:
            get_translator(src_lang, tgt_lang)
            print(f"✓ Initialized {src_lang} -> {tgt_lang} translator")
        except Exception as e:
            print(f"✗ Failed to initialize {src_lang} -> {tgt_lang}: {e}")

def start_api_server():
    initialize_translators()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5005, threaded=True)


# Execute training and start API
if __name__ == "__main__":
    start_api_server()
    
    