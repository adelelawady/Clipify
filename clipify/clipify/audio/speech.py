import whisper
from typing import Optional, Dict, Any
import os
import sys



class SpeechToText:
    def __init__(self, model_size="base"):
        """
        Initialize speech to text converter
        
        Args:
            model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        # Determine the base path
        if getattr(sys, 'frozen', False):  # If running as PyInstaller .exe
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Set Whisper’s asset directory
        whisper.utils.ASSET_DIR = os.path.join(base_path, "whisper/assets")
        self.model = whisper.load_model(model_size,)

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

            # Transcribe audio with word timestamps
            print("Running Whisper transcription with word timestamps...")
            result = self.model.transcribe(audio_path, word_timestamps=True)
            
            if not result or 'text' not in result:
                raise Exception("Whisper transcription failed to return valid result")
            
            print("Transcription completed successfully")
            
            # Process word-level timestamps
            word_timings = []
            for segment in result['segments']:
                if 'words' not in segment:
                    continue
                    
                for word_data in segment['words']:
                    # Check if word_data has the required fields
                    if isinstance(word_data, dict) and 'word' in word_data and 'start' in word_data and 'end' in word_data:
                        word_timings.append({
                            'text': word_data['word'].strip(),
                            'start': word_data['start'],
                            'end': word_data['end']
                        })
                    else:
                        print(f"Warning: Skipping malformed word data: {word_data}")
            
            if not word_timings:
                print("Warning: No valid word timings found in transcription")
            
            return {
                'text': result['text'],
                'word_timings': word_timings
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