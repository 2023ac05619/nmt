import React, { useState } from 'react';
import { translateText } from './api'; 
import './index.css';

function App() {
  // State variables
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [srcLang, setSrcLang] = useState('en');
  const [tgtLang, setTgtLang] = useState('hi');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processingTime, setProcessingTime] = useState(null);

  // static language codes
  const languages = {
    'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu',
    'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada',
    'ml': 'Malayalam', 'pa': 'Punjabi',
  };

  const handleTranslate = async () => {
    // Input validation
    if (!inputText.trim()) {
      setError('Please enter text to translate.');
      return;
    }
    if (srcLang === tgtLang) {
      setError('Source and target languages cannot be the same.');
      return;
    }

    // Reset state for new translation
    setLoading(true);
    setError('');
    setOutputText('');
    setProcessingTime(null);

    try {
      const payload = { text: inputText, src_lang: srcLang, tgt_lang: tgtLang };
      const response = await translateText(payload);
      setOutputText(response.data.translation);
      setProcessingTime(response.data.processing_time);
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to connect to backend. Please ensure it is running.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSwapLanguages = () => {
    // Swap source and target languages
    setSrcLang(tgtLang);
    setTgtLang(srcLang);
    setInputText(outputText);
    setOutputText(inputText);
    setError('');
  };

  return (
    <div className="App">
      <header className="header">
        <h1>Neural Machine Translation</h1>
        <p>Translate between English and popular Indian languages in real-time.</p>
      </header>

      <div className="translation-grid">
        {/* Input Panel */}
        <div className="translation-panel">
          <select
            className="language-selector"
            value={srcLang}
            onChange={(e) => setSrcLang(e.target.value)}
          >
            {Object.entries(languages).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
          <textarea
            className="text-area"
            placeholder="Enter text to translate..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
        </div>

        {/* Swap Button */}
        <div className="swap-button-container">
          <button className="swap-button" onClick={handleSwapLanguages} title="Swap languages">
            <svg className="swap-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </button>
        </div>

        {/* Output Panel */}
        <div className="translation-panel">
          <select
            className="language-selector"
            value={tgtLang}
            onChange={(e) => setTgtLang(e.target.value)}
          >
            {Object.entries(languages).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
          <div className="output-panel">
            {loading ? (
                <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%'}}>
                    <div className="loader" />
                </div>
            ) : (
                outputText || 'Translation will appear here...'
            )}
          </div>
        </div>
      </div>
      
      {processingTime !== null && !loading && !error && (
        <div className="stats">
          Processing time: {processingTime}s
        </div>
      )}

      <div className="controls">
        <button className="translate-btn" onClick={handleTranslate} disabled={loading || !inputText.trim()}>
          {loading ? <div className="loader" /> : 'Translate'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default App;
