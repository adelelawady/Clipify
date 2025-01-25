
![svgviewer-output](https://github.com/user-attachments/assets/534e1369-e3ea-493c-a15d-f6aff9b175fe)


[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/adelelawady/clipify)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://github.com/adelelawady/clipify)

[![PyPI version](https://img.shields.io/pypi/v/clipify.svg)](https://pypi.org/project/clipify/)
[![Python versions](https://img.shields.io/pypi/pyversions/clipify.svg)](https://pypi.org/project/clipify/)
[![License](https://img.shields.io/pypi/l/clipify.svg)](https://github.com/adelelawady/clipify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/clipify.svg)](https://pypi.org/project/clipify/)
[![GitHub stars](https://img.shields.io/github/stars/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/issues)

A powerful Python tool for processing video content into social media-friendly segments with automated transcription, captioning, and thematic segmentation.






## Features

- 🎥 Video Processing
  - Extracts audio from video files
  - Converts speech to text with timing information
  - Segments videos by theme and content
  - Converts videos to mobile-friendly format (9:16 aspect ratio)
  - Adds auto-generated captions

- 🤖 AI-Powered Content Analysis
  - Intelligent thematic segmentation
  - Smart title generation
  - Keyword extraction
  - Sentiment analysis
  - Hashtag generation

- 📝 Transcript Processing
  - Generates accurate transcripts with timing information
  - Processes transcripts into coherent segments
  - Maintains timing alignment for precise video cutting

## Prerequisites

- Python 3.8+
- FFmpeg installed and in PATH
- NLTK resources
- Required Python packages (see requirements.txt)
- API key for content processing services

# Clone the repository:

## Installation

### install from pip

```bash
pip install clipify
```

### install from source

```bash
git clone https://github.com/adelelawady/Clipify.git
cd Clipify
```

# Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Basic video processing:

```python
from clipify.core.clipify import Clipify
    # Initialize Clipify with Hyperbolic or OpenAI or Anthropic AI and specific model
    clipify = Clipify(
        provider_name="hyperbolic",
        api_key="api-key",
        model="deepseek-ai/DeepSeek-V3",  # Specify model
        convert_to_mobile=True,
        add_captions=True,
        mobile_ratio="9:16"
    )
    
    # Process a video
    result = clipify.process_video("path/to/video.mp4")
    
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
```

## Project Structure

```
clipify/
├── clipify/
│ ├── init.py
│ ├── content_processor.py
│ ├── video_processor.py
│ └── utils/
│ ├── audio.py
│ ├── captions.py
│ └── transcription.py
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

  
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
