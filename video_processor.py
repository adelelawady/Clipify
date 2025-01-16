import os
import json
import wave
import subprocess
from vosk import Model, KaldiRecognizer
import shlex

class VideoProcessor:
    def __init__(self, input_folder="segmented_videos", model_path="vosk-model-small-en-us"):
        self.input_folder = input_folder
        # Initialize Vosk model
        if not os.path.exists(model_path):
            raise RuntimeError(f"Please download the Vosk model and place it in {model_path}")
        self.model = Model(model_path)
    
    def sanitize_filename(self, filename):
        """Sanitize filename for ffmpeg"""
        return filename.replace("'", "'\\''")
    
    def extract_audio(self, video_path):
        """Extract audio from video file using ffmpeg"""
        audio_path = video_path.rsplit('.', 1)[0] + '_audio.wav'
        
        # Convert Windows paths to ffmpeg-compatible paths
        safe_video_path = video_path.replace('\\', '/')
        safe_audio_path = audio_path.replace('\\', '/')
        
        command = f'ffmpeg -i "{safe_video_path}" -acodec pcm_s16le -ar 16000 -ac 1 -y "{safe_audio_path}"'
        
        try:
            print("Executing command:", command)
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e}")
            print(f"Command output: {e.output}")
            print(f"Command stderr: {e.stderr}")
            return None

    def speech_to_text(self, audio_path):
        """Convert speech to text using Vosk with word timings"""
        try:
            wf = wave.open(audio_path, "rb")
            
            # Create recognizer
            rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)
            
            # Process audio file
            text = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result and result['text'].strip():
                        text.append(result['text'])
            
            # Get final result
            result = json.loads(rec.FinalResult())
            if 'text' in result and result['text'].strip():
                text.append(result['text'])
            
            return ' '.join(text)
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return ""
        finally:
            if 'wf' in locals():
                wf.close()

    def add_subtitles(self, video_path, text):
        """Add subtitles to video using ffmpeg drawtext filter"""
        output_path = os.path.join(
            "processed_videos",
            f"subtitled_{os.path.basename(video_path)}"
        )
        
        # Create output directory if it doesn't exist
        os.makedirs("processed_videos", exist_ok=True)
        
        # Get video duration using ffprobe
        duration_cmd = (
            f'ffprobe -v error -show_entries format=duration '
            f'-of default=noprint_wrappers=1:nokey=1 "{video_path}"'
        )
        try:
            duration = float(subprocess.check_output(duration_cmd, shell=True))
        except:
            print("Error getting video duration")
            return None

        # Split text into segments (roughly 10 words per segment)
        words = text.split()
        segments = []
        segment_size = 10
        for i in range(0, len(words), segment_size):
            segment = ' '.join(words[i:i + segment_size])
            segments.append(segment)

        # Calculate time per segment
        time_per_segment = duration / len(segments)
        
        # Create a temporary subtitle file in ASS format
        ass_path = video_path.rsplit('.', 1)[0] + '.ass'
        with open(ass_path, 'w', encoding='utf-8') as f:
            # Write ASS header
            f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\n\n")
            f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write("Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,50,1\n\n")
            f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            # Write each segment with proper timing
            for i, segment in enumerate(segments):
                start_time = i * time_per_segment
                end_time = (i + 1) * time_per_segment
                
                # Convert times to ASS format (h:mm:ss.cc)
                start_str = f"{int(start_time/3600):01d}:{int(start_time/60)%60:02d}:{int(start_time%60):02d}.{int((start_time%1)*100):02d}"
                end_str = f"{int(end_time/3600):01d}:{int(end_time/60)%60:02d}:{int(end_time%60):02d}.{int((end_time%1)*100):02d}"
                
                # Escape commas in text for ASS format
                escaped_text = segment.replace(',', '\\,')
                
                # Write the line
                f.write(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{escaped_text}\n")
        
        # Convert Windows paths to ffmpeg-compatible paths
        safe_video_path = video_path.replace('\\', '/')
        safe_ass_path = ass_path.replace('\\', '/')
        safe_output_path = output_path.replace('\\', '/')
        
        # Construct ffmpeg command using ASS subtitles
        command = (
            f'ffmpeg -i "{safe_video_path}" '
            f'-vf "ass={safe_ass_path}" '
            f'-c:a copy -y "{safe_output_path}"'
        )
        
        try:
            # Print command for debugging
            print("Executing command:", command)
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error adding subtitles: {e}")
            print(f"Command output: {e.output}")
            print(f"Command stderr: {e.stderr}")
            return None
        finally:
            # Clean up temporary ASS file
            if os.path.exists(ass_path):
                os.remove(ass_path)

    def process_videos(self):
        """Process all videos in the input folder"""
        if not os.path.exists(self.input_folder):
            print(f"Input folder {self.input_folder} does not exist!")
            return
            
        for video_file in os.listdir(self.input_folder):
            if video_file.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(self.input_folder, video_file)
                print(f"Processing {video_file}...")
                
                # Extract audio
                audio_path = self.extract_audio(video_path)
                if not audio_path:
                    continue
                
                # Convert speech to text
                text = self.speech_to_text(audio_path)
                
                if text:
                    # Add subtitles to video
                    output_path = self.add_subtitles(video_path, text)
                    if output_path:
                        print(f"Processed video saved to: {output_path}")
                else:
                    print(f"No text could be extracted from {video_file}")
                
                # Clean up temporary audio file
                if os.path.exists(audio_path):
                    os.remove(audio_path)

if __name__ == "__main__":
    processor = VideoProcessor()
    processor.process_videos() 