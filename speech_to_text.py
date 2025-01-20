import whisper
from typing import Optional, Dict, Any
import os

class SpeechToText:
    def __init__(self, model_size: str = "base"):
        """
        Initialize the speech to text converter
        
        Args:
            model_size: Size of the Whisper model to use ("tiny", "base", "small", "medium", "large")
        """
        try:
            self.model = whisper.load_model(model_size)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None

    def convert_to_text(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Convert audio file to text with segment-level timing information
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing:
                - text: Full transcript text
                - word_timings: List of segment timing information
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            if self.model is None:
                raise RuntimeError("Whisper model not properly initialized")

            # Transcribe with timestamps
            result = self.model.transcribe(
                audio_path,
                language="en",
                word_timestamps=True
            )

            # Extract full text and segments
            full_text = result["text"]
            segments = []

            # Process segments
            for segment in result["segments"]:
                segments.append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'words': segment.get('words', [])
                })

            return {
                'text': full_text,
                'word_timings': segments
            }

        except Exception as e:
            print(f"Error in speech to text conversion: {str(e)}")
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