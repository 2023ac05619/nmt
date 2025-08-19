import React, { useState, useEffect } from 'react';
import { ArrowRightLeft, Languages, Clock, Copy } from 'lucide-react';
import { translateText as apiTranslateText } from './api';
import { transliterationMap } from './transliterationMap';

// const mockTransliterationMap = {
//   'hello': 'हैलो', 'namaste': 'नमस्ते', 'dhanyawad': 'धन्यवाद',
//   'kaise': 'कैसे', 'hai': 'है', 'main': 'मैं', 'aap': 'आप'
// };

const transliterateText = (text) => {
  let result = text.toLowerCase();
  Object.keys(transliterationMap).forEach(key => {
    const regex = new RegExp(`\\b${key}\\b`, 'g');
    result = result.replace(regex, transliterationMap[key]);
  });
  return result;
};

function App() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [srcLang, setSrcLang] = useState('en');
  const [tgtLang, setTgtLang] = useState('hi');
  // const [selectedModel, setSelectedModel] = useState('neural-transformer-v2');
  // const [availableModels] = useState(['neural-transformer-v2', 'bert-multilingual', 'mbart-large']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processingTime, setProcessingTime] = useState(null);
  const [showTransliteration, setShowTransliteration] = useState(false);
  const [transliteratedText, setTransliteratedText] = useState('');

  const languages = {
    'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada',
  };

  // ✅ THIS IS THE NEW HANDLER FUNCTION
  const handleInputChange = (e) => {
    setInputText(e.target.value);
    if (error) {
      setError('');
    }
  };

  useEffect(() => {
    if (srcLang === 'en' && tgtLang === 'hi' && inputText.trim()) {
      const transliterated = transliterateText(inputText.trim());
      setTransliteratedText(transliterated);
      setShowTransliteration(transliterated !== inputText.toLowerCase() && transliterated.trim() !== '');
    } else {
      setShowTransliteration(false);
    }
  }, [inputText, srcLang, tgtLang]);

  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError('Please enter text to translate.');
      return;
    }
    if (srcLang === tgtLang) {
      setError('Source and target languages cannot be the same.');
      return;
    }

    setLoading(true);
    setError('');
    setOutputText('');
    setProcessingTime(null);
    // const startTime = performance.now();

    try {
      const payload = { text: inputText, src_lang: srcLang, tgt_lang: tgtLang };
      const response = await apiTranslateText(payload);
      // setOutputText(response.data.translated_text);      
      setOutputText(response.data.translation);
      // const endTime = performance.now();
      // setProcessingTime(((endTime - startTime) / 1000).toFixed(2));
      setProcessingTime(response.data.processing_time.toFixed(2));
    } catch (err) {
      console.error("Translation API error:", err);
      setError('Translation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSwapLanguages = () => {
    setSrcLang(tgtLang);
    setTgtLang(srcLang);
    setInputText(outputText);
    setOutputText(inputText);
    setError('');
  };

  const useTransliteration = () => {
    setInputText(transliteratedText);
    setShowTransliteration(false);
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(outputText);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 font-sans">
      <header className="bg-white/70 backdrop-blur-md border-b border-gray-200/50 shadow-sm sticky top-0 z-10">
        {/* Header JSX... */}
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg shadow-md">
              <Languages className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                Fine-Tuned Models by Group #8
              </h1>
              <p className="text-sm text-gray-500"> (trained on 'hi' and 'kn' datasets from ai4bharat/samanantar) </p>
            </div>
          </div>
          {/* <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-500" />
            <span className="text-sm text-gray-600 font-medium">Model:</span>
            <select
              className="bg-gray-50/80 border border-gray-200 rounded-lg px-3 py-1 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {availableModels.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div> */}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-white/50 overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-[2fr_auto_2fr]">
            {/* Input Panel */}
            <div className="p-6">
              <div className="space-y-4">
                <select
                  className="w-full bg-gray-50/50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
                  value={srcLang}
                  onChange={(e) => setSrcLang(e.target.value)}
                >
                  {Object.entries(languages).map(([code, name]) => (
                    <option key={code} value={code}>{name}</option>
                  ))}
                </select>
                <div className="relative">
                  <textarea
                    className="w-full h-48 bg-gray-50/30 border border-gray-200 rounded-xl px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition placeholder-gray-400"
                    placeholder="Enter text to translate..."
                    value={inputText}
                    onChange={handleInputChange} // ✅ USE THE NEW HANDLER HERE
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-gray-400">{inputText.length} chars</div>
                </div>
                {showTransliteration && (
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-xs text-amber-800 font-medium mb-1">Did you mean:</p>
                        <p className="text-md text-amber-900 font-semibold">{transliteratedText}</p>
                      </div>
                      <button
                        onClick={useTransliteration}
                        className="ml-3 px-3 py-1.5 bg-amber-400 text-white rounded-lg hover:bg-amber-500 transition text-sm font-medium shadow-sm"
                      >
                        Use
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Swap Button */}
            <div className="flex items-center justify-center p-4 border-t border-b lg:border-t-0 lg:border-b-0 lg:border-l lg:border-r border-gray-100">
              <button
                onClick={handleSwapLanguages}
                className="p-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full hover:from-blue-600 hover:to-indigo-700 transition duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                title="Swap languages"
              >
                <ArrowRightLeft className="w-5 h-5" />
              </button>
            </div>

            {/* Output Panel */}
            <div className="p-6">
              <div className="space-y-4">
                <select
                  className="w-full bg-gray-50/50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
                  value={tgtLang}
                  onChange={(e) => setTgtLang(e.target.value)}
                >
                  {Object.entries(languages).map(([code, name]) => (
                    <option key={code} value={code}>{name}</option>
                  ))}
                </select>
                <div className="relative">
                  <div className="w-full h-48 bg-gray-50/30 border border-gray-200 rounded-xl px-4 py-3 overflow-y-auto">
                    {loading ? (
                      <div className="flex items-center justify-center h-full">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                        {outputText || <span className="text-gray-400">Translation will appear here...</span>}
                      </p>
                    )}
                  </div>
                  {outputText && !loading && (
                    <button onClick={handleCopyToClipboard} className="absolute top-3 right-3 p-1.5 text-gray-400 hover:text-blue-600 rounded-full hover:bg-gray-100 transition" title="Copy to clipboard">
                      <Copy className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Controls and Stats */}
          <div className="border-t border-gray-100 px-6 py-4 bg-gray-50/30 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {processingTime && (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>{processingTime}s</span>
                </div>
              )}
              {error && (
                <div className="text-sm text-red-600 bg-red-100 px-3 py-1 rounded-full">{error}</div>
              )}
            </div>
            <button
              onClick={handleTranslate}
              disabled={loading || !inputText.trim()}
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-800 transition duration-200 shadow-md hover:shadow-lg transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-md"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Translating...</span>
                </div>
              ) : 'Translate'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
