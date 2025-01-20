from moviepy.editor import VideoFileClip
import os

def convert_to_mobile_format(input_video_path, output_path=None):
    """
    Convert video to mobile-friendly 16:9 aspect ratio
    
    Args:
        input_video_path (str): Path to input video file
        output_path (str): Path for output video file (optional)
    
    Returns:
        str: Path to the converted video file
    """
    try:
        # Load the video
        video = VideoFileClip(input_video_path)
        
        # Calculate target dimensions for 16:9 aspect ratio
        target_width = 1080  # Standard mobile width
        target_height = 1920  # 16:9 aspect ratio height
        
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
        
        # Calculate cropping dimensions to achieve 16:9
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
        
        return output_path
        
    except Exception as e:
        print(f"Error converting video: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert video to mobile-friendly 16:9 format')
    parser.add_argument('input_video', help='Path to input video file')
    parser.add_argument('--output', help='Path to output video file (optional)')
    
    args = parser.parse_args()
    
    result = convert_to_mobile_format(args.input_video, args.output)
    
    if result:
        print(f"Video successfully converted. Output saved to: {result}")
    else:
        print("Video conversion failed.") 