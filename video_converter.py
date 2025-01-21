from moviepy.editor import VideoFileClip
import os

class VideoConverter:
    def convert_to_mobile(self, input_video_path, output_path=None, target_ratio="6:19"):
        """
        Convert video to mobile-friendly format with specified aspect ratio
        
        Args:
            input_video_path (str): Path to input video file
            output_path (str): Path for output video file (optional)
            target_ratio (str): Target aspect ratio (default "6:19")
        
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Parse target ratio
            width_ratio, height_ratio = map(int, target_ratio.split(':'))
            
            # Load the video
            video = VideoFileClip(input_video_path)
            
            # Calculate target dimensions
            target_width = 1080  # Standard mobile width
            target_height = int((target_width * height_ratio) / width_ratio)
            
            # Get original dimensions
            original_width = video.w
            original_height = video.h
            
            # Calculate scaling factors
            width_scale = target_width / original_width
            height_scale = target_height / original_height
            
            # Use the larger scaling factor to ensure the video fills the frame
            scale_factor = max(width_scale, height_scale)
            
            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Resize video
            resized_video = video.resize((new_width, new_height))
            
            # Calculate cropping dimensions
            x_center = new_width / 2
            y_center = new_height / 2
            
            # Crop to target dimensions
            final_video = resized_video.crop(
                x1=x_center - (target_width / 2),
                y1=y_center - (target_height / 2),
                x2=x_center + (target_width / 2),
                y2=y_center + (target_height / 2)
            )
            
            # Generate output path if not provided
            if output_path is None:
                filename, ext = os.path.splitext(input_video_path)
                output_path = f"{filename}_mobile{ext}"
            
            # Write the final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30
            )
            
            # Close the video files
            video.close()
            resized_video.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            print(f"Error converting video: {str(e)}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert video to mobile-friendly format')
    parser.add_argument('input_video', help='Path to input video file')
    parser.add_argument('--output', help='Path to output video file (optional)')
    parser.add_argument('--ratio', help='Target aspect ratio (default: 6:19)', default='6:19')
    
    args = parser.parse_args()
    
    converter = VideoConverter()
    result = converter.convert_to_mobile(args.input_video, args.output, args.ratio)
    
    if result:
        print(f"Video successfully converted. Output saved to: {args.output or args.input_video}")
    else:
        print("Video conversion failed.") 