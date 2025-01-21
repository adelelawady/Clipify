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
                # Process each segment to add timing information
                for segment in segments['segments']:
                    # Get word timings for this specific segment
                    segment_timings = self.get_segment_timings(
                        segment['content'], 
                        word_timings,
                        start_pos=0
                    )
                    
                    # Update segment with timing information
                    if segment_timings['start'] is not None:
                        segment['start_time'] = segment_timings['start']
                        segment['end_time'] = segment_timings['end']
                        segment['word_timings'] = segment_timings['words']
                        segment['operation_status'] = segment_timings['operation_status']
                    else:
                        print(f"Warning: Could not find timing for segment: {segment['title']}")
                        # Add empty timing data to maintain structure
                        segment['start_time'] = 0
                        segment['end_time'] = 0
                        segment['word_timings'] = []
                        segment['operation_status'] = 'failed'
            
            return segments
            
        except Exception as e:
            print(f"Error in segment_by_theme: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    def get_segment_timings(self, segment_text, word_timings, start_pos=0):
        """Extract timing information for a segment based on word timings"""
        try:
            # Ensure word_timings is a dict with word_timings list
            if isinstance(word_timings, dict):
                word_timings = word_timings.get('word_timings', [])
            
            if not word_timings:
                print("Error: No word timings provided")
                return {
                    'start': 0,
                    'end': 0,
                    'words': [],
                    'operation_status': 'failed'
                }

            # Clean and normalize text for comparison
            def clean_word(word):
                return re.sub(r'[^\w\s]', '', word.lower().strip())

            # Get segment words
            segment_words = segment_text.lower().split()
            
            # Find the start of the segment in word timings
            start_idx = -1
            end_idx = -1
            
            # Look for the first few words of the segment
            search_words = segment_words[:3]  # Use first 3 words for better accuracy
            search_text = ' '.join(search_words).lower()
            
            # Build timing text for comparison
            timing_text = ''
            for i, timing in enumerate(word_timings):
                if 'text' in timing:  # Use 'text' instead of 'word'
                    timing_text = ' '.join(t.get('text', '').lower() for t in word_timings[i:i+3])
                    if search_text in timing_text:
                        start_idx = i
                        break

            if start_idx == -1:
                print(f"Warning: Could not find start of segment: {search_text}")
                return {
                    'start': 0,
                    'end': 0,
                    'words': [],
                    'operation_status': 'failed'
                }

            # Find the end of the segment
            end_words = segment_words[-3:]  # Use last 3 words
            end_text = ' '.join(end_words).lower()
            
            for i in range(start_idx, len(word_timings)):
                timing_text = ' '.join(t.get('text', '').lower() for t in word_timings[i:i+3])
                if end_text in timing_text:
                    end_idx = i + 2  # Include the matched words
                    break

            if end_idx == -1:
                end_idx = start_idx + len(segment_words)  # Approximate if exact match not found
            
            # Get timing information
            try:
                start_time = float(word_timings[start_idx].get('start', 0))
                end_time = float(word_timings[min(end_idx, len(word_timings)-1)].get('end', 0))
                
                # Ensure end time is after start time
                if end_time <= start_time:
                    end_time = start_time + 30  # Default to 30 seconds if timing is invalid
                    
                return {
                    'start': start_time,
                    'end': end_time,
                    'words': word_timings[start_idx:end_idx+1],
                    'operation_status': 'success'
                }
                
            except Exception as e:
                print(f"Error extracting timing values: {str(e)}")
                return {
                    'start': 0,
                    'end': 0,
                    'words': [],
                    'operation_status': 'failed'
                }

        except Exception as e:
            print(f"Error in get_segment_timings: {str(e)}")
            return {
                'start': 0,
                'end': 0,
                'words': [],
                'operation_status': 'failed'
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
                        "content": text,
                        "keywords": self.extract_keywords(text)
                    }]
                }

            response_text = response['choices'][0]['message']['content'].strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            try:
                segments_data = json.loads(response_text)
                
                # Add keywords to each segment
                for segment in segments_data['segments']:
                    segment['keywords'] = self.extract_keywords(segment['content'])
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                return {
                    "segments": [{
                        "title": "Complete Content",
                        "content": text,
                        "keywords": self.extract_keywords(text)
                    }]
                }
            
            # Validate segments structure
            if not isinstance(segments_data, dict) or 'segments' not in segments_data:
                print("Error: Invalid segments structure")
                return {
                    "segments": [{
                        "title": "Complete Content",
                        "content": text,
                        "keywords": self.extract_keywords(text)
                    }]
                }
            
            return segments_data

        except Exception as e:
            print(f"Error in get_thematic_segments: {str(e)}")
            return {
                "segments": [{
                    "title": "Complete Content",
                    "content": text,
                    "keywords": self.extract_keywords(text)
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