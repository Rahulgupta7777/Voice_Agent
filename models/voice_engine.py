import os
from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()

class VoiceEngine:
    def __init__(self):
        self.deepgram = DeepgramClient()

    def transcribe(self, audio_file_path):
        """Transcribes an audio file to text using Deepgram Nova-2."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                buffer_data = audio_file.read()

            response = self.deepgram.listen.v1.media.transcribe_file(
                request=buffer_data,
                model="nova-2",
                smart_format=True
            )
            # Access the response data using dictionary access or object attributes
            # Assuming Fern generated python model structure:
            if hasattr(response, 'results'):
                return response.results.channels[0].alternatives[0].transcript
            else:
                return response['results']['channels'][0]['alternatives'][0]['transcript']
        except Exception as e:
            print(f"STT Error: {e}")
            return "Transcription failed."

    def speak(self, text, output_path="response.mp3"):
        """Converts text to speech using Deepgram Aura."""
        try:
            audio_stream = self.deepgram.speak.v1.audio.generate(
                text=text,
                model="aura-asteria-en"
            )
            with open(output_path, 'wb') as f:
                for chunk in audio_stream:
                    f.write(chunk)
            return output_path
        except Exception as e:
            print(f"TTS Error: {e}")
            return output_path
