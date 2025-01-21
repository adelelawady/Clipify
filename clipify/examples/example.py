from clipify import (
    ContentProcessor, 
    VideoCutter,
    VideoConverter,
    VideoProcessor,
    AudioExtractor
)
import os
from pathlib import Path

def process_video_with_custom_settings():
    # Initialize components
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    processor = ContentProcessor(api_key)
    video_name = "test_video"
        
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
                        target_ratio="9:16"
                    )
                    
                    if conversion_result:
                        print(f"Successfully converted segment #{i} to mobile format")
                        
                        print(f"Processing segment #{i} with captions...")

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

def ensure_video_directories():
    """Ensure video processing directories exist"""
    directories = ['segmented_videos', 'processed_videos', 'transcripts', 'processed_content']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_video_directories()
    print("Starting video processing...")
    process_video_with_custom_settings()
    print("\nProcessing complete!") 