

<p align="center">
  <img src="https://github.com/user-attachments/assets/58aecd53-d720-4716-96f2-002beebb52b3" alt="Clipify Logo" width="100"/>
</p>

[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/adelelawady/clipify)
[![PyPI version](https://img.shields.io/pypi/v/clipify.svg)](https://pypi.org/project/clipify/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://github.com/adelelawady/clipify)
[![License](https://img.shields.io/pypi/l/clipify.svg)](https://github.com/adelelawady/clipify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/clipify.svg)](https://pypi.org/project/clipify/)
[![GitHub stars](https://img.shields.io/github/stars/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/issues)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/adelelawady/Clipify/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://makeapullrequest.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://github.com/adelelawady/Clipify#readme)
[![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)](https://github.com/adelelawady/Clipify)
[![GitHub contributors](https://img.shields.io/github/contributors/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/graphs/contributors/)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/adelelawady/Clipify/issues)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/adelelawady/Clipify)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org/)

<!-- Social & Support -->
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-☕-yellow.svg)](https://buymeacoffee.com/adel50ali5b)



A powerful Python tool for processing video content into social media-friendly segments with automated transcription, captioning, and thematic segmentation.


![Screenshot 2025-01-25 045729](https://github.com/user-attachments/assets/f6b9ff76-181b-4de8-b19a-78eff0a2c86a)




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
