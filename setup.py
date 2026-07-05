from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements separately
requirements = [
    "captacity_clipify==0.3.4",
    "moviepy==1.0.3",
    "numpy==1.26.4",
    "openai==1.61.0",
    "requests==2.31.0",
    "openai-whisper==20231117",
    "google-generativeai",
    "gradio",
    "python-dotenv",
    "rapidfuzz",
]

setup(
    name="clipify",
    version="2.1.4",
    author="Diego Colucci",
    author_email="",
    description="AI-powered video highlights generator with burned-in captions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diegomcolucci/Clipify",
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