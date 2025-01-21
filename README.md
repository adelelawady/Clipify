# Video Content Processor

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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adelelawady/Clipify.git
cd Clipify
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Download required NLTK resources:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
```

## Usage

1. Basic video processing:
```python
from content_processor import ContentProcessor

# Initialize processor with your API key
processor = ContentProcessor(api_key="your_api_key")

# Process a video
result = processor.process_video("your_video_name")
```

2. Process video with custom segments:
```python
# Process video with specific segments
video_processor = VideoProcessor()
result = video_processor.process_video(
    input_video="input.mp4",
    output_video="output.mp4"
)
```

## Project Structure 