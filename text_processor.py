import requests
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import time

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

    def segment_by_theme(self, text):
        """Segment text into thematic chunks using AI assistance"""
        
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
        - Make each segment work as an independent video
        - Add necessary context to each segment
        - Ensure no segment references other segments
        - Return ONLY valid JSON, no other text
        """

        try:
            response = self.get_ai_response(prompt)
            response_text = response['choices'][0]['message']['content'].strip()
            
            # Clean the response text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            import json
            segments_data = json.loads(response_text)
            # print("segments_data", segments_data)
            # processed_segments = self.process_segment(segments_data)
            return segments_data
            
        except Exception as e:
            print(f"Error in segment_by_theme: {str(e)}")
            print(f"Raw response: {response['choices'][0]['message']['content']}")
            
            # Create a single segment as fallback
            fallback_segment = {
                'title': 'Complete Video Content',
                'content': text,
                'length': len(text),
                'word_count': self.count_words(text),
                'estimated_duration': f"{self.count_words(text) / self.WORDS_PER_MINUTE:.1f} minutes",
                'sentiment': self.analyze_sentiment(text),
                'keywords': self.extract_keywords(text)
            }
            return [fallback_segment]

    def process_segment(self, segments_data):
        """Process each segment"""
        processed_segments = []
        for segment in segments_data['segments']:
            # Optimize the segment for video
            optimized_content = self.optimize_segment_for_video(segment['content'])

            # Generate metadata
            processed_segment = {
                'title': segment['title'],
                'content': optimized_content,
                'length': len(optimized_content),
                'word_count': self.count_words(optimized_content),
                'estimated_duration': f"{self.count_words(optimized_content) / self.WORDS_PER_MINUTE:.1f} minutes",
                'sentiment': self.analyze_sentiment(optimized_content),
                'keywords': self.extract_keywords(optimized_content)
            }
            processed_segments.append(processed_segment)
        return processed_segments

    def optimize_segment_for_video(self, content):
        """Optimize a segment for video presentation"""
        prompt = f"""
        Transform this content into an engaging, standalone video script:

        {content}

        Requirements:
        1. Add a strong opening hook
        2. Include necessary context and background
        3. Make it completely self-contained
        4. End with a powerful conclusion
        5. Use natural, conversational language
        6. Keep it to 3-5 minutes of speaking time
        7. Format with clear sections:
           - Opening Hook
           - Context/Background
           - Main Points
           - Conclusion

        Return only the optimized script, no explanations.
        """
        
        try:
            response = self.get_ai_response(prompt)
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error optimizing segment: {e}")
            return content

    def process_transcript(self, transcript_text):
        """Process a video transcript into independent, self-contained segments"""
        
        # First, segment the text by themes
        thematic_segments = self.segment_by_theme(transcript_text)
        
        # Then optimize each segment to be self-contained
        optimized_segments = []
        
        for segment in thematic_segments:
            # Optimize the content for standalone video
            prompt = f"""
            Transform this text segment into a self-contained, standalone video script that can be published independently.

            Original text: {segment['content']}

            Requirements:
            1. Add necessary context at the beginning
            2. Make it completely self-contained (no references to other parts)
            3. Include a clear introduction and hook
            4. End with a strong conclusion
            5. Keep the main message and key points
            6. Make it engaging and natural to speak
            7. Ensure it makes sense without any external context
            8. Add transitional phrases where needed
            9. Length: aim for 1-2 minutes of speaking time (~150-300 words)

            Return only the optimized script, no explanations.
            """
            
            response = self.get_ai_response(prompt)
            try:
                optimized_content = response['choices'][0]['message']['content'].strip()
                
                # Remove any markdown formatting if present
                optimized_content = optimized_content.replace('```', '').strip()
                
                # Generate a standalone title
                title_prompt = f"""
                Create a compelling standalone title for this independent video:

                Content: {optimized_content}

                Requirements:
                1. Maximum 60 characters
                2. Must work as a standalone title (no part numbers or references)
                3. Include relevant emoji if appropriate
                4. Make it intriguing but not clickbait
                5. Capture the unique value proposition
                6. Should make sense without context from other videos

                Return only the title, no explanations.
                """
                
                title_response = self.get_ai_response(title_prompt)
                title = title_response['choices'][0]['message']['content'].strip()
                
                # Generate a hook/description
                hook_prompt = f"""
                Create a compelling hook/description for this standalone video:

                Content: {optimized_content}

                Requirements:
                1. 1-2 sentences maximum
                2. Must grab attention immediately
                3. Hint at the value viewer will get
                4. Be specific to this content
                5. Work independently of other videos

                Return only the hook, no explanations.
                """
                
                hook_response = self.get_ai_response(hook_prompt)
                hook = hook_response['choices'][0]['message']['content'].strip()
                
                optimized_segment = {
                    'title': title,
                    'content': optimized_content,
                    'hook': hook,
                    'length': len(optimized_content),
                    'word_count': self.count_words(optimized_content),
                    'estimated_duration': f"{self.count_words(optimized_content) / self.WORDS_PER_MINUTE:.1f} minutes",
                    'sentiment': self.analyze_sentiment(optimized_content),
                    'keywords': self.extract_keywords(optimized_content),
                    'is_standalone': True,
                    'social_share_text': f"{title}\n\n{hook}",
                    'hashtags': self.generate_hashtags(optimized_content)
                }
                
                optimized_segments.append(optimized_segment)
                
            except Exception as e:
                print(f"Error optimizing segment: {e}")
                optimized_segments.append(segment)
        
        return optimized_segments

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