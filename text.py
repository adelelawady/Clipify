from text_processor import SmartTextProcessor
import os

def process_video_transcript(transcript_file_path):
    # Your API key - replace with your actual API key
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    # Initialize the processor
    processor = SmartTextProcessor(api_key)
    
    # Read the transcript file
    try:
        with open(transcript_file_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
            
        # Process the transcript
        # segments = processor.create_shorts(transcript_text)
         # First, segment the text by themes
        thematic_segments = processor.segment_by_theme(transcript_text)

        # print("thematic_segments", thematic_segments)

        # print("segments", segments)

        # Create output directory if it doesn't exist
        output_dir = "processed_content"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results to a file
        output_file = os.path.join(output_dir, 
                                 os.path.basename(transcript_file_path).replace('.txt', '_processed.json'))
        
        # Print the results
        print(f"\n=== Processing Results for {os.path.basename(transcript_file_path)} ===\n")
        for i, segment in enumerate(thematic_segments):
            print(f"Segment #{i}")
            print(f"Title: {segment['title']}")
            print(f"Duration: {segment['estimated_duration']}")
            print(f"Keywords: {', '.join(segment['keywords'])}")
            print(f"Content: {segment['content']}\n")
            print("-" * 50 + "\n")
            
        return thematic_segments
        
    except FileNotFoundError:
        print(f"Error: Could not find transcript file at {transcript_file_path}")
        return None
    except Exception as e:
        print(f"Error processing transcript: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    transcript_path = "transcripts/The True Meaning Of Life (Animated Cinematic)_transcript.txt"
    processed_segments = process_video_transcript(transcript_path)