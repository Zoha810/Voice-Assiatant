import speech_recognition as sr
import pyttsx3

_recognizer = sr.Recognizer()
_tts_engine = pyttsx3.init()

def listen(timeout=None, phrase_time_limit=None):
    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return _recognizer.recognize_google(audio)
        except Exception:
            return ''

def speak(text: str):
    _tts_engine.say(text)
    _tts_engine.runAndWait()