from moviepy.editor import VideoFileClip
import cv2
import numpy as np
import os

class VideoConverter:
    def __init__(self):
        self.supported_ratios = ["1:1", "4:5", "9:16"]

    def blur_frame(self, image, blur_amount=30):
        """Apply Gaussian blur to an image"""
        return cv2.GaussianBlur(image, (blur_amount * 2 + 1, blur_amount * 2 + 1), 0)

    def convert_to_mobile(self, input_video, output_video, target_ratio="9:16"):
        """
        Convert video to mobile-friendly format with blurred background
        
        Args:
            input_video (str): Path to input video
            output_video (str): Path to save converted video
            target_ratio (str): Target aspect ratio (default: "9:16")
            
        Returns:
            bool: Success status
        """
        try:
            if target_ratio not in self.supported_ratios:
                raise ValueError(f"Unsupported ratio. Supported ratios: {self.supported_ratios}")

            clip = VideoFileClip(input_video)
            
            # Calculate target dimensions while maintaining aspect ratio
            target_w, target_h = map(int, target_ratio.split(":"))
            target_ratio_float = target_w / target_h
            
            # Calculate the dimensions for the final video
            if clip.w/clip.h > target_ratio_float:  # wider than target
                new_height = int(clip.h)
                new_width = int(new_height * target_ratio_float)
            else:  # taller than target
                new_width = int(clip.w)
                new_height = int(new_width / target_ratio_float)

            def process_frame(current_frame):
                # First, create a black canvas of the target size
                final_frame = np.zeros((new_height, new_width, 3), dtype=np.uint8)
                
                # Calculate the size for the square (1:1) main video
                # Use the smaller dimension to ensure it fits
                main_size = min(new_width, new_height)
                
                # Resize the current frame to 1:1 square
                main_frame = cv2.resize(current_frame, (main_size, main_size))
                
                # Create blurred background by scaling the frame to fill the target size
                background = cv2.resize(current_frame, (new_width, new_height))
                background = self.blur_frame(background)
                
                # Calculate the position to center the main video
                x_offset = (new_width - main_size) // 2
                y_offset = (new_height - main_size) // 2
                
                # Copy the blurred background
                final_frame[:] = background
                
                # Overlay the square main video in the center
                final_frame[y_offset:y_offset + main_size, 
                           x_offset:x_offset + main_size] = main_frame
                
                return final_frame

            # Create the final clip
            final = clip.fl_image(process_frame)
            final = final.set_duration(clip.duration)
            
            # Write output
            final.write_videofile(output_video)
            
            # Clean up
            clip.close()
            final.close()
            
            return True
            
        except Exception as e:
            print(f"Error converting video: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert video to mobile-friendly format')
    parser.add_argument('input_video', help='Path to input video file')
    parser.add_argument('--output', help='Path to output video file (optional)')
    parser.add_argument('--ratio', help='Target aspect ratio (default: 9:16)', default='9:16')
    
    args = parser.parse_args()
    
    converter = VideoConverter()
    result = converter.convert_to_mobile(args.input_video, args.output, args.ratio)
    
    if result:
        print(f"Video successfully converted. Output saved to: {args.output or args.input_video}")
    else:
        print("Video conversion failed.") 