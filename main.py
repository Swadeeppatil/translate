import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import filedialog
import json
import os
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import speech_recognition as sr
from threading import Thread
import pyperclip
from PIL import Image, ImageTk

class LinguaEase:
    def __init__(self, root):
        self.root = root
        self.root.title("LinguaEase - Language Translator")
        self.root.geometry("1000x600")
        
        # Initialize translator
        self.translator = Translator()
        self.is_dark_mode = False
        
        # Create cache directory if it doesn't exist
        self.cache_dir = "translation_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.setup_ui()
        self.load_cache()
        
    def setup_ui(self):
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Language selection
        self.setup_language_selection()
        
        # Text areas
        self.setup_text_areas()
        
        # Buttons
        self.setup_buttons()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=6, column=0, columnspan=4, pady=5)
        
    def setup_language_selection(self):
        # Source language
        ttk.Label(self.main_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.source_lang = ttk.Combobox(self.main_frame, values=list(LANGUAGES.values()))
        self.source_lang.grid(row=0, column=1, padx=5, pady=5)
        self.source_lang.set('english')
        
        # Target language
        ttk.Label(self.main_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.target_lang = ttk.Combobox(self.main_frame, values=list(LANGUAGES.values()))
        self.target_lang.grid(row=0, column=3, padx=5, pady=5)
        self.target_lang.set('spanish')
        
    def setup_text_areas(self):
        # Source text
        self.source_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=40, height=10)
        self.source_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Target text
        self.target_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=40, height=10)
        self.target_text.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
    def setup_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Translate button
        self.translate_btn = ttk.Button(button_frame, text="Translate", command=self.translate)
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_text)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        self.copy_btn = ttk.Button(button_frame, text="Copy Translation", command=self.copy_translation)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Speech recognition button
        self.speech_btn = ttk.Button(button_frame, text="🎤 Speech to Text", command=self.start_speech_recognition)
        self.speech_btn.pack(side=tk.LEFT, padx=5)
        
        # Text to speech buttons
        self.tts_source_btn = ttk.Button(button_frame, text="🔊 Read Source", command=lambda: self.text_to_speech('source'))
        self.tts_source_btn.pack(side=tk.LEFT, padx=5)
        
        self.tts_target_btn = ttk.Button(button_frame, text="🔊 Read Translation", command=lambda: self.text_to_speech('target'))
        self.tts_target_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(button_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
    def translate(self):
        try:
            source_text = self.source_text.get("1.0", tk.END).strip()
            if not source_text:
                return
                
            # Get language codes
            source_lang = [k for k, v in LANGUAGES.items() if v.lower() == self.source_lang.get().lower()][0]
            target_lang = [k for k, v in LANGUAGES.items() if v.lower() == self.target_lang.get().lower()][0]
            
            # Check cache first
            cache_key = f"{source_text}_{source_lang}_{target_lang}"
            if cache_key in self.translation_cache:
                translated_text = self.translation_cache[cache_key]
            else:
                # Perform translation
                translation = self.translator.translate(source_text, src=source_lang, dest=target_lang)
                translated_text = translation.text
                # Cache the translation
                self.translation_cache[cache_key] = translated_text
                self.save_cache()
            
            # Update UI
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", translated_text)
            self.status_var.set("Translation completed!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
            self.status_var.set("Translation failed!")
            
    def clear_text(self):
        self.source_text.delete("1.0", tk.END)
        self.target_text.delete("1.0", tk.END)
        self.status_var.set("")
        
    def copy_translation(self):
        translation = self.target_text.get("1.0", tk.END).strip()
        if translation:
            pyperclip.copy(translation)
            self.status_var.set("Translation copied to clipboard!")
            
    def start_speech_recognition(self):
        def recognize_speech():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.status_var.set("Listening... Speak now!")
                try:
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio)
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", text)
                    self.status_var.set("Speech recognition completed!")
                    self.translate()
                except sr.UnknownValueError:
                    self.status_var.set("Could not understand audio")
                except sr.RequestError:
                    self.status_var.set("Could not request results")
                except Exception as e:
                    self.status_var.set(f"Error: {str(e)}")
        
        Thread(target=recognize_speech).start()
        
    def text_to_speech(self, text_type):
        try:
            if text_type == 'source':
                text = self.source_text.get("1.0", tk.END).strip()
                lang = [k for k, v in LANGUAGES.items() if v.lower() == self.source_lang.get().lower()][0]
            else:
                text = self.target_text.get("1.0", tk.END).strip()
                lang = [k for k, v in LANGUAGES.items() if v.lower() == self.target_lang.get().lower()][0]
            
            if text:
                tts = gTTS(text=text, lang=lang)
                tts.save("temp.mp3")
                os.system("start temp.mp3")
                self.status_var.set("Playing audio...")
        except Exception as e:
            messagebox.showerror("Error", f"Text-to-speech failed: {str(e)}")
            
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        bg_color = '#2b2b2b' if self.is_dark_mode else 'white'
        fg_color = 'white' if self.is_dark_mode else 'black'
        
        self.root.configure(bg=bg_color)
        self.main_frame.configure(style='Dark.TFrame' if self.is_dark_mode else 'TFrame')
        
        # Update text areas
        self.source_text.configure(bg=bg_color, fg=fg_color)
        self.target_text.configure(bg=bg_color, fg=fg_color)
        
        # Update button text
        self.theme_btn.configure(text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode")
        
    def load_cache(self):
        try:
            with open(os.path.join(self.cache_dir, 'translation_cache.json'), 'r', encoding='utf-8') as f:
                self.translation_cache = json.load(f)
        except FileNotFoundError:
            self.translation_cache = {}
            
    def save_cache(self):
        with open(os.path.join(self.cache_dir, 'translation_cache.json'), 'w', encoding='utf-8') as f:
            json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = LinguaEase(root)
    root.mainloop()
