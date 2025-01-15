import os
import json
import nltk
from text_processor import SmartTextProcessor
from pathlib import Path
from audio_extractor import AudioExtractor
from speech_to_text import SpeechToText

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
        """Extract audio and convert to text"""
        video_path = f"{video_name}.mp4"  # Assuming MP4 format
        
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return None
            
        print("Extracting audio from video...")
        audio_path = self.audio_extractor.extract_audio(video_path)
        
        if not audio_path:
            print("Failed to extract audio from video")
            return None
            
        print(f"Audio extracted successfully to: {audio_path}")
        print("Converting speech to text...")
        
        text = self.speech_to_text.convert_to_text(audio_path)
        
        if text:
            # Save transcript
            transcript_path = self.get_transcript_path(video_name)
            try:
                os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Transcript saved to: {transcript_path}")
                return text
            except Exception as e:
                print(f"Error saving transcript: {e}")
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
                # Process the transcript into shorts
                try:
                    # Ensure NLTK resources before processing
                    self.ensure_nltk_resources()
                    
                    shorts = self.processor.create_shorts(transcript_text)
                    
                    # Add metadata about the source
                    processed_content = {
                        'video_name': video_name,
                        'shorts': shorts,
                        'metadata': {
                            'total_shorts': len(shorts),
                            'total_characters': sum(short['length'] for short in shorts),
                            'average_sentiment': sum(short['sentiment'] for short in shorts) / len(shorts) if shorts else 0
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

def main():
    # Your API key
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    # Initialize the content processor
    processor = ContentProcessor(api_key)
    
    # Example video name (without extension)
    video_name = "The True Meaning Of Life (Animated Cinematic)"
    
    # Process the video
    result = processor.process_video(video_name)
    
    if result:
        print("\n=== Processing Results ===\n")
        print(f"Video: {result['video_name']}")
        print(f"Total Shorts: {result['metadata']['total_shorts']}")
        print(f"Total Characters: {result['metadata']['total_characters']}")
        print(f"Average Sentiment: {result['metadata']['average_sentiment']:.2f}")
        print("\n=== Generated Shorts ===\n")
        
        for i, short in enumerate(result['shorts'], 1):
            print(f"Short #{i}")
            print(f"Title: {short['title']}")
            print(f"Content: {short['content']}")
            print(f"Length: {short['length']} characters")
            print(f"Sentiment: {'Positive' if short['sentiment'] > 0 else 'Negative' if short['sentiment'] < 0 else 'Neutral'}")
            print(f"Keywords: {', '.join(short['keywords'])}")
            print("\n" + "="*50 + "\n")
    else:
        print("No content was processed")

if __name__ == "__main__":
    main() 