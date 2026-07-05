import os
import shutil
from captacity_clipify import add_captions
from typing import Optional, Dict, Any, List

class VideoProcessor:
    def __init__(self, 
                 # Trending bold display font suitable for short-form captions
                 font: str = "Bangers-Regular.ttf",
                 # Larger default for mobile short-form: 80 is a good baseline on 1080x1920
                 font_size: int = 60,
                 # On-screen text color (white with dark stroke is highly legible)
                 font_color: str = "white",
                 # Slightly thicker stroke for better contrast on mobile
                 stroke_width: int = 3,
                 stroke_color: str = "#111111",
                 highlight_current_word: bool = True,
                 word_highlight_color: str = "#FFCC00",  # trending accent (yellow/gold)
                 shadow_strength: float = 0.8,
                 shadow_blur: float = 0.08,
                 line_count: int = 1,
                 fit_function: Optional[callable] = None,
                 padding: int = 50,
                 position: str = "bottom",
                 print_info: bool = False,
                 initial_prompt: Optional[str] = None,
                 words_per_caption: Optional[int] = None):
        """
        Initialize the video processor with caption styling options

        Args:
            font (str): Path to font file (default: "Bangers-Regular.ttf")
            font_size (int): Size of the caption font (default: 60)
            font_color (str): Color of the caption text (default: "white")
            stroke_width (int): Width of the text outline (default: 2)
            stroke_color (str): Color of the text outline (default: "black")
            highlight_current_word (bool): Whether to highlight the current word (default: True)
            word_highlight_color (str): Color for word highlighting (default: "red")
            shadow_strength (float): Strength of the text shadow (0.0-1.0) (default: 0.8)
            shadow_blur (float): Blur amount of the text shadow (0.0-1.0) (default: 0.08)
            line_count (int): Maximum number of lines per caption (default: 1)
            fit_function (callable): Optional custom function for text fitting
            padding (int): Padding around the captions in pixels (default: 50)
            position (str): Position of captions ("bottom", "top", or "center") (default: "bottom")
            print_info (bool): Whether to print processing info (default: False)
            initial_prompt (str): Initial prompt for whisper transcription
            words_per_caption (int): Optional maximum number of words per caption (default: None)
        """
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_width = stroke_width 
        self.stroke_color = stroke_color
        self.highlight_current_word = highlight_current_word
        self.word_highlight_color = word_highlight_color
        self.shadow_strength = shadow_strength
        self.shadow_blur = shadow_blur
        self.line_count = line_count
        self.fit_function = fit_function
        self.padding = padding
        self.position = position
        self.print_info = print_info
        self.initial_prompt = initial_prompt
        self.words_per_caption = words_per_caption

    def process_video(self,
                     input_video: str,
                     output_video: str,
                     custom_segments: Optional[Dict[str, Any]] = None,
                     use_local_whisper: str = "auto") -> bool:
        """
        Process a video file by adding captions using Captacity
        
        Args:
            input_video: Path to input video file
            output_video: Path to save output video with captions
            custom_segments: Optional custom whisper segments to use
            use_local_whisper: Whether to use local whisper ("auto", True, or False)
            
        Returns:
            True if processing is successful, False otherwise
        """
        try:
            # Ensure input video exists
            if not os.path.exists(input_video):
                raise FileNotFoundError(f"Input video not found: {input_video}")

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_video)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Pre-check captioning dependencies and provide clearer errors if missing
            def _check_caption_deps() -> List[str]:
                missing = []
                # ImageMagick: either 'convert' (legacy) or 'magick'
                if not (shutil.which('convert') or shutil.which('magick')):
                    missing.append('ImageMagick (convert or magick)')
                # ffmpeg is also required
                if not shutil.which('ffmpeg'):
                    missing.append('ffmpeg')
                return missing

            missing_deps = _check_caption_deps()
            if missing_deps:
                # Raise to allow caller to fallback to ffmpeg-based burning
                raise RuntimeError(f"Missing caption dependencies: {', '.join(missing_deps)}")

            # Add captions to video using Captacity
            # Build a fit function that respects the requested words-per-caption limit
            fit_func = self.fit_function
            if self.words_per_caption:
                from captacity_clipify import fits_frame, get_font_path
                try:
                    import subprocess
                    width_cmd = [
                        "ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width",
                        "-of", "csv=s=x:p=0", input_video
                    ]
                    frame_width = int(subprocess.check_output(width_cmd, stderr=subprocess.DEVNULL).decode().strip())
                except Exception:
                    frame_width = 1080
                text_bbox_width = max(100, frame_width - self.padding * 2)
                base_fit = fit_func if fit_func else fits_frame(
                    self.line_count,
                    get_font_path(self.font),
                    self.font_size,
                    self.stroke_width,
                    text_bbox_width,
                )
                max_words = self.words_per_caption
                def fit_func(text):
                    if len(text.split()) > max_words:
                        return False
                    return base_fit(text)

            add_captions(
                video_file=input_video,
                output_file=output_video,
                
                # Caption styling
                font=self.font,
                font_size=self.font_size,
                font_color=self.font_color,
                stroke_width=self.stroke_width,
                stroke_color=self.stroke_color,
                highlight_current_word=self.highlight_current_word,
                word_highlight_color=self.word_highlight_color,
                shadow_strength=self.shadow_strength, 
                shadow_blur=self.shadow_blur,
                line_count=self.line_count,
                fit_function=fit_func,
                padding=self.padding,
                position=self.position,
                
                # Processing options
                print_info=self.print_info,
                initial_prompt=self.initial_prompt,
                segments=custom_segments if custom_segments else None,
                use_local_whisper=use_local_whisper
            )

            return True

        except Exception as e:
            print(f"Error processing video: {e}")
            return False

    def process_video_segments(self,
                             segment_files: list[str],
                             output_dir: str,
                             custom_segments: Optional[Dict[str, Any]] = None) -> list[str]:
        """
        Process multiple video segments by adding captions
        
        Args:
            segment_files: List of paths to video segment files
            output_dir: Directory to save processed segments
            custom_segments: Optional custom whisper segments to use
            
        Returns:
            List of paths to processed video segments
        """
        processed_segments = []

        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Process each segment
        for i, segment in enumerate(segment_files):
            output_file = os.path.join(
                output_dir,
                f"segment_{i}_captioned{os.path.splitext(segment)[1]}"
            )
            
            processed_file = self.process_video(
                input_video=segment,
                output_video=output_file,
                custom_segments=custom_segments
            )
            
            processed_segments.append(processed_file)

        return processed_segments

def main():
    """Example usage"""
    processor = VideoProcessor(
        font_size=60,
        font_color="white",
        stroke_width=2,
        stroke_color="black",
        shadow_strength=0.8,
        shadow_blur=0.08,
        line_count=1,
        padding=50,
        position="bottom"
    )

    # Process single video
    processor.process_video(
        input_video="segment_10_Youre Not Alone The Struggle and the Hope.mp4",
        output_video="segment_10_Youre Not Alone The Struggle and the Hope_captioned.mp4"
    )

if __name__ == "__main__":
    main()
