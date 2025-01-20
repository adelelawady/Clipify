import os
import json
import nltk
from text_processor import SmartTextProcessor
from pathlib import Path
from audio_extractor import AudioExtractor
from speech_to_text import SpeechToText
from video_cutter import VideoCutter
from video_processor import VideoProcessor

# Download required NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"Warning: Error downloading NLTK resources: {e}")

class ContentProcessor:
    def __init__(self, api_key):
        # Ensure NLTK resources are downloaded
        self.ensure_nltk_resources()
        
        self.processor = SmartTextProcessor(api_key)
        self.transcripts_dir = "transcripts"
        self.processed_dir = "processed_content"
        self.audio_extractor = AudioExtractor()
        self.speech_to_text = SpeechToText()
        
    def ensure_nltk_resources(self):
        """Ensure all required NLTK resources are available"""
        required_resources = [
            'punkt',
            'punkt_tab',
            'averaged_perceptron_tagger',
            'stopwords'
        ]
        
        for resource in required_resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                print(f"Downloading required NLTK resource: {resource}")
                nltk.download(resource, quiet=True)
    
    def ensure_directories(self):
        """Ensure necessary directories exist"""
        for directory in [self.transcripts_dir, self.processed_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_transcript_path(self, video_name):
        """Get the path for transcript file"""
        return os.path.join(self.transcripts_dir, f"{video_name}_transcript.txt")
    
    def get_processed_path(self, video_name):
        """Get the path for processed content file"""
        return os.path.join(self.processed_dir, f"{video_name}_processed.json")
    
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
    
    def extract_and_transcribe(self, video_name):
        """Extract audio and convert to text with timing information"""
        video_path = f"{video_name}.mp4"
        
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
            # Save transcript
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
    
    def process_video(self, video_name):
        """Process video content, checking for existing files"""
        try:
            self.ensure_directories()
            
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
                transcript_text = self.extract_and_transcribe(video_name)
            
            if transcript_text:
                # Process the transcript into segments
                try:
                    # Ensure NLTK resources before processing
                    self.ensure_nltk_resources()
                    
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
    directories = ['segmented_videos', 'processed_videos']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    # Your API key
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    processor = ContentProcessor(api_key)
    video_name = "How Lust Destroys Your Life - Atlas (720p, h264).mp4"
    
    # Process video content
    result = processor.process_video(video_name)
    
    if result:
        print("\n=== Processing Results ===\n")
        print(f"Video: {result['video_name']}")
        print(f"Total Segments: {result['metadata']['total_segments']}")
        print(f"Has Timing Data: {result['metadata']['has_timing_data']}")
        
        # Initialize video cutter and processor
        video_cutter = VideoCutter()
        video_processor = VideoProcessor()
        
        # Create shorts from processed segments
        input_video = f"{video_name}.mp4"
        
        if not os.path.exists(input_video):
            print(f"Error: Input video not found: {input_video}")
            return
            
        print("\n=== Cutting Video Segments ===\n")
        
        # Create output directories
        Path("segmented_videos").mkdir(exist_ok=True)
        Path("processed_videos").mkdir(exist_ok=True)
        
        for i, segment in enumerate(result['segments'], 1):
            try:
                if 'start_time' not in segment or 'end_time' not in segment:
                    print(f"Warning: Segment {i} missing timing information")
                    continue
                    
                # Clean the title for filename
                clean_title = "".join(c for c in segment['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                
                # Cut the segment
                output_segment = f"segmented_videos/segment_{i}_{clean_title}.mp4"
                cut_result = video_cutter.cut_video(
                    input_video,
                    output_segment,
                    float(segment['start_time']),
                    float(segment['end_time'])
                )
                
                if cut_result:
                    print(f"Successfully cut segment #{i}: {segment['title']}")
                    
                    # Process the segment with captions
                    output_processed = f"processed_videos/segment_{i}_{clean_title}_captioned.mp4"
                    process_result = video_processor.process_video(
                        input_video=output_segment,
                        output_video=output_processed
                    )
                    
                    if process_result:
                        print(f"Successfully added captions to segment #{i}")
                    else:
                        print(f"Failed to add captions to segment #{i}")
                else:
                    print(f"Failed to cut segment #{i}")
                    
            except Exception as e:
                print(f"Error processing segment #{i}: {str(e)}")
                continue
    else:
        print("No content was processed")

ensure_video_directories()

if __name__ == "__main__":
    main() 