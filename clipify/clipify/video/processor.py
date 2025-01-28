import os
from captacity_clipify import add_captions
from typing import Optional, Dict, Any

class VideoProcessor:
    def __init__(self, 
                 font_size: int = 60,
                 font_color: str = "white",
                 stroke_width: int = 2,
                 stroke_color: str = "black",
                 shadow_strength: float = 0.8,
                 shadow_blur: float = 0.08,
                 line_count: int = 1,
                 padding: int = 50,
                 position: str = "bottom"):
        """
        Initialize the video processor with caption styling options

        Args:
            font_size (int): Size of the caption font (default: 60)
            font_color (str): Color of the caption text (default: "white")
            stroke_width (int): Width of the text outline (default: 2)
            stroke_color (str): Color of the text outline (default: "black")
            shadow_strength (float): Strength of the text shadow (0.0-1.0) (default: 0.8)
            shadow_blur (float): Blur amount of the text shadow (0.0-1.0) (default: 0.08)
            line_count (int): Maximum number of lines per caption (default: 1)
            padding (int): Padding around the captions in pixels (default: 50)
            position (str): Position of captions ("bottom", "top", or "center") (default: "bottom")
        """
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_width = stroke_width 
        self.stroke_color = stroke_color
        self.shadow_strength = shadow_strength
        self.shadow_blur = shadow_blur
        self.line_count = line_count
        self.padding = padding
        self.position = position

    def process_video(self,
                     input_video: str,
                     output_video: str,
                     custom_segments: Optional[Dict[str, Any]] = None) -> bool:
        """
        Process a video file by adding captions using Captacity
        
        Args:
            input_video: Path to input video file
            output_video: Path to save output video with captions
            custom_segments: Optional custom whisper segments to use
            
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

            # Add captions to video using Captacity
            add_captions(
                video_file=input_video,
                output_file=output_video,
                
                # Caption styling
                font_size=self.font_size,
                font_color=self.font_color,
                stroke_width=self.stroke_width,
                stroke_color=self.stroke_color,
                shadow_strength=self.shadow_strength, 
                shadow_blur=self.shadow_blur,
                line_count=self.line_count,
                padding=self.padding,
                position=self.position,
                
                # Optional custom segments
                segments=custom_segments if custom_segments else None,
                
                # Use local whisper if available
                use_local_whisper=True
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
