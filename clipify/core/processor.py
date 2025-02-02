import os
import json
from .text_processor import SmartTextProcessor
from pathlib import Path
from ..audio.extractor import AudioExtractor
from ..audio.speech import SpeechToText
from ..video.cutter import VideoCutter
from ..video.processor import VideoProcessor
from ..video.converter import VideoConverter


class ContentProcessor:
    def __init__(self, ai_provider):
        """
        Initialize with an AI provider instance
        
        Args:
            ai_provider: Instance of AIProvider class
        """
        # Initialize components
        self.processor = SmartTextProcessor(ai_provider)
        self.video_processor = VideoProcessor()
        self.video_converter = VideoConverter()
        self.video_cutter = VideoCutter()
        self.audio_extractor = AudioExtractor()
        self.speech_to_text = SpeechToText()
        

        
        self.transcripts_dir = "transcripts"
        self.processed_dir = "processed_content"
        
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        for directory in [self.transcripts_dir, self.processed_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_transcript_path(self, video_name):
        """Get the path for transcript file"""
        return os.path.join(self.transcripts_dir, f"{video_name}_transcript.txt")
    
    def get_processed_path(self, video_name):
        """Get the path for processed content file"""
        # Remove any directory part and extension from video_name
        base_name = Path(video_name).stem
        return os.path.join(self.processed_dir, f"{base_name}_processed.json")
    
    def read_transcript(self, transcript_path):
        """Read transcript from file"""
        try:
            with open(transcript_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading transcript: {e}")
            return None
    
    def save_processed_content(self, video_name, content):
        """Save processed content to JSON file"""
        output_path = self.get_processed_path(video_name)
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(content, file, indent=4)
            print(f"Processed content saved to: {output_path}")
        except Exception as e:
            print(f"Error saving processed content: {e}")
    
    def extract_and_transcribe(self, video_path):
        """Extract audio and convert to text with timing information"""
        # Use the full video path directly
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return None
            
        print("Extracting audio from video...")
        audio_path = self.audio_extractor.extract_audio(video_path)
        
        if not audio_path:
            print("Failed to extract audio from video")
            return None
            
        print("Converting speech to text with timing information...")
        result = self.speech_to_text.convert_to_text(audio_path)
        
        if result:
            # Use video name without directory for saving transcript
            video_name = Path(video_path).stem
            transcript_path = self.get_transcript_path(video_name)
            timing_path = os.path.join(self.transcripts_dir, f"{video_name}_timings.json")
            
            try:
                os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
                
                # Save transcript text as a single string
                transcript_text = result['text']
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript_text)
                print(f"Transcript saved to: {transcript_path}")
                
                # Save word timings
                with open(timing_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'transcript': transcript_text,
                        'word_timings': result['word_timings']
                    }, f, indent=2)
                print(f"Word timings saved to: {timing_path}")
                
                return transcript_text
                
            except Exception as e:
                print(f"Error saving transcript or timings: {e}")
                return None
        else:
            print("Failed to convert speech to text")
            return None
    
    def process_video(self, video_path):
        """Process video content, checking for existing files"""
        try:
            self.ensure_directories()
            
            # Get base name without directory and extension
            video_name = Path(video_path).stem
            
            transcript_path = self.get_transcript_path(video_name)
            processed_path = self.get_processed_path(video_name)
            timing_path = os.path.join('transcripts', f"{video_name}_timings.json")
            
            # Check if already processed
            if os.path.exists(processed_path):
                print(f"Found existing processed content for {video_name}")
                try:
                    with open(processed_path, 'r', encoding='utf-8') as file:
                        return json.load(file)
                except Exception as e:
                    print(f"Error reading existing processed content: {e}")
            
            # Check for existing transcript
            if os.path.exists(transcript_path):
                print(f"Found existing transcript for {video_name}")
                transcript_text = self.read_transcript(transcript_path)
            else:
                print(f"No transcript found for {video_name}")
                print("Attempting to create transcript from video...")
                # Pass the full video path for transcription
                transcript_text = self.extract_and_transcribe(video_path)
            
            if transcript_text:
                # Process the transcript into segments
                try:
                    
                    # Read word timings if available
                    word_timings = None
                    if os.path.exists(timing_path):
                        with open(timing_path, 'r', encoding='utf-8') as f:
                            word_timings = json.load(f)
                    
                    # Use segment_by_theme instead of create_shorts
                    segments = self.processor.segment_by_theme(transcript_text, word_timings)
                    
                    if not segments:
                        print("Error: No segments were created")
                        return None
                    
                    # Add metadata about the source
                    processed_content = {
                        'video_name': video_name,
                        'segments': segments['segments'],  # Note: segments now includes timing data
                        'metadata': {
                            'total_segments': len(segments['segments']),
                            'total_characters': sum(len(seg['content']) for seg in segments['segments']),
                            'has_timing_data': word_timings is not None
                        }
                    }
                    
                    # Save the processed content
                    self.save_processed_content(video_name, processed_content)
                    
                    return processed_content
                    
                except Exception as e:
                    print(f"Error processing transcript: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error in process_video: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

def ensure_video_directories():
    """Ensure video processing directories exist"""
    directories = ['segmented_videos', 'processed_videos' , 'transcripts' , 'processed_content']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    pass

ensure_video_directories()

if __name__ == "__main__":
    main() 