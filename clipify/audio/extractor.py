from pydub import AudioSegment
import os
from shutil import which

class AudioExtractor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
        # Set ffmpeg path
        self.setup_ffmpeg()

    def setup_ffmpeg(self):
        """Setup ffmpeg path"""
        ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg')
        if os.path.exists(ffmpeg_path):
            os.environ["PATH"] += os.pathsep + ffmpeg_path
        
        # Verify ffmpeg is available
        if not which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg not found. Please ensure ffmpeg is installed and in PATH"
            )

    def extract_audio(self, video_path, output_path=None):
        """
        Extract audio from video file
        :param video_path: Path to input video file
        :param output_path: Path to save extracted audio (optional)
        :return: Path to extracted audio file
        """
        try:
            print(f"Attempting to extract audio from: {video_path}")
            # Validate video format
            if not any(video_path.lower().endswith(fmt) for fmt in self.supported_formats):
                raise ValueError(f"Unsupported video format. Supported formats: {self.supported_formats}")

            # Validate video exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Generate output path if not provided
            if output_path is None:
                output_path = os.path.splitext(video_path)[0] + '.wav'

            print(f"Extracting audio to: {output_path}")
            # Extract audio using pydub
            audio = AudioSegment.from_file(video_path)
            
            # Convert to mono and set sample width to 2 (16-bit) for Whisper compatibility
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)
            
            # Export as WAV
            audio.export(output_path, format='wav')
            
            if not os.path.exists(output_path):
                raise Exception(f"Failed to create output file: {output_path}")
            
            print(f"Successfully extracted audio to: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None 