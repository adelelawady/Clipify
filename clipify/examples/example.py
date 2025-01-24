from clipify.core.clipify import Clipify
from clipify.clipify.core.ai_providers import HyperbolicAI, OpenAIProvider, AnthropicProvider

def main():
    """Example usage of Clipify"""
    
    # Initialize Clipify with Hyperbolic AI and specific model
    clipify = Clipify(
        provider_name="hyperbolic",
        api_key="your-hyperbolic-api-key",
        model="deepseek-ai/DeepSeek-V3",  # Specify model
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
    """Example using OpenAI GPT-4"""
    clipify = Clipify(
        provider_name="openai",
        api_key="your-openai-api-key",
        model="gpt-4",  # Specify GPT-4 model
        convert_to_mobile=False,
        add_captions=False
    )
    return clipify.process_video("path/to/video.mp4")

def example_anthropic():
    """Example using Claude 3 Opus"""
    clipify = Clipify(
        provider_name="anthropic",
        api_key="your-anthropic-api-key",
        model="claude-3-opus",  # Specify Claude 3 Opus model
        convert_to_mobile=True,
        add_captions=False,
        mobile_ratio="4:5"
    )
    return clipify.process_video("path/to/video.mp4")

def list_available_models():
    """Print available models for each provider"""
    print("Available Models:")
    print("\nHyperbolic AI:")
    for model in HyperbolicAI.AVAILABLE_MODELS:
        if model != "default":
            print(f"  - {model}")
    
    print("\nOpenAI:")
    for model in OpenAIProvider.AVAILABLE_MODELS:
        if model != "default":
            print(f"  - {model}")
    
    print("\nAnthropic:")
    for model in AnthropicProvider.AVAILABLE_MODELS:
        if model != "default":
            print(f"  - {model}")

if __name__ == "__main__":
    # Optionally show available models
    list_available_models()
    print("\nStarting processing...")
    main() 