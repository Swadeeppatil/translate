from googletrans import Translator, LANGUAGES
import os
import json

class TranslationManager:
    def __init__(self, cache_dir="translation_cache"):
        self.translator = Translator()
        self.cache_dir = cache_dir
        self.cache = self.load_cache()
        
    def translate(self, text, source_lang, target_lang):
        """
        Translate text with caching support
        """
        cache_key = f"{text}_{source_lang}_{target_lang}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Perform translation
        try:
            translation = self.translator.translate(text, src=source_lang, dest=target_lang)
            translated_text = translation.text
            
            # Cache the result
            self.cache[cache_key] = translated_text
            self.save_cache()
            
            return translated_text
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
            
    def load_cache(self):
        """
        Load translation cache from file
        """
        cache_file = os.path.join(self.cache_dir, "translation_cache.json")
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def save_cache(self):
        """
        Save translation cache to file
        """
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = os.path.join(self.cache_dir, "translation_cache.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
            
    def get_language_code(self, language_name):
        """
        Convert language name to language code
        """
        try:
            return [k for k, v in LANGUAGES.items() if v.lower() == language_name.lower()][0]
        except IndexError:
            raise ValueError(f"Language '{language_name}' not found")
            
    def get_language_name(self, language_code):
        """
        Convert language code to language name
        """
        return LANGUAGES.get(language_code, "Unknown")
