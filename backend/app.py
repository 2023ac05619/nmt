# backend/app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
from .translator import NMTTranslator
from .config import LANGUAGES, MODEL_CONFIGS
import os

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')),
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')))
CORS(app)

translator = NMTTranslator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text', '').strip()
    src_lang = data.get('src_lang', 'en')
    tgt_lang = data.get('tgt_lang', 'hi')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    start_time = time.time()
    result = translator.translate(text, src_lang, tgt_lang)
    end_time = time.time()

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        'translation': result['translation'],
        'processing_time': round(end_time - start_time, 2),
        'src_lang': src_lang,
        'tgt_lang': tgt_lang
    })

@app.route('/supported_languages')
def supported_languages():
    return jsonify({
        'languages': LANGUAGES,
        'supported_pairs': list(MODEL_CONFIGS.keys())
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)