from abc import ABC, abstractmethod
import requests
import time
import os

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def get_response(self, prompt, retry_count=3):
        """Get response from AI provider"""
        pass

class HyperbolicAI(AIProvider):
    """Hyperbolic AI provider implementation"""
    
    def __init__(self, api_key):
        self.url = "https://api.hyperbolic.xyz/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.cache = {}

    def get_response(self, prompt, retry_count=3):
        """Get response from Hyperbolic AI with retry mechanism and caching"""
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
                    "temperature": 0.7,
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
                time.sleep(1)
                
        return None

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key):
        try:
            import openai
            self.openai = openai
            self.openai.api_key = api_key
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        self.cache = {}

    def get_response(self, prompt, retry_count=3):
        """Get response from OpenAI with retry mechanism and caching"""
        if prompt in self.cache:
            return self.cache[prompt]
            
        for attempt in range(retry_count):
            try:
                response = self.openai.ChatCompletion.create(
                    model="gpt-4",  # or another model
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
                
                # Convert OpenAI response format to match Hyperbolic format
                result = {
                    "choices": [{
                        "message": {
                            "content": response.choices[0].message.content
                        }
                    }]
                }
                
                self.cache[prompt] = result
                return result
                
            except Exception as e:
                if attempt == retry_count - 1:
                    raise e
                time.sleep(1)
                
        return None

class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, api_key):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        self.cache = {}

    def get_response(self, prompt, retry_count=3):
        """Get response from Claude with retry mechanism and caching"""
        if prompt in self.cache:
            return self.cache[prompt]
            
        for attempt in range(retry_count):
            try:
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2048,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Convert Anthropic response format to match Hyperbolic format
                result = {
                    "choices": [{
                        "message": {
                            "content": response.content[0].text
                        }
                    }]
                }
                
                self.cache[prompt] = result
                return result
                
            except Exception as e:
                if attempt == retry_count - 1:
                    raise e
                time.sleep(1)
                
        return None

def get_ai_provider(provider_name: str, api_key: str) -> AIProvider:
    """Factory function to get AI provider instance"""
    providers = {
        "hyperbolic": HyperbolicAI,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}. Available providers: {', '.join(providers.keys())}")
    
    return provider_class(api_key) 