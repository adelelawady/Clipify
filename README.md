<p align="center"> <img src="https://github.com/user-attachments/assets/876170d2-523c-4045-b4c9-67ac957e46c1" alt="Clipify Logo" width="150"> </p>

# Clipify

> AI-powered video highlights generator with burned-in captions, optimized for short-form content.

## Features

- Upload a video and get AI-selected highlight clips
- Automatic transcription with Whisper
- Customizable captions (font, size, colors, position, words per caption)
- Audio loudness normalization
- Gradio web UI for easy use

## Requirements

- Python 3.11
- ffmpeg
- ImageMagick (`magick`)
- macOS, Linux or Windows (WSL recommended)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/diegomcolucci/Clipify.git
cd Clipify

# 2. Create virtual environment
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY or OPENAI_API_KEY

# 4. Run the Gradio UI
./scripts/run_gradio.sh
```

Open `http://127.0.0.1:7860` in your browser.

## ImageMagick on macOS

If `magick` is not available, install via Miniforge:

```bash
curl -L -o miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash miniforge.sh -b -p $HOME/miniforge3
$HOME/miniforge3/bin/conda install -y -c conda-forge imagemagick
```

## Project Structure

```
Clipify/
├── clipify/
│   ├── core/ai_providers.py      # AI provider factory
│   ├── pipelines/
│   │   ├── gemini_pipeline.py    # transcription, AI highlights, alignment, SRTs
│   │   ├── ui_helpers.py         # ffmpeg cut/burn helpers + whisper transcription
│   │   ├── ass_style.py          # ASS subtitle style utilities
│   │   └── srt_validator.py      # SRT timing validation
│   └── video/processor.py        # captioning wrapper (captacity)
├── ui/
│   ├── app_gradio.py             # Gradio web interface
│   └── style_preview.py          # subtitle style preview
├── scripts/run_gradio.sh         # launcher
├── requirements.txt
└── setup.py
```

## License

MIT