from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements separately
requirements = [
    "captacity_clipify==0.3.4",
    "opencv-python==4.8.0.74",
    "moviepy==1.0.3",
    "numpy==1.24.3",
    "openai==1.61.0",
    "pydub==0.25.1",
    "requests==2.31.0",
    "setuptools==49.2.1",
    "textblob==0.17.1",
    "openai-whisper==20231117",
]

setup(
    name="clipify",
    version="2.1.2",
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