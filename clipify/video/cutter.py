from moviepy.editor import VideoFileClip
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoCutter:
    def __init__(self):
        """Initialize the video cutter"""
        pass

    def cut_video(self, input_video: str, output_video: str, start_time: float, end_time: float) -> bool:
        """
        Cut video segment between start and end times
        
        Args:
            input_video (str): Path to input video
            output_video (str): Path to save cut video
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            bool: Success status
        """
        try:
            # Validate inputs
            if not os.path.exists(input_video):
                raise FileNotFoundError(f"Input video not found: {input_video}")
                
            if start_time >= end_time:
                raise ValueError("Start time must be less than end time")
            
            # Load video and cut segment
            video = VideoFileClip(input_video)
            
            if end_time > video.duration:
                end_time = video.duration
                
            segment = video.subclip(start_time, end_time)
            
            # Write output
            segment.write_videofile(output_video)
            
            # Clean up
            video.close()
            segment.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error cutting video: {e}")
            return False

    def cut_segments(self, input_video: str, segments: list, output_dir: str) -> list:
        """
        Cut multiple segments from a video file
        
        Args:
            input_video: Path to input video file
            segments: List of dictionaries containing 'start_time' and 'end_time'
            output_dir: Directory to save cut segments
            
        Returns:
            List of paths to cut video segments
        """
        cut_segments = []
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, segment in enumerate(segments, 1):
            try:
                # Clean filename by removing invalid characters
                clean_title = "".join(c for c in segment['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_path = os.path.join(
                    output_dir,
                    f"segment_{i}_{clean_title}.mp4"
                )
                
                # Get timing information
                start_time = segment.get('start_time')
                end_time = segment.get('end_time')
                
                # Skip segments without valid timing information
                if start_time is None or end_time is None:
                    print(f"Skipping segment {i}: {clean_title} - No valid timing information")
                    continue
                
                # Convert to float and validate
                start_time = float(start_time)
                end_time = float(end_time)
                
                if start_time >= end_time:
                    print(f"Skipping segment {i}: {clean_title} - Invalid time range")
                    continue
                
                logger.info(f"\nProcessing segment {i}: {clean_title}")
                logger.info(f"Time range: {start_time:.2f}s - {end_time:.2f}s")
                
                result = self.cut_video(
                    input_video=input_video,
                    output_video=output_path,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if result:
                    cut_segments.append(output_path)
                    
            except Exception as e:
                logger.error(f"Error processing segment {i}: {str(e)}", exc_info=True)
                continue
                
        return cut_segments

def main():
    """Test the video cutter"""
    cutter = VideoCutter()
    
    # Test cutting a single segment
    result = cutter.cut_video(
        input_video="test_video.mp4",
        output_video="test_segment.mp4",
        start_time=0,
        end_time=10
    )
    
    if result:
        print(f"Successfully cut video segment: {result}")

if __name__ == "__main__":
    main()