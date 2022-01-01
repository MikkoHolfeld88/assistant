""" Dataflow Management sorgt, dafür dass der Spech to Text Loop von
    außen gestartet und gestoppt werden kann und modularisiert ihn besser """

import re
from google.cloud import speech
from src.chatbot import Chatbot, MongoService, Logger
from src.speech_to_text.speech_to_text import ResumableMicrophoneStream
from src.speech_to_text.enums import STOP_PHRASES
from src.text_to_speech import speak

log = Logger.get_module_logger(__name__)

class SpeechToTextHandler:

    STREAMING_LIMIT = 120000  # 2 minutes
    SAMPLE_RATE = 8000
    CHUNK_SIZE = int(SAMPLE_RATE / 20)  # 50ms
    LANGUAGE_CODE = "de"

    CLIENT = speech.SpeechClient()
    SPEECH_CONFIG = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=LANGUAGE_CODE,
        max_alternatives=1,
    )

    STREAMING_CONFIG = speech.StreamingRecognitionConfig(
        config=SPEECH_CONFIG,
        interim_results=True,
    )

    def __init__(self, sample_rate=None, chunk_size=None):
        """ Initialisiert Instanzen von DataflowManagement

            :param sample_rate: Sample Rate mit der die Aufnahme gestreamt wird
            :param chunk_size: Größe der Chunks in welche die Aufnahme geteilt wird """

        self.stop_phrases = MongoService.get_goodbye_intents()
        self.mic_manager = ResumableMicrophoneStream(
            self.SAMPLE_RATE if sample_rate is None else sample_rate,
            self.CHUNK_SIZE if chunk_size is None else chunk_size
        )

    def start_speechToText(self):
        """ Startet den Speech to Text Loop """

        while True:
            chatbot_response = self.start_STT_loop()

            if chatbot_response == STOP_PHRASES.BREAK_LOOP.value:
                break

            speak(chatbot_response)

    def start_STT_loop(self):
        """ Startet den SpeechToText Loop """

        with self.mic_manager as stream:
            while not stream.closed:
                log.info("Started new Request for Google's speech-to-text API.")
                stream.audio_input = []
                audio_generator = stream.generator()

                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                responses = self.CLIENT.streaming_recognize(self.STREAMING_CONFIG, requests)

                return self.return_response(responses, stream)


    def return_response(self, responses, stream):
        """ Iteriert über alle Responses und gibt die Beste zurück """

        for response in responses:

            if not response.results:
                continue

            result = response.results[0]

            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            if result.is_final:
                log.debug("Transcript: %s", transcript)

                stream.last_transcript_was_final = True

                self.close_stream(stream)  # unterbricht den Stream während Jarvis eine Antwort gibt

                chatbot_response = Chatbot.respond(transcript)

                if re.compile('|'.join(self.stop_phrases), re.IGNORECASE).search(transcript):
                    return STOP_PHRASES.BREAK_LOOP.value

                return chatbot_response

    def close_stream(self, stream):
        """ Beendet den mic_stream """

        stream._audio_stream.stop_stream()
        stream._audio_stream.close()
        stream._buff.put(None)
        stream._audio_interface.terminate()
        stream.closed = True


speech_to_text_handler = SpeechToTextHandler()