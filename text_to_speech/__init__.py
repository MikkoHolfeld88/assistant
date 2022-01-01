""" Die Init-Datei von text_to_speech gibt verschiedne Funktionen nach Außen"""

from src.text_to_speech.text_to_speech import speak, list_voices

def __init__():
    __all__ = ["speak", "list_voices"]