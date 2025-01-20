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

    def cut_video(self, input_video: str, output_video: str, start_time: float, end_time: float) -> str:
        """
        Cut a segment from a video file
        
        Args:
            input_video: Path to input video file
            output_video: Path to save output video segment
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Path to the cut video segment
        """
        try:
            # Ensure input video exists
            if not os.path.exists(input_video):
                logger.error(f"Input video not found: {input_video}")
                return None

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_video)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)

            logger.info(f"Cutting video segment from {start_time}s to {end_time}s")
            logger.info(f"Input: {input_video}")
            logger.info(f"Output: {output_video}")

            # Load video
            with VideoFileClip(input_video) as video:
                # Validate times
                if start_time >= video.duration or end_time > video.duration:
                    logger.error(f"Invalid time range: video duration is {video.duration}s")
                    return None
                
                if end_time <= start_time:
                    logger.error(f"Invalid time range: end_time ({end_time}) must be greater than start_time ({start_time})")
                    return None

                # Cut the segment
                video_segment = video.subclip(start_time, end_time)
                
                # Write the segment
                video_segment.write_videofile(
                    output_video,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    logger=None  # Suppress moviepy progress bars
                )

            if os.path.exists(output_video):
                logger.info(f"Successfully created video segment: {output_video}")
                return output_video
            else:
                logger.error("Failed to create video segment")
                return None

        except Exception as e:
            logger.error(f"Error cutting video: {str(e)}", exc_info=True)
            return None

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
                start_time = float(segment.get('start_time', 0))
                end_time = float(segment.get('end_time', 0))
                
                logger.info(f"\nProcessing segment {i}: {clean_title}")
                logger.info(f"Time range: {start_time:.2f}s - {end_time:.2f}s")
                
                result = self.cut_video(
                    input_video=input_video,
                    output_video=output_path,
                    start_time=start_time,
                    end_time=end_time
                )
                
                if result:
                    cut_segments.append(result)
                    
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