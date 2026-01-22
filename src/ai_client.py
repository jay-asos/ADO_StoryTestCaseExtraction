"""
AI Client Factory for OpenAI and Azure OpenAI Service
Provides unified interface for both AI services with automatic provider switching
"""

from openai import OpenAI, AzureOpenAI
from config.settings import Settings
import time
import logging

logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text
    Simple approximation: ~4 characters per token for English text
    For more accuracy, use tiktoken library
    """
    if not text:
        return 0
    # Simple estimation: 4 chars per token (conservative estimate)
    return len(text) // 4


def count_message_tokens(messages: list) -> int:
    """Estimate total tokens for a list of messages"""
    total = 0
    for message in messages:
        if isinstance(message, dict):
            content = message.get('content', '')
            role = message.get('role', '')
            total += estimate_tokens(content)
            total += estimate_tokens(role)
            total += 4  # Every message has overhead tokens
    return total

class AIClientFactory:
    """Factory class for creating AI clients with provider abstraction"""
    
    @staticmethod
    def create_client():
        """Create appropriate AI client based on configuration"""
        provider = Settings.AI_SERVICE_PROVIDER
        logger.info(f"🤖 AI Client Factory: Creating client for provider '{provider}'")
        
        if provider == 'AZURE_OPENAI':
            logger.info(f"🔷 Initializing Azure OpenAI Service client")
            return AzureOpenAIClient()
        elif provider == 'GITHUB':
            logger.info(f"🐙 Initializing GitHub Models client")
            return GitHubModelsClient()
        else:
            logger.info(f"🔶 Initializing OpenAI client")
            return OpenAIClient()

class BaseAIClient:
    """Base class for AI clients"""
    
    def __init__(self):
        self.max_retries = Settings.OPENAI_MAX_RETRIES
        self.retry_delay = Settings.OPENAI_RETRY_DELAY
        self.last_request_tokens = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0
        }
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Abstract method for chat completion"""
        raise NotImplementedError
    
    def get_last_token_usage(self):
        """Get token usage from last API call"""
        return self.last_request_tokens.copy()
    
    def _retry_request(self, func, *args, **kwargs):
        """Helper method for retrying requests with exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"AI request failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"AI request failed after {self.max_retries} attempts: {e}")
        
        raise last_exception

class OpenAIClient(BaseAIClient):
    """Client for standard OpenAI API"""
    
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.OPENAI_MODEL
        logger.info(f"Initialized OpenAI client with model: {self.model}")
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Make chat completion request to OpenAI"""
        def _make_request():
            logger.info(f"🔶 OpenAI: Making chat completion request with model '{self.model}'")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track token usage from response
            if hasattr(response, 'usage'):
                self.last_request_tokens = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            result = response.choices[0].message.content.strip()
            logger.info(f"🔶 OpenAI: Request completed successfully, response length: {len(result)} characters")
            logger.info(f"🔶 OpenAI: Token usage - Prompt: {self.last_request_tokens['prompt_tokens']}, Completion: {self.last_request_tokens['completion_tokens']}, Total: {self.last_request_tokens['total_tokens']}")
            return result
        
        return self._retry_request(_make_request)

class AzureOpenAIClient(BaseAIClient):
    """Client for Azure OpenAI Service"""
    
    def __init__(self):
        super().__init__()
        self.client = AzureOpenAI(
            api_key=Settings.AZURE_OPENAI_API_KEY,
            api_version=Settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = Settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.model = Settings.AZURE_OPENAI_MODEL
        logger.info(f"Initialized Azure OpenAI client with deployment: {self.deployment_name}")
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Make chat completion request to Azure OpenAI"""
        def _make_request():
            logger.info(f"🔷 Azure OpenAI: Making chat completion request to deployment '{self.deployment_name}'")
            logger.debug(f"🔷 Azure OpenAI: Endpoint={Settings.AZURE_OPENAI_ENDPOINT}, API Version={Settings.AZURE_OPENAI_API_VERSION}")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name as model for Azure
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track token usage from response
            if hasattr(response, 'usage'):
                self.last_request_tokens = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            result = response.choices[0].message.content.strip()
            logger.info(f"🔷 Azure OpenAI: Request completed successfully, response length: {len(result)} characters")
            logger.info(f"🔷 Azure OpenAI: Token usage - Prompt: {self.last_request_tokens['prompt_tokens']}, Completion: {self.last_request_tokens['completion_tokens']}, Total: {self.last_request_tokens['total_tokens']}")
            return result
        
        return self._retry_request(_make_request)

# Convenience function for backward compatibility
def get_ai_client():
    """Get AI client instance based on current configuration"""
    return AIClientFactory.create_client()

class GitHubModelsClient(BaseAIClient):
    """Client for GitHub Models (free tier with GitHub PAT)"""
    
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            base_url=Settings.GITHUB_API_BASE,
            api_key=Settings.GITHUB_TOKEN
        )
        self.model = Settings.GITHUB_MODEL
        logger.info(f"Initialized GitHub Models client with model: {self.model}")
        logger.info(f"Using endpoint: {Settings.GITHUB_API_BASE}")
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Make chat completion request to GitHub Models"""
        def _make_request():
            logger.info(f"🐙 GitHub Models: Making chat completion request with model '{self.model}'")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track token usage from response
            if hasattr(response, 'usage'):
                self.last_request_tokens = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            result = response.choices[0].message.content.strip()
            logger.info(f"🐙 GitHub Models: Request completed successfully, response length: {len(result)} characters")
            logger.info(f"🐙 GitHub Models: Token usage - Prompt: {self.last_request_tokens['prompt_tokens']}, Completion: {self.last_request_tokens['completion_tokens']}, Total: {self.last_request_tokens['total_tokens']}")
            return result
        
        return self._retry_request(_make_request)

# Legacy compatibility functions
def create_openai_client():
    """Legacy function for OpenAI client creation"""
    return OpenAIClient()

def create_azure_openai_client():
    """Legacy function for Azure OpenAI client creation"""
    return AzureOpenAIClient()

def create_github_models_client():
    """Legacy function for GitHub Models client creation"""
    return GitHubModelsClient()
