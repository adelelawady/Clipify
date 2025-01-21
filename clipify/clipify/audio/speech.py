import whisper
from typing import Optional, Dict, Any
import os

class SpeechToText:
    def __init__(self, model_size="base"):
        """
        Initialize speech to text converter
        
        Args:
            model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model = whisper.load_model(model_size)

    def convert_to_text(self, audio_path):
        """
        Convert audio to text with timing information
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            dict: Transcription results including text and word timings
        """
        try:
            print(f"Starting transcription of: {audio_path}")
            # Validate input
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Transcribe audio
            print("Running Whisper transcription...")
            result = self.model.transcribe(audio_path)
            
            if not result or 'text' not in result:
                raise Exception("Whisper transcription failed to return valid result")
            
            print("Transcription completed successfully")
            return {
                'text': result['text'],
                'word_timings': [
                    {
                        'text': segment['text'],
                        'start': segment['start'],
                        'end': segment['end']
                    }
                    for segment in result['segments']
                ]
            }

        except Exception as e:
            print(f"Error converting speech to text: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    def process_large_file(self, audio_path: str, chunk_duration: int = 30) -> Optional[Dict[str, Any]]:
        """
        Process a large audio file by chunks
        
        Args:
            audio_path: Path to the audio file
            chunk_duration: Duration of each chunk in seconds
            
        Returns:
            Combined transcription result
        """
        try:
            result = self.convert_to_text(audio_path)
            return result
        except Exception as e:
            print(f"Error processing large file: {str(e)}")
            return None

def main():
    """Test the speech to text conversion"""
    converter = SpeechToText(model_size="base")
    result = converter.convert_to_text("test_audio.wav")
    
    if result:
        print("Transcript:", result['text'])
        print("\nSegments:")
        for segment in result['word_timings'][:3]:  # Print first 3 segments
            print(f"Text: {segment['text']}")
            print(f"Time: {segment['start']:.2f}s - {segment['end']:.2f}s")
            print("---")

if __name__ == "__main__":
    main() 