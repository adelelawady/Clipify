import json

def format_timestamp(seconds):
    """
    Convert a float timestamp in seconds to SRT timestamp format (HH:MM:SS,ms).
    """
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def json_to_srt(json_file, output_srt):
    """
    Convert JSON file with transcript and word timings to SRT file format.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Validate the JSON structure
        if 'transcript' not in data or 'word_timings' not in data:
            raise ValueError("JSON file must contain 'transcript' and 'word_timings' keys.")

        word_timings = data['word_timings']
        transcript = data['transcript']

        # Create SRT content
        srt_content = ""
        for i, word_data in enumerate(word_timings, start=1):
            start_time = format_timestamp(word_data['start'])
            end_time = format_timestamp(word_data['end'])
            word = word_data['word']

            srt_content += f"{i}\n{start_time} --> {end_time}\n{word}\n\n"

        # Save to SRT file
        with open(output_srt, 'w', encoding='utf-8') as file:
            file.write(srt_content)

        print(f"SRT file successfully created: {output_srt}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Input and output file paths
input_json = "transcripts/The True Meaning Of Life (Animated Cinematic)_timings.json"  # Replace with your JSON file name
output_srt = "output.srt"

json_to_srt(input_json, output_srt)
