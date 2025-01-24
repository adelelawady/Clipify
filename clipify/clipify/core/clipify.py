from pathlib import Path
import os
from .processor import ContentProcessor
from .ai_providers import get_ai_provider
from ..video.cutter import VideoCutter
from ..video.processor import VideoProcessor
from ..video.converter import VideoConverter

class Clipify:
    """Main interface for Clipify video processing"""
    
    def __init__(
        self,
        provider_name="hyperbolic",
        api_key=None,
        model="default",
        convert_to_mobile=True,
        add_captions=True,
        mobile_ratio="9:16"
    ):
        """
        Initialize Clipify with processing options
        
        Args:
            provider_name: Name of AI provider ('hyperbolic', 'openai', or 'anthropic')
            api_key: API key for the chosen provider
            model: Model name to use (provider-specific, defaults to provider's default model)
            convert_to_mobile: Whether to convert segments to mobile format
            add_captions: Whether to add captions to segments
            mobile_ratio: Aspect ratio for mobile conversion
        """
        # Store configuration
        self.convert_to_mobile = convert_to_mobile
        self.add_captions = add_captions
        self.mobile_ratio = mobile_ratio
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv(f"{provider_name.upper()}_API_KEY")
            if not api_key:
                raise ValueError(
                    f"No API key provided for {provider_name}. "
                    f"Set {provider_name.upper()}_API_KEY environment variable or pass api_key parameter."
                )
        
        # Initialize AI provider and processor
        self.ai_provider = get_ai_provider(provider_name, api_key, model)
        self.processor = ContentProcessor(self.ai_provider)
        
        # Initialize video components only if needed
        self.video_cutter = VideoCutter()
        self.video_processor = VideoProcessor() if add_captions else None
        self.video_converter = VideoConverter() if convert_to_mobile else None
        
        # Ensure directories exist
        self.ensure_directories()
    
    @staticmethod
    def ensure_directories():
        """Ensure necessary directories exist"""
        directories = ['segmented_videos', 'processed_videos', 'transcripts', 'processed_content']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def process_video(self, video_path):
        """
        Process a video file with the configured options
        
        Args:
            video_path: Path to the input video file
        
        Returns:
            dict: Processing results including paths to generated files
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Process video content
        result = self.processor.process_video(video_path)
        
        if not result:
            print("No content was processed")
            return None
        
        print("\n=== Processing Results ===\n")
        print(f"Video: {result['video_name']}")
        print(f"Total Segments: {result['metadata']['total_segments']}")
        
        processed_segments = []
        print("\n=== Processing Video Segments ===\n")
        
        for i, segment in enumerate(result['segments'], 1):
            try:
                if 'start_time' not in segment or 'end_time' not in segment:
                    print(f"Warning: Segment {i} missing timing information")
                    continue
                
                # Clean the title for filename
                clean_title = "".join(c for c in segment['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                
                segment_info = {
                    'title': segment['title'],
                    'segment_number': i
                }
                
                # Cut the segment
                output_segment = f"segmented_videos/segment_{i}_{clean_title}.mp4"
                cut_result = self.video_cutter.cut_video(
                    video_path,
                    output_segment,
                    float(segment['start_time']),
                    float(segment['end_time'])
                )
                
                if cut_result:
                    print(f"Successfully cut segment #{i}: {segment['title']}")
                    segment_info['cut_video'] = output_segment
                    current_output = output_segment
                    
                    # Convert to mobile if requested
                    if self.convert_to_mobile:
                        print(f"Converting segment #{i} to mobile format...")
                        mobile_segment = f"segmented_videos/segment_{i}_{clean_title}_mobile.mp4"
                        conversion_result = self.video_converter.convert_to_mobile(
                            output_segment,
                            mobile_segment,
                            target_ratio=self.mobile_ratio
                        )
                        
                        if conversion_result:
                            print(f"Successfully converted segment #{i} to mobile format")
                            segment_info['mobile_video'] = mobile_segment
                            current_output = mobile_segment
                        else:
                            print(f"Failed to convert segment #{i} to mobile format")
                            continue
                    
                    # Add captions if requested
                    if self.add_captions:
                        print(f"Processing segment #{i} with captions...")
                        output_processed = f"processed_videos/segment_{i}_{clean_title}_captioned.mp4"
                        process_result = self.video_processor.process_video(
                            input_video=current_output,
                            output_video=output_processed
                        )
                        
                        if process_result:
                            print(f"Successfully added captions to segment #{i}")
                            segment_info['captioned_video'] = output_processed
                        else:
                            print(f"Failed to add captions to segment #{i}")
                    
                    processed_segments.append(segment_info)
                else:
                    print(f"Failed to cut segment #{i}")
                
            except Exception as e:
                print(f"Error processing segment #{i}: {str(e)}")
                continue
        
        return {
            'video_path': video_path,
            'segments': processed_segments,
            'metadata': result['metadata']
        } 