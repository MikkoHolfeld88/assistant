""" Die Init-Datei des DetectionService gibt das Singleton nach Außen"""

from src.detection_service.detection_service import DetectionService

def __init__():
    __all__ = ["DetectionService"]