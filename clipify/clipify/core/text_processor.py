import re
from textblob import TextBlob
import json


class SmartTextProcessor:
    def __init__(self, ai_provider):
        """
        Initialize with an AI provider instance
        
        Args:
            ai_provider: Instance of AIProvider class
        """
        self.ai_provider = ai_provider
        
        # Constants for chunk sizing
        self.WORDS_PER_MINUTE = 150
        self.TARGET_CHUNK_SIZE = self.WORDS_PER_MINUTE
        self.MAX_CHUNK_SIZE = int(self.TARGET_CHUNK_SIZE * 1.2)
        self.MIN_CHUNK_SIZE = int(self.TARGET_CHUNK_SIZE * 0.8)
        
        # Constants for thematic segmentation
        self.MIN_SEGMENT_LENGTH = 50
        self.MAX_SEGMENT_LENGTH = 1000
        
        # Common English stop words
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why',
            'can', 'could', 'should', 'would', 'may', 'might', 'must', 'shall'
        }

    def get_ai_response(self, prompt, retry_count=3):
        """Get AI response using the configured provider"""
        return self.ai_provider.get_response(prompt, retry_count)

    def analyze_sentiment(self, text):
        """Analyze the sentiment of text to help with title generation"""
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def extract_keywords(self, text):
        """Extract important keywords from text """
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words 
            and len(word) > 2 
            and word.isalnum()
        ]
        
        # Count word frequencies
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        # Sort by frequency and length
        sorted_keywords = sorted(
            word_freq.items(),
            key=lambda x: (x[1], len(x[0])),
            reverse=True
        )
        
        # Return top 5 unique keywords
        return [word for word, _ in sorted_keywords[:5]]

    def generate_fallback_title(self, keywords):
        """Generate a simple title from keywords if AI generation fails"""
        return f"{''.join(keywords[:3]).title()}"

    def count_words(self, text):
        """Count words in text"""
        return len(text.split())
    
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
                    if segment_timings['start'] is not None and segment_timings['end'] is not None:
                        segment['start_time'] = segment_timings['start']
                        segment['end_time'] = segment_timings['end']
                        segment['word_timings'] = segment_timings['words']
                        segment['operation_status'] = 'success'
                    else:
                        print(f"Warning: Could not find timing for segment: {segment['title']}")
                        # Set to None instead of 0 to indicate missing timing data
                        segment['start_time'] = None
                        segment['end_time'] = None
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
                    'start': None,
                    'end': None,
                    'words': [],
                    'operation_status': 'failed'
                }

            # Clean segment text for comparison
            segment_words = segment_text.split()
            matching_words = []
            
            # Find the start position by looking for the first few words
            start_sequence = ' '.join(segment_words[:3]).lower()  # Use first 3 words as anchor
            
            # Find starting position in word_timings
            start_idx = 0
            for i in range(len(word_timings)):
                current_sequence = ' '.join(
                    w['text'].strip().lower() 
                    for w in word_timings[i:i+3]
                ).strip('.,!?;:"\'')
                
                if start_sequence.strip('.,!?;:"\'') in current_sequence:
                    start_idx = i
                    break
            
            # Start matching from the found position
            current_pos = 0
            for i in range(start_idx, len(word_timings)):
                if current_pos >= len(segment_words):
                    break
                    
                timing_word = word_timings[i]['text'].strip().lower()
                segment_word = segment_words[current_pos].lower()
                
                # Skip punctuation and whitespace for comparison
                if timing_word.strip('.,!?;:"\'') == segment_word.strip('.,!?;:"\''):
                    matching_words.append(word_timings[i])
                    current_pos += 1
            
            if not matching_words:
                print(f"Warning: No matching words found for segment starting with: {start_sequence}")
                return {
                    'start': None,
                    'end': None,
                    'words': [],
                    'operation_status': 'failed'
                }
            
            # Verify we matched most of the words (at least 80%)
            if len(matching_words) < len(segment_words) * 0.8:
                print(f"Warning: Only matched {len(matching_words)}/{len(segment_words)} words")
                return {
                    'start': None,
                    'end': None,
                    'words': [],
                    'operation_status': 'failed'
                }
            
            return {
                'start': matching_words[0]['start'],
                'end': matching_words[-1]['end'],
                'words': matching_words,
                'operation_status': 'success'
            }
            
        except Exception as e:
            print(f"Error in get_segment_timings: {str(e)}")
            return {
                'start': None,
                'end': None,
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

    def get_thematic_segments(self, text):
        """Get thematic segments using AI assistance"""
        json_template = '''
{
    "segments": [
        {
            "title": "Compelling Title Here",
            "content": "Complete segment content here",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }
    ]
}'''

        prompt = f"""
        Analyze this text and divide it into 1-2 minute segments. Each segment should be a complete, standalone story.

        Text to analyze: {text}

        Requirements:
        1. Each segment must be self-contained and make sense on its own
        2. Include proper context and background in each segment
        3. Each segment should be 150-300 words (1-2 minutes of speaking)
        4. Give each segment a compelling title
        5. Include 5 relevant keywords or tags for each segment
        6. IMPORTANT: Segments must not overlap in content - each piece of text should appear in exactly one segment
        7. Format as valid JSON with this exact structure:
{json_template}

        Important:
        - Keep original text exactly as provided (don't paraphrase)
        - Preserve word order for timing alignment
        - Make clean cuts between segments at natural breaks
        - Keywords should be relevant to the segment's specific content
        - Return ONLY the JSON, no additional text or formatting
        """

        try:
            response = self.get_ai_response(prompt)
            if not response or 'choices' not in response:
                print("Error: Invalid AI response")
                return self._create_fallback_segment(text)

            # Extract the content from the response
            response_text = response['choices'][0]['message']['content'].strip()
            
            # Find the JSON content between triple backticks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            try:
                segments_data = json.loads(response_text)
                
                # Ensure each segment has keywords, fallback to extracted keywords if missing
                for segment in segments_data['segments']:
                    if 'keywords' not in segment or not segment['keywords']:
                        segment['keywords'] = self.extract_keywords(segment['content'])
                    # Limit to 5 keywords if more were provided
                    segment['keywords'] = segment['keywords'][:5]
                
                # Validate segments structure
                if not isinstance(segments_data, dict) or 'segments' not in segments_data:
                    print("Error: Invalid segments structure")
                    return self._create_fallback_segment(text)
                
                return segments_data

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Response text was: {response_text}")
                return self._create_fallback_segment(text)

        except Exception as e:
            print(f"Error in get_thematic_segments: {str(e)}")
            return self._create_fallback_segment(text)

    def _create_fallback_segment(self, text):
        """Create a fallback segment when processing fails"""
        return {
            "segments": [{
                "title": "Complete Content",
                "content": text,
                "keywords": self.extract_keywords(text)
            }]
        }

def main():
    pass

if __name__ == "__main__":
    main() 