import warnings

# Suppress specific Whisper warning about torch.load
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="whisper",
    message="You are using `torch.load` with `weights_only=False`.*"
)
# Suppress MoviePy warning about bytes reading
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="moviepy.video.io.ffmpeg_reader",
    message="Warning: in file.*bytes wanted but 0 bytes read.*"
)

__version__ = "0.1.0"