import requests
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import time
import json

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class SmartTextProcessor:
    def __init__(self, api_key):
        self.url = "https://api.hyperbolic.xyz/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.cache = {}
        
        # Constants for chunk sizing
        self.WORDS_PER_MINUTE = 150  # Average speaking rate
        self.TARGET_CHUNK_SIZE = self.WORDS_PER_MINUTE  # Words per chunk (1 minute)
        self.MAX_CHUNK_SIZE = int(self.TARGET_CHUNK_SIZE * 1.2)  # Allow 20% overflow
        self.MIN_CHUNK_SIZE = int(self.TARGET_CHUNK_SIZE * 0.8)  # Allow 20% underflow
        
        # Add new constants for thematic segmentation
        self.MIN_SEGMENT_LENGTH = 50  # Minimum characters per segment
        self.MAX_SEGMENT_LENGTH = 1000  # Maximum characters per segment
    
    def get_ai_response(self, prompt, retry_count=3):
        """Get AI response with retry mechanism and caching"""
        if prompt in self.cache:
            return self.cache[prompt]
            
        for attempt in range(retry_count):
            try:
                data = {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "deepseek-ai/DeepSeek-V3",
                    "max_tokens": 5012,
                    "temperature": 0.7,  # Increased for more creative titles
                    "top_p": 0.9
                }
                
                response = requests.post(self.url, headers=self.headers, json=data)
                result = response.json()
                
                if 'choices' in result:
                    self.cache[prompt] = result
                    return result
                    
            except Exception as e:
                if attempt == retry_count - 1:
                    raise e
                time.sleep(1)  # Wait before retry
                
        return None

    def analyze_sentiment(self, text):
        """Analyze the sentiment of text to help with title generation"""
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def extract_keywords(self, text):
        """Extract important keywords from text"""
        stop_words = set(stopwords.words('english'))
        words = text.lower().split()
        keywords = [word for word in words if word.isalnum() and word not in stop_words]
        return list(set(keywords))[:5]  # Return top 5 unique keywords

    def generate_smart_title(self, text):
        """Generate a more contextual and engaging title"""
        sentiment = self.analyze_sentiment(text)
        keywords = self.extract_keywords(text)
        
        # Craft a more specific title prompt based on content analysis
        prompt_elements = [
            "Generate a catchy title that:",
            "- Captures the main topic: " + ", ".join(keywords),
            "- Matches the tone: " + ("positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"),
            "- Is attention-grabbing and social media friendly",
            "- Is no longer than 60 characters",
            f"For this text: {text[:200]}..."  # Send first 200 chars for context
        ]
        
        title_prompt = "\n".join(prompt_elements)
        title_response = self.get_ai_response(title_prompt)
        
        try:
            title = title_response['choices'][0]['message']['content'].strip()
            # Remove quotes if present
            title = title.strip('"\'')
            return title
        except:
            return self.generate_fallback_title(keywords)

    def generate_fallback_title(self, keywords):
        """Generate a simple title from keywords if AI generation fails"""
        return f"{''.join(keywords[:3]).title()}"

    def count_words(self, text):
        """Count words in text"""
        return len(text.split())
    
    def create_shorts(self, text):
        """Create approximately one-minute chunks of content using AI assistance"""
        # Initial split into sentences
        sentences = sent_tokenize(text)
        
        shorts = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_word_count = self.count_words(sentence)
            
            # If adding this sentence would exceed max chunk size and we have enough words
            if (current_word_count + sentence_word_count > self.MAX_CHUNK_SIZE and 
                current_word_count >= self.MIN_CHUNK_SIZE):
                
                # Create short from current chunk
                chunk_text = " ".join(current_chunk)
                
                # Use AI to optimize the chunk
                prompt = f"""
                Please optimize this text into a perfect one-minute short video script:
                
                Original text: {chunk_text}
                
                Requirements:
                1. Keep the main message and key points
                2. Make it engaging and natural to speak
                3. Aim for ~150 words (one minute of speech)
                4. Maintain coherent flow
                5. Start and end with strong hooks
                6. Keep it self-contained (make sense on its own)
                
                Return only the optimized script, no explanations.
                """
                print(prompt)
                response = self.get_ai_response(prompt)
                try:
                    optimized_text = response['choices'][0]['message']['content'].strip()
                except:
                    optimized_text = chunk_text
                
                # Generate title using another AI call
                title_prompt = f"""
                Create a catchy, engaging social media title for this one-minute video:
                
                Content: {optimized_text}
                
                Requirements:
                1. Maximum 60 characters
                2. Include emojis if appropriate
                3. Make it clickable but not clickbait
                4. Capture the main value proposition
                
                Return only the title, no explanations.
                """
                
                title_response = self.get_ai_response(title_prompt)
                try:
                    title = title_response['choices'][0]['message']['content'].strip()
                except:
                    title = self.generate_fallback_title(self.extract_keywords(optimized_text))
                
                # Calculate metrics for the optimized text
                word_count = self.count_words(optimized_text)
                
                shorts.append({
                    'title': title,
                    'content': optimized_text,
                    'length': len(optimized_text),
                    'word_count': word_count,
                    'estimated_duration': f"{word_count / self.WORDS_PER_MINUTE:.1f} minutes",
                    'sentiment': self.analyze_sentiment(optimized_text),
                    'keywords': self.extract_keywords(optimized_text),
                    'hook': optimized_text.split('.')[0] + '.'  # First sentence as hook
                })
                
                # Start new chunk
                current_chunk = [sentence]
                current_word_count = sentence_word_count
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_word_count
        
        # Handle the last chunk if it meets minimum size
        if current_chunk and current_word_count >= self.MIN_CHUNK_SIZE:
            chunk_text = " ".join(current_chunk)
            
            # Use AI to optimize the final chunk
            prompt = f"""
            Please optimize this text into a perfect one-minute short video script:
            
            Original text: {chunk_text}
            
            Requirements:
            1. Keep the main message and key points
            2. Make it engaging and natural to speak
            3. Aim for ~150 words (one minute of speech)
            4. Maintain coherent flow
            5. Start and end with strong hooks
            6. Keep it self-contained (make sense on its own)
            
            Return only the optimized script, no explanations.
            """
            
            response = self.get_ai_response(prompt)
            try:
                optimized_text = response['choices'][0]['message']['content'].strip()
            except:
                optimized_text = chunk_text
            
            # Generate title for final chunk
            title_prompt = f"""
            Create a catchy, engaging social media title for this one-minute video:
            
            Content: {optimized_text}
            
            Requirements:
            1. Maximum 60 characters
            2. Include emojis if appropriate
            3. Make it clickable but not clickbait
            4. Capture the main value proposition
            
            Return only the title, no explanations.
            """
            
            title_response = self.get_ai_response(title_prompt)
            try:
                title = title_response['choices'][0]['message']['content'].strip()
            except:
                title = self.generate_fallback_title(self.extract_keywords(optimized_text))
            
            word_count = self.count_words(optimized_text)
            
            shorts.append({
                'title': title,
                'content': optimized_text,
                'length': len(optimized_text),
                'word_count': word_count,
                'estimated_duration': f"{word_count / self.WORDS_PER_MINUTE:.1f} minutes",
                'sentiment': self.analyze_sentiment(optimized_text),
                'keywords': self.extract_keywords(optimized_text),
                'hook': optimized_text.split('.')[0] + '.'  # First sentence as hook
            })
        
        return shorts

    def segment_by_theme(self, text, word_timings=None):
        """Segment text by theme with timing information"""
        try:
            # Get initial segments
            segments = self.get_thematic_segments(text)
            
            if word_timings:
                # Track overall position in text
                processed_words = 0
                
                for segment in segments['segments']:
                    # Get word timings for this specific segment
                    segment_timings = self.get_segment_timings(
                        segment['content'], 
                        word_timings[processed_words:],  # Pass only remaining timings
                        start_pos=processed_words
                    )
                    
                    # Update segment with timing information
                    segment['start_time'] = segment_timings['start']
                    segment['end_time'] = segment_timings['end']
                    segment['word_timings'] = segment_timings['words']
                    
                    # Update processed words count
                    processed_words += len(segment['content'].split())
            
            return segments
            
        except Exception as e:
            print(f"Error in segment_by_theme: {str(e)}")
            return None

    def get_segment_timings(self, segment_text, word_timings, start_pos=0):
        """Extract timing information for a segment based on word timings"""
        try:
            segment_words = segment_text.split()
            segment_start = None
            segment_end = None
            segment_word_timings = []
            
            # Process only the words in this segment
            for i, word in enumerate(segment_words):
                if i < len(word_timings):
                    timing = word_timings[i]
                    segment_word_timings.append(timing)
                    
                    # Set start time if not set
                    if segment_start is None:
                        segment_start = float(timing['start'])
                    
                    # Update end time
                    segment_end = float(timing['end'])
            
            return {
                'start': segment_start,
                'end': segment_end,
                'words': segment_word_timings
            }
        except Exception as e:
            print(f"Error getting segment timings: {str(e)}")
            return {
                'start': None,
                'end': None,
                'words': []
            }

    def process_transcript(self, transcript_text, word_timings=None):
        """Process transcript with word timing information"""
        try:
            # Get segments with timing data
            segments = self.segment_by_theme(transcript_text, word_timings)
            
            if not segments or 'segments' not in segments:
                print("No valid segments returned")
                return None
            
            processed_segments = []
            for segment in segments['segments']:
                # Ensure all required fields exist
                if 'content' not in segment:
                    continue
                    
                # Create processed segment with all required fields
                processed_segment = {
                    'title': segment.get('title', 'Untitled Segment'),
                    'content': segment['content'],
                    'length': len(segment['content']),
                    'word_count': self.count_words(segment['content']),
                    'estimated_duration': f"{self.count_words(segment['content']) / self.WORDS_PER_MINUTE:.1f} minutes",
                    'sentiment': segment.get('sentiment', self.analyze_sentiment(segment['content'])),
                    'keywords': segment.get('keywords', self.extract_keywords(segment['content'])),
                    'start_time': segment.get('start_time'),
                    'end_time': segment.get('end_time'),
                    'word_timings': segment.get('word_timings', [])
                }
                processed_segments.append(processed_segment)
            
            if not processed_segments:
                print("No segments were processed")
                # Create a fallback segment
                return [{
                    'title': 'Complete Content',
                    'content': transcript_text,
                    'length': len(transcript_text),
                    'word_count': self.count_words(transcript_text),
                    'estimated_duration': f"{self.count_words(transcript_text) / self.WORDS_PER_MINUTE:.1f} minutes",
                    'sentiment': self.analyze_sentiment(transcript_text),
                    'keywords': self.extract_keywords(transcript_text),
                    'start_time': None,
                    'end_time': None,
                    'word_timings': []
                }]
            
            return processed_segments
            
        except Exception as e:
            print(f"Error in process_transcript: {str(e)}")
            # Return fallback segment on error
            return [{
                'title': 'Complete Content',
                'content': transcript_text,
                'length': len(transcript_text),
                'word_count': self.count_words(transcript_text),
                'estimated_duration': f"{self.count_words(transcript_text) / self.WORDS_PER_MINUTE:.1f} minutes",
                'sentiment': self.analyze_sentiment(transcript_text),
                'keywords': self.extract_keywords(transcript_text),
                'start_time': None,
                'end_time': None,
                'word_timings': []
            }]

    def generate_hashtags(self, content, max_tags=5):
        """Generate relevant hashtags for the content"""
        prompt = f"""
        Generate {max_tags} relevant hashtags for this content:
        {content}

        Requirements:
        1. Start each with #
        2. No spaces in hashtags
        3. Mix of broad and specific tags
        4. All lowercase
        5. Return only the hashtags separated by spaces

        Example format: #motivation #success #mindset #growth #wisdom
        """
        
        try:
            response = self.get_ai_response(prompt)
            hashtags = response['choices'][0]['message']['content'].strip()
            return hashtags.split()
        except:
            # Fallback to basic hashtags from keywords
            keywords = self.extract_keywords(content)
            return [f"#{keyword.lower()}" for keyword in keywords[:max_tags]]

    def get_thematic_segments(self, text):
        """Get thematic segments using AI assistance"""
        prompt = f"""
        Analyze this text and divide it into 1-2 minute segments. Each segment should be a complete, standalone story.

        Text to analyze: {text}

        Requirements:
        1. Each segment must be self-contained and make sense on its own
        2. Include proper context and background in each segment
        3. Each segment should be 150-300 words (1-2 minutes of speaking)
        4. Give each segment a compelling title
        5. Format as valid JSON with this exact structure:
        {{
            "segments": [
                {{
                    "title": "Compelling Title Here",
                    "content": "Complete segment content here"
                }}
            ]
        }}

        Important:
        - Keep original text exactly as provided (don't paraphrase)
        - Preserve word order for timing alignment
        - Make clean cuts between segments at natural breaks
        """

        try:
            response = self.get_ai_response(prompt)
            if not response or 'choices' not in response:
                print("Error: Invalid AI response")
                return {
                    "segments": [{
                        "title": "Complete Content",
                        "content": text
                    }]
                }

            response_text = response['choices'][0]['message']['content'].strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            try:
                segments_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return {
                    "segments": [{
                        "title": "Complete Content",
                        "content": text
                    }]
                }
            
            # Validate segments structure
            if not isinstance(segments_data, dict) or 'segments' not in segments_data:
                print("Error: Invalid segments structure")
                return {
                    "segments": [{
                        "title": "Complete Content",
                        "content": text
                    }]
                }
            
            return segments_data

        except Exception as e:
            print(f"Error in get_thematic_segments: {str(e)}")
            return {
                "segments": [{
                    "title": "Complete Content",
                    "content": text
                }]
            }

def main():
    # Your API key
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGVsNTBhbGk1MEBnbWFpbC5jb20iLCJpYXQiOjE3MzYxODcxMjR9.qXy0alEIV38TFlVQnS6JUYgEiayxu46F_CdZxf8Czy8"
    
    # Initialize the processor
    processor = SmartTextProcessor(api_key)
    
    # Example transcript text
    transcript = """
    [Your video transcript text here]
    """
    
    # Process the transcript
    segments = processor.process_transcript(transcript)
    
    # Print the results
    print("\n=== Processed Video Segments ===\n")
    for i, segment in enumerate(segments, 1):
        print(f"Segment #{i}")
        print(f"Title: {segment['title']}")
        print(f"Content: {segment['content']}")
        print(f"Duration: {segment['estimated_duration']}")
        print(f"Keywords: {', '.join(segment['keywords'])}")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main() 