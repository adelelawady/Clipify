<p align="center">
  <img src="https://github.com/user-attachments/assets/58aecd53-d720-4716-96f2-002beebb52b3" alt="Clipify Logo" width="100"/>
</p>

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

Download and install the latest version:

<p align="center">
  <a href="https://github.com/adelelawady/clipify-hub/releases/download/latest/clipify-hub-installer.exe">
    <img src="https://img.shields.io/badge/Download-Desktop%20App-blue?style=for-the-badge&logo=windows" alt="Download Desktop">
  </a>
  <a href="https://github.com/adelelawady/clipify-hub/releases/download/latest/clipify-hub-server.exe">
    <img src="https://img.shields.io/badge/Download-Server-green?style=for-the-badge&logo=docker" alt="Download Server">
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

## 📦 Project Structure
```
clipify/
├── clipify/
│   ├── __init__.py
│   ├── core/
│   │   ├── clipify.py
│   │   ├── content_processor.py
│   │   └── video_processor.py
│   └── utils/
│       ├── audio.py
│       ├── captions.py
│       └── transcription.py
├── tests/
├── examples/
├── docs/
└── requirements.txt
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

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌐 Support

- Enterprise Support: Contact support@clipify.ai
- Community Support: [GitHub Issues](https://github.com/adelelawady/Clipify/issues)
- Documentation: [Wiki](https://github.com/adelelawady/Clipify/wiki)

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