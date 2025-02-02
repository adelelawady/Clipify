from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements separately
requirements = [
    "numpy==1.24.3",
    "Pillow==10.0.0",
    "requests==2.31.0",
    
    # Video processing
    "moviepy==1.0.3",
    "opencv-python==4.8.0.74",
    "ffmpeg-python==0.2.0",
    "imageio==2.31.1",
    "imageio-ffmpeg==0.4.8",
    
    # Audio processing
    "pydub==0.25.1",
    "openai-whisper==20231117",
    
    # ML/AI dependencies
    "torch==2.6.0",
    "torchaudio==2.6.0",
    "torchvision==0.21.0",
    "textblob==0.17.1",
    
    # Captioning
    "captacity-clipify==0.3.4",
]

setup(
    name="clipify",
    version="2.0.3",
    author="Adel Elawady",
    author_email="adel50ali50@gmail.com",
    description="A powerful tool for processing video content into social media-friendly segments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adelelawady/clipify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
) 