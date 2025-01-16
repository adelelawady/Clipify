from vosk import Model, KaldiRecognizer
import wave
import json
import os

class SpeechToText:
    def __init__(self, model_path="vosk-model-small-en-us"):
        """
        Initialize speech to text converter
        :param model_path: Path to Vosk model (will download if not exists)
        """
        # Download model if it doesn't exist
        if not os.path.exists(model_path):
            print("Downloading Vosk model (this may take a while)...")
            import wget
            wget.download("https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
            # Extract the model
            import zipfile
            with zipfile.ZipFile("vosk-model-small-en-us-0.15.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.rename("vosk-model-small-en-us-0.15", model_path)

        self.model = Model(model_path)

    def convert_to_text(self, audio_path):
        """
        Convert audio file to text using Vosk speech recognition
        Returns both text and word timings
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            wf = wave.open(audio_path, "rb")
            
            if wf.getnchannels() != 1:
                raise ValueError("Audio file must be mono")
            if wf.getsampwidth() != 2:
                raise ValueError("Audio file must be WAV format PCM16")
            if wf.getcomptype() != "NONE":
                raise ValueError("Audio file must be WAV format PCM16")

            recognizer = KaldiRecognizer(self.model, wf.getframerate())
            recognizer.SetWords(True)  # Enable word timing

            full_text = []
            word_timings = []
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if 'result' in result:
                        # Extract word timings
                        for word in result['result']:
                            word_timings.append({
                                'word': word['word'],
                                'start': word['start'],
                                'end': word['end']
                            })
                    if 'text' in result and result['text'].strip():
                        full_text.append(result['text'])

            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if 'result' in final_result:
                for word in final_result['result']:
                    word_timings.append({
                        'word': word['word'],
                        'start': word['start'],
                        'end': word['end']
                    })
            if 'text' in final_result and final_result['text'].strip():
                full_text.append(final_result['text'])

            wf.close()

            return {
                'text': ' '.join(full_text),
                'word_timings': word_timings
            }

        except Exception as e:
            print(f"Error converting speech to text: {str(e)}")
            return None 