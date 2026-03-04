import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VoiceEngine:
    def __init__(self):
        self.client = OpenAI()

    def transcribe(self, audio_file_path):
        """Transcribes an audio file to text."""
        with open(audio_file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript

    def speak(self, text, output_path="response.mp3"):
        """Converts text to speech and saves it to a file."""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(output_path)
        return output_path
