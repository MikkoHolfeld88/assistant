""" Detection Service stellt die Hotword Detection für einen Spachbot """

import struct
from pyaudio import PyAudio, paInt16
import pvporcupine
from src.chatbot.logging_service.Logger import get_module_logger
log = get_module_logger(__name__)


porcupine = None
pa = None
audio_stream = None

class DetectionService():

    def __init__(self):
        self.porcupine = self.init_porcupine()
        self.pyaudio = PyAudio()
        self.audio_stream = self.init_audio_stream()

    def init_porcupine(self):
        return pvporcupine.create(keywords=["jarvis"])

    def init_audio_stream(self):
        return self.pyaudio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length)

    def start_loop(self):
        self.hotword_detected = False

        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            keyword_index = self.porcupine.process(pcm)

            if keyword_index >= 0:
                log.info("Hotword detected.")
                self.hotword_detected = True

            if self.hotword_detected:
                self.pyaudio.close(self.audio_stream)
                break


detection_service = DetectionService()

if __name__ == "__main__":
    detection_service.start_loop()