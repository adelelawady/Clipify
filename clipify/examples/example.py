from clipify.core.clipify import Clipify

def main():
    """Example usage of Clipify"""
    
    # Initialize Clipify with Hyperbolic AI and all options
    clipify = Clipify(
        provider_name="hyperbolic",
        api_key="your-hyperbolic-api-key",
        convert_to_mobile=True,
        add_captions=True,
        mobile_ratio="9:16"
    )
    
    # Process a video
    result = clipify.process_video("path/to/your/video.mp4")
    
    if result:
        print("\nProcessing Summary:")
        print(f"Processed video: {result['video_path']}")
        print(f"Created {len(result['segments'])} segments")
        
        for segment in result['segments']:
            print(f"\nSegment #{segment['segment_number']}: {segment['title']}")
            if 'cut_video' in segment:
                print(f"Cut video: {segment['cut_video']}")
            if 'mobile_video' in segment:
                print(f"Mobile version: {segment['mobile_video']}")
            if 'captioned_video' in segment:
                print(f"Captioned version: {segment['captioned_video']}")

def example_openai():
    """Example using OpenAI with only cutting (no mobile conversion or captions)"""
    clipify = Clipify(
        provider_name="openai",
        api_key="your-openai-api-key",
        convert_to_mobile=False,
        add_captions=False
    )
    return clipify.process_video("path/to/video.mp4")

def example_anthropic():
    """Example using Anthropic with mobile conversion but no captions"""
    clipify = Clipify(
        provider_name="anthropic",
        api_key="your-anthropic-api-key",
        convert_to_mobile=True,
        add_captions=False,
        mobile_ratio="4:5"
    )
    return clipify.process_video("path/to/video.mp4")

if __name__ == "__main__":
    main() 