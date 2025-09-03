"""
AI Client Factory for OpenAI and Azure OpenAI Service
Provides unified interface for both AI services with automatic provider switching
"""

from openai import OpenAI, AzureOpenAI
from config.settings import Settings
import time
import logging

logger = logging.getLogger(__name__)

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
        else:
            logger.info(f"🔶 Initializing OpenAI client")
            return OpenAIClient()

class BaseAIClient:
    """Base class for AI clients"""
    
    def __init__(self):
        self.max_retries = Settings.OPENAI_MAX_RETRIES
        self.retry_delay = Settings.OPENAI_RETRY_DELAY
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Abstract method for chat completion"""
        raise NotImplementedError
    
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
            
            result = response.choices[0].message.content.strip()
            logger.info(f"🔶 OpenAI: Request completed successfully, response length: {len(result)} characters")
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
            
            result = response.choices[0].message.content.strip()
            logger.info(f"🔷 Azure OpenAI: Request completed successfully, response length: {len(result)} characters")
            return result
        
        return self._retry_request(_make_request)

# Convenience function for backward compatibility
def get_ai_client():
    """Get AI client instance based on current configuration"""
    return AIClientFactory.create_client()

# Legacy compatibility functions
def create_openai_client():
    """Legacy function for OpenAI client creation"""
    return OpenAIClient()

def create_azure_openai_client():
    """Legacy function for Azure OpenAI client creation"""
    return AzureOpenAIClient()
