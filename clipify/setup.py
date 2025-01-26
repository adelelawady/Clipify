from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements separately
requirements = [
    "numpy>=1.19.0",
    "moviepy>=1.0.3",
    "pydub>=0.25.1",
    "nltk>=3.6.0",
    "textblob>=0.15.3",
    "whisper>=1.0.0",
    "requests>=2.25.1",
    "ffmpeg-python>=0.2.0",
    "SpeechRecognition>=3.8.1",
    "vosk>=0.3.32",
    "transformers>=4.5.0",
    "torch>=1.8.0",
    "torchaudio>=0.8.0",
    "tqdm>=4.60.0",
    "python-dotenv>=0.17.0",
    "typing-extensions>=3.7.4",
    "pathlib>=1.0.1",
    "opencv-python>=4.5.0",
    "scipy>=1.6.0",
]

setup(
    name="clipify",
    version="0.8.0",
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