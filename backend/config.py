# Config for different language pairs

MODEL_CONFIGS = {
    # English to Indian languages
    'en-hi': 'ai4bharat/indictrans2-en-indic-1B',
    'en-ta': 'ai4bharat/indictrans2-en-indic-1B',
    'en-te': 'ai4bharat/indictrans2-en-indic-1B',
    'en-bn': 'ai4bharat/indictrans2-en-indic-1B',
    'en-mr': 'ai4bharat/indictrans2-en-indic-1B',

    # Indian languages to English
    'hi-en': 'ai4bharat/indictrans2-indic-en-1B',
    'ta-en': 'ai4bharat/indictrans2-indic-en-1B',
    'te-en': 'ai4bharat/indictrans2-indic-en-1B',
    'bn-en': 'ai4bharat/indictrans2-indic-en-1B',
    'mr-en': 'ai4bharat/indictrans2-indic-en-1B',

    # Indian language to Indian language
    'hi-ta': 'ai4bharat/indictrans2-indic-indic-1B',
    'hi-te': 'ai4bharat/indictrans2-indic-indic-1B',
    'hi-mr': 'ai4bharat/indictrans2-indic-indic-1B',
    'ta-hi': 'ai4bharat/indictrans2-indic-indic-1B',
    'te-hi': 'ai4bharat/indictrans2-indic-indic-1B',
    'mr-hi': 'ai4bharat/indictrans2-indic-indic-1B'
}

# Supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'mr': 'Marathi'
}

# Transliteration dictionary
TRANSLITERATIONS = {
    'namaste': 'नमस्ते',
    'dhanyawad': 'धन्यवाद',
    'kaise ho': 'कैसे हो',
    'vanakkam': 'வணக்கம்',
    'shukriya': 'شکریہ',
    'adaab': 'آداب',
    'namaskar': 'नमस्कार',
    'swagat': 'स्वागत है'
}