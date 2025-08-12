# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from translator import NMTTranslator
from config import LANGUAGES

# Initialize Flask app
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS)
CORS(app) 

# Initialize translator class
print("Initializing the translator...")
translator = NMTTranslator()
print("Translator initialized successfully.")

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """
    API endpoint to handle translation requests.
    Expects a JSON payload with 'text', 'src_lang', and 'tgt_lang'.
    """
    try:
        data = request.json
        text = data.get('text', '').strip()
        src_lang = data.get('src_lang', 'en')
        tgt_lang = data.get('tgt_lang', 'hi')

        # --- Input Validation ---
        if not text:
            return jsonify({'error': 'No text provided for translation.'}), 400
        if src_lang not in LANGUAGES or tgt_lang not in LANGUAGES:
            return jsonify({'error': 'Unsupported language selected.'}), 400
        if src_lang == tgt_lang:
            return jsonify({'error': 'Source and target languages are the same.'}), 400

        # --- Perform Translation ---
        start_time = time.time()
        result = translator.translate(text, src_lang, tgt_lang)
        end_time = time.time()

        if "error" in result:
            return jsonify(result), 500

        # --- Return Successful Response ---
        return jsonify({
            'translation': result.get('translation'),
            'processing_time': round(end_time - start_time, 2)
        })

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True, port=5000)
