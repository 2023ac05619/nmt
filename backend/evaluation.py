import pandas as pd
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from translator import NMTTranslator

def download_nltk_data():
    """Downloads the necessary NLTK data."""
    try:
        nltk.data.find('tokenizers/punkt')
    except nltk.downloader.DownloadError:
        print("Downloading NLTK 'punkt' data...")
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/wordnet')
    except nltk.downloader.DownloadError:
        print("Downloading NLTK 'wordnet' data...")
        nltk.download('wordnet')

class TranslationEvaluator:
    def __init__(self):
        self.smoothing = SmoothingFunction().method1

    def calculate_bleu(self, reference, candidate):
        ref_tokens = nltk.word_tokenize(reference.lower())
        cand_tokens = nltk.word_tokenize(candidate.lower())
        score = sentence_bleu([ref_tokens], cand_tokens, smoothing_function=self.smoothing)
        return round(score * 100, 2)

    def calculate_meteor(self, reference, candidate):
        score = meteor_score([reference], candidate)
        return round(score * 100, 2)

def run_evaluation(translator, test_cases):
    evaluator = TranslationEvaluator()
    results = []
    print("Running translation evaluation...")
    for i, case in enumerate(test_cases):
        print(f"  - Evaluating case {i+1}/{len(test_cases)}...")
        result = translator.translate(case['source'], case['src_lang'], case['tgt_lang'])
        if 'error' in result:
            print(f"    Error translating '{case['source']}': {result['error']}")
            continue
        pred_text = result.get('translation', '')
        bleu = evaluator.calculate_bleu(case['reference'], pred_text)
        meteor = evaluator.calculate_meteor(case['reference'], pred_text)
        results.append({
            'Source': case['source'],
            'Reference': case['reference'],
            'Prediction': pred_text,
            'BLEU': bleu,
            'METEOR': meteor
        })
    print("Evaluation complete.")
    return pd.DataFrame(results)

def main():
    download_nltk_data()
    nmt = NMTTranslator()
    evaluation_pairs = [
        {'source': 'Hello, how are you?', 'reference': 'नमस्ते, आप कैसे हैं?', 'src_lang': 'en', 'tgt_lang': 'hi'},
        {'source': 'Good morning', 'reference': 'सुप्रभात', 'src_lang': 'en', 'tgt_lang': 'hi'},
        {'source': 'Where are you from?', 'reference': 'तुम्ही कुठून आहात?', 'src_lang': 'en', 'tgt_lang': 'mr'},
        {'source': 'This is a beautiful place', 'reference': 'हे एक सुंदर ठिकाण आहे', 'src_lang': 'en', 'tgt_lang': 'mr'},
        {'source': 'नमस्ते', 'reference': 'Hello', 'src_lang': 'hi', 'tgt_lang': 'en'},
        {'source': 'मी ठीक आहे', 'reference': 'I am fine', 'src_lang': 'mr', 'tgt_lang': 'en'}
    ]
    evaluation_df = run_evaluation(nmt, evaluation_pairs)
    print("\n--- Evaluation Results ---")
    print(evaluation_df.to_string())
    print("------------------------\n")

if __name__ == '__main__':
    main()
