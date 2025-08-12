# Configuration variables for the NMT application.
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
}

# Translation model from Hugging Face.
MODEL_CONFIGS = {
    'model_name': 'facebook/mbart-large-50-many-to-many-MMT',
    
    # Language codes for mBART model.
    'lang_codes': {
        'en': 'en_XX',
        'hi': 'hi_IN',
        'ta': 'ta_IN',
        'te': 'te_IN',
        'bn': 'bn_IN',
        'mr': 'mr_IN',
        'gu': 'gu_IN',
        'kn': 'kn_IN', 
        'ml': 'ml_IN',
        'pa': 'pa_IN',
    }
}
