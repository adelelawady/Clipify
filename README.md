<p align="center"> <img src="https://github.com/user-attachments/assets/876170d2-523c-4045-b4c9-67ac957e46c1" alt="Clipify Logo" width="150"> </p>

# Clipify

> An AI-powered video processing toolkit for creating social media-optimized content with automated transcription, captioning, and thematic segmentation.

[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/adelelawady/clipify)
[![PyPI version](https://img.shields.io/pypi/v/clipify.svg)](https://pypi.org/project/clipify/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://github.com/adelelawady/clipify)
[![License](https://img.shields.io/pypi/l/clipify.svg)](https://github.com/adelelawady/clipify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/clipify.svg)](https://pypi.org/project/clipify/)
[![GitHub stars](https://img.shields.io/github/stars/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/stargazers)
[![Documentation Status](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://github.com/adelelawady/Clipify#readme)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌟 Key Features

### Content Processing
- **Video Processing Pipeline**
  - Automated audio extraction and speech-to-text conversion
  - Smart thematic segmentation using AI
  - Mobile-optimized format conversion (9:16, 4:5, 1:1)
  - Intelligent caption generation and overlay

### AI Capabilities
- **Advanced Analysis**
  - Context-aware content segmentation
  - Dynamic title generation
  - Smart keyword and hashtag extraction
  - Sentiment analysis for content optimization

### Platform Options
- **Desktop Application**
  - Intuitive graphical interface
  - Drag-and-drop functionality
  - Real-time processing feedback
  - Batch processing capabilities

- **Server Deployment**
  - RESTful API integration
  - Asynchronous processing with webhooks
  - Multi-tenant architecture
  - Containerized deployment support

## 🚀 Quick Start

### Desktop Application

🚀 Check out our full project based on Clipify on [https://github.com/adelelawady/Clipify-hub](https://github.com/adelelawady/Clipify-hub) 🚀

Download and install the latest version:

<p align="center">
  <a href="https://github.com/adelelawady/Clipify-Hub/releases/download/3.3.0/clipify-hub-installer.exe">
    <img src="https://img.shields.io/badge/Download-Installable%20App-blue?style=for-the-badge&logo=windows" alt="Download Installable">
  </a>
  <a href="https://github.com/adelelawady/Clipify-Hub/releases/download/3.3.0/clipify-hub-server.exe">
    <img src="https://img.shields.io/badge/Download-Server%20Only-green?style=for-the-badge&logo=docker" alt="Download Server">
  </a>
</p>

### Python Package Installation

```bash
# Via pip
pip install clipify

# From source
git clone https://github.com/adelelawady/Clipify.git
cd Clipify
pip install -r requirements.txt
```

## 💻 Usage Examples

### Basic Implementation
```python
from clipify.core.clipify import Clipify

# Initialize with basic configuration
clipify = Clipify(
    provider_name="hyperbolic",
    api_key="your-api-key",
    model="deepseek-ai/DeepSeek-V3",
    convert_to_mobile=True,
    add_captions=True
)

# Process video
result = clipify.process_video("input.mp4")

# Handle results
if result:
    print(f"Created {len(result['segments'])} segments")
    for segment in result['segments']:
        print(f"Segment {segment['segment_number']}: {segment['title']}")
```

### Advanced Configuration
```python
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
```


## AudioExtractor


```python
from clipify.audio.extractor import AudioExtractor

# Initialize audio extractor
extractor = AudioExtractor()

# Extract audio from video
audio_path = extractor.extract_audio(
    video_path="input_video.mp4",
    output_path="extracted_audio.wav"
)

if audio_path:
    print(f"Audio successfully extracted to: {audio_path}")
```

##  SpeechToText

```python
from clipify.audio.speech import SpeechToText

# Initialize speech to text converter
converter = SpeechToText(model_size="base")  # Options: tiny, base, small, medium, large

# Convert audio to text with timing
result = converter.convert_to_text("audio_file.wav")

if result:
    print("Transcript:", result['text'])
    print("\nWord Timings:")
    for word in result['word_timings'][:5]:  # Show first 5 words
        print(f"Word: {word['text']}")
        print(f"Time: {word['start']:.2f}s - {word['end']:.2f}s")
```

## VideoConverter

```python
from clipify.video.converter import VideoConverter

# Initialize video converter
converter = VideoConverter()

# Convert video to mobile format with blurred background
result = converter.convert_to_mobile(
    input_video="landscape_video.mp4",
    output_video="mobile_video.mp4",
    target_ratio="9:16"  # Options: "1:1", "4:5", "9:16"
)

if result:
    print("Video successfully converted to mobile format")
```


## VideoConverterStretch


```python
from clipify.video.converterStretch import VideoConverterStretch

# Initialize stretch converter
stretch_converter = VideoConverterStretch()

# Convert video using stretch method
result = stretch_converter.convert_to_mobile(
    input_video="landscape.mp4",
    output_video="stretched.mp4",
    target_ratio="4:5"  # Options: "1:1", "4:5", "9:16"
)

if result:
    print("Video successfully converted using stretch method")
```


## VideoProcessor

```python
from clipify.video.processor import VideoProcessor

# Initialize video processor with caption styling
processor = VideoProcessor(
    # Font settings
    font="Bangers-Regular.ttf",
    font_size=60,
    font_color="white",
    
    # Text effects
    stroke_width=2,
    stroke_color="black",
    shadow_strength=0.8,
    shadow_blur=0.08,
    
    # Caption behavior
    highlight_current_word=True,
    word_highlight_color="red",
    line_count=1,
    padding=50,
    position="bottom"  # Options: "bottom", "top", "center"
)

# Process video with captions
result = processor.process_video(
    input_video="input_video.mp4",
    output_video="captioned_output.mp4",
    use_local_whisper="auto"  # Options: "auto", True, False
)

if result:
    print("Video successfully processed with captions")

# Process multiple video segments
segment_files = ["segment1.mp4", "segment2.mp4", "segment3.mp4"]
processed_segments = processor.process_video_segments(
    segment_files=segment_files,
    output_dir="processed_segments"
)
```

The VideoProcessor provides powerful captioning capabilities:
- Customizable font styling and text effects
- Word-level highlighting for better readability
- Shadow and stroke effects for visibility
- Automatic speech recognition using Whisper
- Support for batch processing multiple segments

## VideoCutter

```python
from clipify.video.cutter import VideoCutter

# Initialize video cutter
cutter = VideoCutter()

# Cut a specific segment
result = cutter.cut_video(
    input_video="full_video.mp4",
    output_video="segment.mp4",
    start_time=30.5,  # Start at 30.5 seconds
    end_time=45.2     # End at 45.2 seconds
)

if result:
    print("Video segment successfully cut")
``` 


## SmartTextProcessor

```python
from clipify.core.text_processor import SmartTextProcessor
from clipify.core.ai_providers import HyperbolicAI

# Initialize AI provider and text processor
ai_provider = HyperbolicAI(api_key="your_api_key")
processor = SmartTextProcessor(ai_provider)

# Process text content
text = "Your long text content here..."
segments = processor.segment_by_theme(text)

if segments:
    for segment in segments['segments']:
        print(f"\nTitle: {segment['title']}")
        print(f"Keywords: {', '.join(segment['keywords'])}")
        print(f"Content length: {len(segment['content'])} chars")
```

## 📦 Project Structure
```
clipify/
├── clipify/
│   ├── __init__.py           # Package exports and version info
│   ├── core/
│   │   ├── __init__.py       # Core module exports
│   │   ├── clipify.py        # Main Clipify class implementation
│   │   ├── processor.py      # Content processing and segmentation
│   │   ├── text_processor.py # Text analysis and theme detection
│   │   └── ai_providers.py  # AI providers (OpenAI, Anthropic, Hyperbolic)
│   ├── video/
│   │   ├── __init__.py       # Video module exports
│   │   ├── processor.py      # Video captioning and effects
│   │   ├── converter.py      # Mobile format with blur background
│   │   ├── converter_stretch.py  # Stretch-based format conversion
│   │   └── cutter.py         # Video segment extraction
│   ├── audio/
│   │   ├── __init__.py       # Audio module exports
│   │   ├── extractor.py      # FFmpeg-based audio extraction
│   │   └── speech.py         # Whisper speech recognition
├── scripts/
│   ├── build.sh              # Package build script
│   └── publish.sh            # PyPI publishing script
├── .gitignore                # Git ignore patterns
├── LICENSE                 # MIT License
├── MANIFEST.in             # Package manifest
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
└── setup.py  # Package configuration


```

## 🛠️ Configuration Options

### AI Providers
- `hyperbolic`: Default provider with DeepSeek-V3 model
- `openai`: OpenAI GPT models support
- `anthropic`: Anthropic Claude models
- `ollama`: Local model deployment

### Video Formats
- Aspect Ratios: `1:1`, `4:5`, `9:16`
- Output Formats: MP4, MOV
- Quality Presets: Low, Medium, High

### Caption Customization
- Font customization
- Color schemes
- Position options
- Animation effects
- Word highlighting

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](LICENSE.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌐 Support

- Enterprise Support: Contact adel50ali5b@gmail.com
- Community Support: [GitHub Issues](https://github.com/adelelawady/Clipify/issues)
- Documentation: [Wiki](https://github.com/adelelawady/Clipify)

## 🙏 Acknowledgments

- FFmpeg for video processing
- OpenAI for AI capabilities
- PyTorch community
- All contributors and supporters

---

<p align="center">
  <a href="https://buymeacoffee.com/adel50ali5b">
    <img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-☕-yellow.svg" alt="Buy me a coffee">
  </a>
</p>