from moviepy.editor import VideoFileClip
import os

class VideoConverterStretch:
    def __init__(self):
        self.supported_ratios = ["1:1", "4:5", "9:16"]

    def convert_to_mobile(self, input_video, output_video, target_ratio="9:16"):
        """
        Convert video to mobile-friendly format
        
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
            
            # Calculate new dimensions
            target_w, target_h = map(int, target_ratio.split(":"))
            ratio = target_w / target_h
            
            if ratio < 1:  # vertical video
                new_height = clip.w
                new_width = int(new_height * ratio)
            else:  # horizontal video
                new_width = clip.h
                new_height = int(new_width / ratio)
            
            # Resize and crop video
            resized = clip.resize(width=new_width, height=new_height)
            final = resized.crop(x_center=resized.w/2, y_center=resized.h/2, 
                               width=new_width, height=new_height)
            
            # Write output
            final.write_videofile(output_video)
            
            # Clean up
            clip.close()
            resized.close()
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