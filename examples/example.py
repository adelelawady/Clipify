"""
Clipify Usage Examples
This file demonstrates various use cases of Clipify and its components.
"""

from clipify.core.clipify import Clipify
from clipify.audio.extractor import AudioExtractor
from clipify.audio.speech import SpeechToText
from clipify.video.converter import VideoConverter
from clipify.video.converterStretch import VideoConverterStretch
from clipify.video.cutter import VideoCutter
from clipify.core.text_processor import SmartTextProcessor
from clipify.core.ai_providers import HyperbolicAI

def basic_clipify_example():
    """
    Basic implementation of Clipify with essential features
    """
    print("\n=== Basic Clipify Example ===")
    
    # Initialize with basic configuration
    clipify = Clipify(
        provider_name="hyperbolic",
        api_key="your-api-key",
        model="deepseek-ai/DeepSeek-V3",
        convert_to_mobile=True,
        add_captions=True
    )

    # Process a video file
    result = clipify.process_video("input.mp4")
    
    if result:
        print(f"Created {len(result['segments'])} segments")
        for segment in result['segments']:
            print(f"Segment {segment['segment_number']}: {segment['title']}")

def advanced_clipify_example():
    """
    Advanced implementation of Clipify with detailed configuration
    """
    print("\n=== Advanced Clipify Example ===")
    
    clipify = Clipify(
        # AI Configuration
        provider_name="hyperbolic",
        api_key="your-api-key",
        model="deepseek-ai/DeepSeek-V3",
        max_tokens=5048,
        temperature=0.7,
        
        # Video Processing
        convert_to_mobile=True,
        add_captions=True,
        mobile_ratio="9:16",
        
        # Caption Styling
        caption_options={
            "font": "Bangers-Regular.ttf",
            "font_size": 60,
            "font_color": "white",
            "stroke_width": 2,
            "stroke_color": "black",
            "highlight_current_word": True,
            "word_highlight_color": "red",
            "shadow_strength": 0.8,
            "shadow_blur": 0.08,
            "line_count": 1,
            "padding": 50,
            "position": "bottom"
        }
    )

    result = clipify.process_video("input.mp4")
    if result:
        print("Video processed successfully with advanced configuration")

def audio_processing_example():
    """
    Demonstrates audio extraction and speech-to-text conversion
    """
    print("\n=== Audio Processing Example ===")
    
    # Audio extraction
    extractor = AudioExtractor()
    audio_path = extractor.extract_audio(
        video_path="input_video.mp4",
        output_path="extracted_audio.wav"
    )
    
    if audio_path:
        print(f"Audio extracted to: {audio_path}")
        
        # Speech to text conversion
        converter = SpeechToText(model_size="base")
        result = converter.convert_to_text(audio_path)
        
        if result:
            print("\nTranscript preview:")
            print(result['text'][:200] + "...")
            print("\nFirst 3 word timings:")
            for word in result['word_timings'][:3]:
                print(f"Word: {word['text']}, Time: {word['start']:.2f}s - {word['end']:.2f}s")

def video_processing_example():
    """
    Demonstrates various video processing capabilities
    """
    print("\n=== Video Processing Example ===")
    
    # Standard video conversion
    converter = VideoConverter()
    result = converter.convert_to_mobile(
        input_video="landscape.mp4",
        output_video="mobile_standard.mp4",
        target_ratio="9:16"
    )
    if result:
        print("Standard conversion completed")
    
    # Stretch conversion
    stretch_converter = VideoConverterStretch()
    result = stretch_converter.convert_to_mobile(
        input_video="landscape.mp4",
        output_video="mobile_stretched.mp4",
        target_ratio="4:5"
    )
    if result:
        print("Stretch conversion completed")
    
    # Video cutting
    cutter = VideoCutter()
    result = cutter.cut_video(
        input_video="full_video.mp4",
        output_video="segment.mp4",
        start_time=30.5,
        end_time=45.2
    )
    if result:
        print("Video segment cut successfully")

def text_processing_example():
    """
    Demonstrates smart text processing capabilities
    """
    print("\n=== Text Processing Example ===")
    
    # Initialize AI provider and text processor
    ai_provider = HyperbolicAI(api_key="your-api-key")
    processor = SmartTextProcessor(ai_provider)
    
    # Sample text content
    text = """
    Artificial Intelligence is transforming the way we live and work. 
    Machine learning algorithms are becoming increasingly sophisticated, 
    enabling new applications across various industries. The future of AI 
    looks promising, with potential benefits for healthcare, education, 
    and environmental conservation.
    """
    
    segments = processor.segment_by_theme(text)
    if segments:
        print("Text Processing Results:")
        for i, segment in enumerate(segments['segments'], 1):
            print(f"\nSegment {i}:")
            print(f"Title: {segment['title']}")
            print(f"Keywords: {', '.join(segment['keywords'])}")
            print(f"Content Preview: {segment['content'][:100]}...")

def main():
    """
    Main function to run all examples
    """
    print("Starting Clipify Examples...")
    
    try:
        basic_clipify_example()
        advanced_clipify_example()
        audio_processing_example()
        video_processing_example()
        text_processing_example()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
