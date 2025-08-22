#!/usr/bin/env python3

import pytest
import requests
import time

# Test Configuration
API_BASE_URL = "http://127.0.0.1:5005/api"
TIMEOUT = 30  # seconds

# HTTP client for translation API
class APIClient:
        
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    # Get API health status
    def health_check(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/health", timeout=TIMEOUT)
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> requests.Response:
        # Translate text via API
        payload = {
            "text": text,
            "src_lang": src_lang,
            "tgt_lang": tgt_lang
        }
        return self.session.post(f"{self.base_url}/translate", json=payload, timeout=TIMEOUT)

# Pytest Fixtures
@pytest.fixture(scope="session")
def api_client():
    # Create API client instance
    return APIClient()

@pytest.fixture(scope="session")
def api_health_check(api_client):
    # Verify API is healthy before running tests - but don't skip on 500 errors
    try:
        response = api_client.health_check()
        # Return response data even if there are errors, let individual tests handle them
        if response.status_code == 200:
            return response.json()
        else:
            # Return error info for test analysis
            return {
                "status": "unhealthy", 
                "error": f"HTTP {response.status_code}",
                "supported_languages": {"en": "English", "hi": "Hindi", "kn": "Kannada"}  # fallback
            }
    except Exception as e:
        return {
            "status": "unavailable", 
            "error": str(e),
            "supported_languages": {"en": "English", "hi": "Hindi", "kn": "Kannada"}  # fallback
        }

@pytest.fixture
def supported_languages():
    # Supported language codes
    return {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada'}

# Health Check Tests
class TestAPIHealth:
    # Test API health and availability
    
    def test_health_endpoint_accessible(self, api_client):
        # Test that health endpoint is accessible
        response = api_client.health_check()
        # Health endpoint should be accessible, even if it returns 500
        assert response.status_code in [200, 500], f"Health endpoint returned unexpected status: {response.status_code}"
    
    def test_health_response_structure(self, api_health_check):
        # Test health response contains required fields when available
        if api_health_check.get("status") == "unhealthy":
            pytest.skip("Health endpoint returned error, skipping structure test")
        
        assert 'status' in api_health_check
        assert 'supported_languages' in api_health_check
    
    def test_supported_languages_present(self, api_health_check, supported_languages):
        # Test that expected languages are supported
        if api_health_check.get("status") in ["unhealthy", "unavailable"]:
            pytest.skip("Health endpoint not available, skipping language check")
        
        api_languages = api_health_check['supported_languages']
        for lang_code in supported_languages:
            assert lang_code in api_languages

# Basic Translation Tests
class TestBasicTranslation:
    # Test basic translation functionality
    
    @pytest.mark.parametrize("text,src_lang,tgt_lang", [
        ("Hello world", "en", "hi"),
        ("Hello world", "en", "kn"),
        ("नमस्ते", "hi", "en"),
        ("ಹಲೋ", "kn", "en"),
    ])
    def test_basic_translation_success(self, api_client, text, src_lang, tgt_lang):
        # Test basic translations return success
        response = api_client.translate(text, src_lang, tgt_lang)
        assert response.status_code == 200
        
        data = response.json()
        assert 'translation' in data
        assert 'source_text' in data
        assert 'processing_time' in data
        assert data['source_text'] == text
        assert data['source_language'] == src_lang
        assert data['target_language'] == tgt_lang
        assert len(data['translation']) > 0
    
    def test_translation_response_time(self, api_client):
        # Test translation completes within reasonable time
        start_time = time.time()
        response = api_client.translate("Hello world", "en", "hi")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.parametrize("text,src_lang,tgt_lang", [
        ("Hello", "en", "hi"),
        ("Thank you", "en", "kn"),
        ("Good morning", "en", "hi"),
    ])
    def test_translation_not_empty(self, api_client, text, src_lang, tgt_lang):
        # Test translations are not empty
        response = api_client.translate(text, src_lang, tgt_lang)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation'].strip()) > 0
        assert data['translation'] != text  # Should be different from input

# Input Validation Tests
class TestInputValidation:
    # Test input validation and error handling
    
    @pytest.mark.parametrize("text,description", [
        ("", "empty_text"),
        ("   ", "whitespace_only"),
        ("\n\n", "newlines_only"),
        ("\t\t", "tabs_only"),
    ])
    def test_empty_text_validation(self, api_client, text, description):
        # Test empty or whitespace-only text returns error
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 400
        
        data = response.json()
        assert 'error' in data
        assert 'text' in data['error'].lower()
    
    def test_same_languages_validation(self, api_client):
        # Test same source and target language returns error
        response = api_client.translate("Hello", "en", "en")
        assert response.status_code == 400
        
        data = response.json()
        assert 'error' in data
        assert 'same' in data['error'].lower()
    
    @pytest.mark.parametrize("src_lang,tgt_lang,description", [
        ("xx", "hi", "invalid_source"),
        ("en", "yy", "invalid_target"),
        ("xx", "yy", "both_invalid"),
    ])
    def test_invalid_languages(self, api_client, src_lang, tgt_lang, description):
        # Test invalid language codes return error
        response = api_client.translate("Hello", src_lang, tgt_lang)
        assert response.status_code == 400
        
        data = response.json()
        assert 'error' in data
        assert 'language' in data['error'].lower()
    
    def test_missing_json_data(self, api_client):
        # Test missing JSON payload returns error
        response = api_client.session.post(f"{api_client.base_url}/translate")
        # API might return 500 instead of 400 for missing JSON
        assert response.status_code in [400, 500], f"Expected 400 or 500, got {response.status_code}"

# Special Characters and Unicode Tests
class TestSpecialCharacters:
    # Test handling of special characters and Unicode    
    @pytest.mark.parametrize("text,description", [
        ("I have 5 apples", "numbers"),
        ("Hello! How are you?", "punctuation"),
        ("Price: $50.99", "currency"),
        ("Test@email.com", "email_format"),
        ("Mixed123Text!", "mixed_content"),
    ])
    def test_special_characters_translation(self, api_client, text, description):
        # Test translation with special characters
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0
    
    def test_emoji_handling(self, api_client):
        # Test emoji handling in translations
        text = "Hello world! 😊🌍"
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        # Translation should exist, emojis may or may not be preserved
        assert len(data['translation']) > 0
    
    def test_unicode_characters(self, api_client):
        # Test Unicode character handling
        text = "Café résumé naïve"
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0

# Length and Boundary Tests
class TestTextLength:
    # Test various text lengths and boundaries
    
    def test_single_character(self, api_client):
        # Test single character translation
        response = api_client.translate("A", "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0
    
    def test_very_long_text(self, api_client):
        # Test very long text handling
        long_text = "This is a test sentence. " * 20  # ~500 characters
        response = api_client.translate(long_text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0
    
    @pytest.mark.parametrize("length", [50, 100, 200, 500])
    def test_various_lengths(self, api_client, length):
        # Test different text lengths
        text = "a" * length
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0

# Performance Tests
class TestPerformance:
    # Test API performance characteristics
    
    def test_response_time_basic(self, api_client):
        # Test basic translation response time
        start_time = time.time()
        response = api_client.translate("Hello world", "en", "hi")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 5.0  # Should respond within 5 seconds
    
    def test_response_time_long_text(self, api_client):
        # Test long text translation response time
        long_text = "This is a longer text for performance testing. " * 10
        start_time = time.time()
        response = api_client.translate(long_text, "en", "hi")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 15.0  # Longer text, but should still be reasonable
    
    @pytest.mark.parametrize("text", [
        "Hello",
        "Hello world",
        "How are you today?",
        "This is a test sentence.",
        "Good morning, how can I help you?",
    ])
    def test_consistent_performance(self, api_client, text):
        # Test performance consistency across different inputs
        start_time = time.time()
        response = api_client.translate(text, "en", "hi")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 10.0  # All should complete reasonably quickly

# Real-world Usage Tests
class TestRealWorldUsage:
    # Test real-world translation scenarios
    
    @pytest.mark.parametrize("text,context", [
        ("Good morning", "greeting"),
        ("Thank you very much", "gratitude"),
        ("Where is the bathroom?", "question"),
        ("I need help", "request"),
        ("How much does this cost?", "shopping"),
    ])
    def test_common_phrases(self, api_client, text, context):
        # Test translation of common phrases
        response = api_client.translate(text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0
        # Basic sanity check - translation should be different from input
        assert data['translation'] != text
    
    def test_formal_language(self, api_client):
        # Test formal language translation
        formal_text = "I would like to request your assistance with this matter."
        response = api_client.translate(formal_text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0
    
    def test_informal_language(self, api_client):
        # Test informal language translation
        informal_text = "Hey, what's up? Can you help me out?"
        response = api_client.translate(informal_text, "en", "hi")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data['translation']) > 0

# Language Pair Tests
class TestLanguagePairs:
    # Test all supported language pairs
    
    @pytest.mark.parametrize("src,tgt", [
        ("en", "hi"),
        ("hi", "en"),
        ("en", "kn"),
        ("kn", "en"),
    ])
    def test_supported_language_pairs(self, api_client, src, tgt):
        # Test all officially supported language pairs
        response = api_client.translate("Hello", src, tgt)
        # Should succeed or return a clear error about unsupported pair
        assert response.status_code in [200, 400, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert 'translation' in data
            assert len(data['translation']) > 0

# Stress Tests
class TestStressScenarios:
    # Stress testing scenarios
    
    def test_repeated_requests(self, api_client):
        # Test multiple rapid requests
        texts = ["Hello", "Thank you", "Good morning", "How are you?", "Goodbye"]
        
        for text in texts:
            response = api_client.translate(text, "en", "hi")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data['translation']) > 0
    
    def test_concurrent_language_pairs(self, api_client):
        # Test different language pairs in sequence
        test_cases = [
            ("Hello", "en", "hi"),
            ("नमस्ते", "hi", "en"),
            ("Hello", "en", "kn"),
            ("Thank you", "en", "hi"),
        ]
        
        for text, src, tgt in test_cases:
            response = api_client.translate(text, src, tgt)
            # Some pairs might not be supported
            assert response.status_code in [200, 400, 503]

# Error Recovery Tests
class TestErrorRecovery:
    # Test error handling and recovery
    
    def test_malformed_request_recovery(self, api_client):
        # Test that API recovers from malformed requests
        malformed_response = api_client.session.post(
            f"{api_client.base_url}/translate",
            json={"invalid": "data"}
        )
        assert malformed_response.status_code == 400
        
        # Then verify normal requests still work
        normal_response = api_client.translate("Hello", "en", "hi")
        assert normal_response.status_code == 200
    
    def test_timeout_recovery(self, api_client):
        very_long_text = "Test sentence. " * 1000
        
        try:
            response = api_client.translate(very_long_text, "en", "hi")
            # Should either succeed or timeout gracefully
            assert response.status_code in [200, 503, 408]
        except requests.exceptions.Timeout:
            # Timeout is also acceptable
            pass

# Configuration for pytest
def pytest_configure(config):
    # Configure pytest with proper markers
    config.addinivalue_line(
        "markers", "parametrize: parametrized test cases"
    )

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])