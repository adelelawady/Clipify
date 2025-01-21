import os
import json
import nltk
from .text_processor import SmartTextProcessor
from pathlib import Path
from ..audio.extractor import AudioExtractor
from ..audio.speech import SpeechToText
from ..video.cutter import VideoCutter
from ..video.processor import VideoProcessor
from ..video.converter import VideoConverter

# Download required NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"Warning: Error downloading NLTK resources: {e}")

class ContentProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("CLIPIFY_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set it via constructor or CLIPIFY_API_KEY environment variable")
        
        # Initialize components
        self.video_processor = VideoProcessor()
        self.video_converter = VideoConverter()
        self.video_cutter = VideoCutter()
        self.audio_extractor = AudioExtractor()
        self.speech_to_text = SpeechToText()
        self.text_processor = SmartTextProcessor(api_key=self.api_key)
        
        # Ensure NLTK resources are downloaded
        self.ensure_nltk_resources()
        
        self.transcripts_dir = "transcripts"
        self.processed_dir = "processed_content"
        
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
        """
        Process a video file into social media-friendly segments
        
        Args:
            video_name (str): Path to input video file
            
        Returns:
            dict: Processing results including segments and metadata
        """
        try:
            print("Extracting audio from video...")
            # Extract audio
            audio_path = self.audio_extractor.extract_audio(f"{video_name}.mp4")
            if not audio_path:
                raise Exception("Failed to extract audio from video")
            
            print("Converting speech to text...")
            # Convert speech to text
            transcript = self.speech_to_text.convert_to_text(audio_path)
            if not transcript:
                raise Exception("Failed to convert speech to text")
            
            print("Processing text into segments...")
            # Process text into segments
            segments = self.text_processor.create_shorts(transcript['text'])
            if not segments:
                raise Exception("Failed to create segments from text")
            
            return {
                'video_name': video_name,
                'segments': segments,
                'metadata': {
                    'total_segments': len(segments),
                    'transcript': transcript
                }
            }
            
        except Exception as e:
            print(f"Error in process_video: {str(e)}")
            print("Full error details:", e.__class__.__name__)
            import traceback
            print(traceback.format_exc())
            return None

def ensure_video_directories():
    """Ensure video processing directories exist"""
    directories = ['segmented_videos', 'processed_videos' , 'transcripts' , 'processed_content']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def main():
    # Your API key
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    processor = ContentProcessor(api_key)
    video_name = "How Lust Destroys Your Life - Atlas (720p, h264)"
    
    # Process video content
    result = processor.process_video(video_name)
    
    if result:
        print("\n=== Processing Results ===\n")
        print(f"Video: {result['video_name']}")
        print(f"Total Segments: {result['metadata']['total_segments']}")
        
        # Initialize video cutter, processor and converter
        video_cutter = VideoCutter()
        video_processor = VideoProcessor()
        video_converter = VideoConverter()
        
        # Create shorts from processed segments
        input_video = f"{video_name}.mp4"
        
        if not os.path.exists(input_video):
            print(f"Error: Input video not found: {input_video}")
            return
            
        # Create output directories
        Path("segmented_videos").mkdir(exist_ok=True)
        Path("processed_videos").mkdir(exist_ok=True)
        
        print("\n=== Cutting Video Segments ===\n")
        
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
                    
                    # Convert the segment to mobile format
                    print(f"Converting segment #{i} to mobile format...")
                    mobile_segment = f"segmented_videos/segment_{i}_{clean_title}_mobile.mp4"
                    conversion_result = video_converter.convert_to_mobile(
                        output_segment,
                        mobile_segment,
                        target_ratio="6:19"
                    )
                    
                    if conversion_result:
                        print(f"Successfully converted segment #{i} to mobile format")
                        
                        # Process the mobile segment with captions
                        output_processed = f"processed_videos/segment_{i}_{clean_title}_captioned.mp4"
                        process_result = video_processor.process_video(
                            input_video=mobile_segment,
                            output_video=output_processed
                        )
                        
                        if process_result:
                            print(f"Successfully added captions to segment #{i}")
                        else:
                            print(f"Failed to add captions to segment #{i}")
                    else:
                        print(f"Failed to convert segment #{i} to mobile format")
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