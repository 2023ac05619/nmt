// frontend/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://localhost:5000';
    const inputText = document.getElementById('inputText');
    const srcLang = document.getElementById('srcLang');
    const tgtLang = document.getElementById('tgtLang');
    const outputDiv = document.getElementById('outputText');
    const loadingDiv = document.getElementById('loading');
    const timeSpan = document.getElementById('processingTime');
    const charCount = document.getElementById('charCount');
    const translateBtn = document.getElementById('translateBtn');

    function updateCharCount() {
        charCount.textContent = `Characters: ${inputText.value.length}`;
    }

    async function translateText() {
        const textToTranslate = inputText.value.trim();

        if (!textToTranslate) {
            outputDiv.innerHTML = '<div class="error">Please enter some text to translate.</div>';
            return;
        }

        if (srcLang.value === tgtLang.value) {
            outputDiv.innerHTML = '<div class="error">Source and target languages cannot be the same.</div>';
            return;
        }

        translateBtn.disabled = true;
        loadingDiv.style.display = 'block';
        outputDiv.textContent = 'Translating...';
        timeSpan.textContent = '';

        try {
            const response = await fetch(`${API_BASE}/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: textToTranslate,
                    src_lang: srcLang.value,
                    tgt_lang: tgtLang.value
                })
            });

            const data = await response.json();

            if (response.ok) {
                outputDiv.textContent = data.translation;
                timeSpan.textContent = `Processing time: ${data.processing_time}s`;
            } else {
                outputDiv.innerHTML = `<div class="error">${data.error}</div>`;
            }
        } catch (error) {
            outputDiv.innerHTML = `<div class="error">Connection error: ${error.message}</div>`;
        } finally {
            translateBtn.disabled = false;
            loadingDiv.style.display = 'none';
        }
    }

    function setTestCase(text, src, tgt) {
        inputText.value = text;
        srcLang.value = src;
        tgtLang.value = tgt;
        updateCharCount();
        if (text.trim()) {
            translateText();
        }
    }

    inputText.addEventListener('input', updateCharCount);
    translateBtn.addEventListener('click', translateText);

    document.querySelectorAll('.test-case').forEach(button => {
        button.addEventListener('click', () => {
            setTestCase(button.dataset.text, button.dataset.src, button.dataset.tgt);
        });
    });

    inputText.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            translateText();
        }
    });

    updateCharCount();
});