from text_processor import SmartTextProcessor
import os
import json

def process_video_transcript(transcript_file_path, timing_file_path=None):
    """Process video transcript with optional word timing data"""
    
    api_key = "your-api-key"
    processor = SmartTextProcessor(api_key)
    
    try:
        # Read the transcript
        with open(transcript_file_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
        
        # Read word timings if provided
        word_timings = None
        if timing_file_path and os.path.exists(timing_file_path):
            with open(timing_file_path, 'r', encoding='utf-8') as file:
                word_timings = json.load(file)
        
        # Process the transcript with timing data
        segments = processor.process_transcript(transcript_text, word_timings)
        
        if not segments:
            return None
            
        # Create output directory
        output_dir = "processed_content"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save results
        output_file = os.path.join(output_dir, 
                                 os.path.basename(transcript_file_path).replace('.txt', '_processed.json'))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'transcript_file': transcript_file_path,
                'timing_file': timing_file_path,
                'segments': segments
            }, f, indent=2, ensure_ascii=False)
        
        # Print results
        print(f"\n=== Processing Results for {os.path.basename(transcript_file_path)} ===\n")
        for i, segment in enumerate(segments, 1):
            print(f"Segment #{i}")
            print(f"Title: {segment['title']}")
            print(f"Duration: {segment['estimated_duration']}")
            if segment.get('start_time'):
                print(f"Video Time: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
            print(f"Keywords: {', '.join(segment['keywords'])}")
            print(f"Content: {segment['content']}\n")
            print("-" * 50 + "\n")
            
        return segments
        
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        return None

if __name__ == "__main__":
    transcript_path = "transcripts/The True Meaning Of Life (Animated Cinematic)_transcript.txt"
    timing_path = "transcripts/The True Meaning Of Life (Animated Cinematic)_timings.json"
    processed_segments = process_video_transcript(transcript_path, timing_path)