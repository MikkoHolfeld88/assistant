""" Die Init-Datei von speech_to_text gibt verschiedene Funktionen nach Außen """

from src.speech_to_text.speech_to_text_handler import speech_to_text_handler as SpeechToTextHandler
from src.speech_to_text.speech_to_text import listen_return_response, main as start_transcription_loop

def __init__():
    __all__ = ["listen_return_response", "SpeechToTextHandler", "start_transcription_loop"]