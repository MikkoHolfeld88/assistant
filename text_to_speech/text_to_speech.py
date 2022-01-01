""" Wandelt Text-Strings in Synthetische Sprache """

from google.cloud import texttospeech
from audioplayer import AudioPlayer
import os

# print('Credendtials from environ: {}'.format(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))

def list_voices():
    """Lists the available voices."""
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        # Display the voice's name. Example: tpc-vocoded
        print(f"Name: {voice.name}")

        # Display the supported language codes for this voice. Example: "en-US"
        for language_code in voice.language_codes:
            print(f"Supported language: {language_code}")

        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print(f"SSML Voice Gender: {ssml_gender.name}")

        # Display the natural sample rate hertz for this voice. Example: 24000
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")

def speak(text):
    """Synthesizes speech from the input string of text."""

    client = texttospeech.TextToSpeechClient()
    print(text)
    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="de", name="de-DE-Wavenet-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    response = client.synthesize_speech(
        request={"input": input_text,
                 "voice": voice,
                 "audio_config": audio_config}
    )

    filename = createFilename()
    with open(filename, 'wb') as out:  # schreibt SsmlVoice in Audiodatei
        out.write(response.audio_content)

    AudioPlayer(filename).play(block=True)

def createFilename():
    creation_path = "audio"
    if not os.path.isdir(creation_path):
        os.makedirs(creation_path)

    return creation_path + "\synthesized_text.mp3"


