import ffmpeg
import json
import os
from pathlib import Path

class VideoSegmenter:
    def __init__(self, processed_json_path, video_path):
        """
        Initialize the video segmenter
        :param processed_json_path: Path to the processed JSON file with segment information
        :param video_path: Path to the source video file
        """
        self.processed_data = self.load_json(processed_json_path)
        self.video_path = video_path
        self.output_dir = "segmented_videos"
        self.target_duration = 60  # Target duration in seconds
        os.makedirs(self.output_dir, exist_ok=True)

    def load_json(self, json_path):
        """Load and parse the processed JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return None

    def calculate_segment_timing(self, word_timings):
        """
        Calculate accurate segment timings from word timings
        :param word_timings: List of word timing dictionaries
        :return: tuple of (start_time, end_time)
        """
        if not word_timings:
            return None, None
            
        # Sort timings by start time to ensure correct order
        sorted_timings = sorted(word_timings, key=lambda x: float(x['start']))
        
        # Get first and last word timings
        start_time = float(sorted_timings[0]['start'])
        end_time = float(sorted_timings[-1]['end'])
        
        return start_time, end_time

    def cut_segment(self, segment_index):
        """
        Cut a specific segment from the video using ffmpeg
        :param segment_index: Index of the segment to cut (0-based)
        :return: Path to the cut video segment
        """
        try:
            # Validate segment index
            if not self.processed_data or 'segments' not in self.processed_data:
                raise ValueError("Invalid processed data format")

            segments = self.processed_data['segments']
            if segment_index < 0 or segment_index >= len(segments):
                raise ValueError(f"Invalid segment index: {segment_index}")

            # Get segment information
            segment = segments[segment_index]
            if 'word_timings' not in segment:
                raise ValueError("Segment missing word timing information")

            # Calculate timing from word_timings
            start_time, end_time = self.calculate_segment_timing(segment['word_timings'])
            
            if start_time is None or end_time is None:
                raise ValueError("Could not determine segment timing from word timings")

            duration = end_time - start_time

            # Generate output filename
            clean_title = "".join(c for c in segment['title'] if c.isalnum() or c.isspace()).rstrip()
            output_filename = f"segment_{segment_index + 1}_{clean_title}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)

            print(f"\nProcessing segment {segment_index + 1}: {clean_title}")
            print(f"Start time: {start_time:.2f}s")
            print(f"End time: {end_time:.2f}s")
            print(f"Duration: {duration:.2f}s")

            try:
                # Cut the segment using ffmpeg
                stream = ffmpeg.input(self.video_path, ss=start_time, t=duration)
                stream = ffmpeg.output(stream, output_path, 
                                    acodec='aac', 
                                    vcodec='h264',
                                    video_bitrate='2000k',
                                    audio_bitrate='128k')
                
                # Run ffmpeg command
                ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
                
                print(f"Segment saved to: {output_path}")
                return output_path

            except ffmpeg.Error as e:
                print(f"FFmpeg error: {e.stderr.decode()}")
                return None

        except Exception as e:
            print(f"Error cutting segment: {e}")
            return None

    def process_video(self):
        """Process the entire video into segments"""
        if not self.processed_data or 'segments' not in self.processed_data:
            print("No segments found in processed data")
            return []

        # Cut each segment
        output_paths = []
        for i in range(len(self.processed_data['segments'])):
            output_path = self.cut_segment(i)
            if output_path:
                output_paths.append(output_path)

        return output_paths

def main():
    # Example usage
    video_name = "The True Meaning Of Life (Animated Cinematic)"
    processed_json_path = Path("processed_content") / f"{video_name}_processed.json"
    video_path = Path(f"{video_name}.mp4")
    
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        return
        
    if not processed_json_path.exists():
        print(f"Error: Processed JSON file not found: {processed_json_path}")
        return
    
    # Create video segmenter
    segmenter = VideoSegmenter(processed_json_path, video_path)
    
    # Process the video into segments
    output_paths = segmenter.process_video()
    print(f"\nCreated {len(output_paths)} segments successfully")

if __name__ == "__main__":
    main()