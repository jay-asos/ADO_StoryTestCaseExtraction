import os
from dotenv import load_dotenv

class Settings:
    """Application settings loaded from environment variables"""

    # Load environment variables
    print("[CONFIG] Loading environment variables...")
    load_dotenv()
    
    # Log AI service provider configuration at startup
    _ai_provider = os.getenv('AI_SERVICE_PROVIDER', 'OPENAI')
    print(f"[CONFIG] 🤖 AI Service Provider: {_ai_provider}")
    if _ai_provider == 'AZURE_OPENAI':
        _azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', 'Not configured')
        _azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'Not configured')
        print(f"[CONFIG] 🔷 Azure OpenAI Endpoint: {_azure_endpoint}")
        print(f"[CONFIG] 🔷 Azure OpenAI Deployment: {_azure_deployment}")
    else:
        _openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        print(f"[CONFIG] 🔶 OpenAI Model: {_openai_model}")

    # Platform selection (ADO or JIRA)
    PLATFORM_TYPE = os.getenv('PLATFORM_TYPE', 'ADO')  # 'ADO' or 'JIRA'

    # Azure DevOps settings
    ADO_ORGANIZATION = os.getenv('ADO_ORGANIZATION')
    ADO_PROJECT = os.getenv('ADO_PROJECT')
    ADO_PAT = os.getenv('ADO_PAT')
    ADO_BASE_URL = "https://dev.azure.com"

    # JIRA settings
    JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')  # e.g., https://yourcompany.atlassian.net
    JIRA_USERNAME = os.getenv('JIRA_USERNAME')  # JIRA username/email
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')  # JIRA API token
    JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')  # e.g., 'PROJ'

    # Work item types for ADO
    REQUIREMENT_TYPE = os.getenv('ADO_REQUIREMENT_TYPE', 'Epic')
    USER_STORY_TYPE = os.getenv('ADO_USER_STORY_TYPE', 'User Story')

    # Work item types for JIRA
    JIRA_REQUIREMENT_TYPE = os.getenv('JIRA_REQUIREMENT_TYPE', 'Epic')
    JIRA_USER_STORY_TYPE = os.getenv('JIRA_USER_STORY_TYPE', 'Story')
    JIRA_TEST_CASE_TYPE = os.getenv('JIRA_TEST_CASE_TYPE', 'Test')

    # Story extraction work item type (Story or Task)
    STORY_EXTRACTION_TYPE = os.getenv('ADO_STORY_EXTRACTION_TYPE', 'User Story')

    # Test case extraction work item type (Issue or Test Case)
    TEST_CASE_EXTRACTION_TYPE = os.getenv('ADO_TEST_CASE_EXTRACTION_TYPE', 'Test Case')
    
    # Test case extraction settings
    AUTO_TEST_CASE_EXTRACTION = os.getenv('ADO_AUTO_TEST_CASE_EXTRACTION', 'true').lower() == 'true'

    # AI Service Configuration
    AI_SERVICE_PROVIDER = os.getenv('AI_SERVICE_PROVIDER', 'OPENAI')  # 'OPENAI' or 'AZURE_OPENAI'

    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_RETRIES = int(os.getenv('OPENAI_MAX_RETRIES', 3))

    # Azure OpenAI settings
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
    AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL', 'gpt-35-turbo')

    try:
        OPENAI_RETRY_DELAY = int(os.getenv('OPENAI_RETRY_DELAY', 5))
    except Exception:
        OPENAI_RETRY_DELAY = 5
    print(f"[CONFIG] OPENAI_RETRY_DELAY: {OPENAI_RETRY_DELAY}")

    @classmethod
    def get_available_work_item_types(cls):
        """Get available work item types for configuration"""
        return {
            'story_types': ['User Story', 'Task'],
            'test_case_types': ['Issue', 'Test Case']
        }

    @classmethod
    def validate(cls):
        """Validate required settings are present"""
        print("[CONFIG] Validating settings...")
        missing = []
        
        # Validate and print test case type
        print(f"[CONFIG] TEST_CASE_EXTRACTION_TYPE: {cls.TEST_CASE_EXTRACTION_TYPE}")
        if cls.TEST_CASE_EXTRACTION_TYPE not in ['Issue', 'Test Case']:
            print(f"[WARNING] Invalid TEST_CASE_EXTRACTION_TYPE: {cls.TEST_CASE_EXTRACTION_TYPE}. Using default: Test Case")
            cls.TEST_CASE_EXTRACTION_TYPE = 'Test Case'

        # Check Azure DevOps settings
        if not cls.ADO_ORGANIZATION:
            missing.append("ADO_ORGANIZATION")
            print("[ERROR] ADO_ORGANIZATION is not set")
        else:
            print(f"[CONFIG] ADO_ORGANIZATION: {cls.ADO_ORGANIZATION}")

        if not cls.ADO_PROJECT:
            missing.append("ADO_PROJECT")
            print("[ERROR] ADO_PROJECT is not set")
        else:
            print(f"[CONFIG] ADO_PROJECT: {cls.ADO_PROJECT}")

        if not cls.ADO_PAT:
            missing.append("ADO_PAT")
            print("[ERROR] ADO_PAT is not set")
        else:
            print(f"[CONFIG] ADO_PAT: {'*' * (len(cls.ADO_PAT) - 4) + cls.ADO_PAT[-4:]}")

        # Check AI service settings
        print(f"[CONFIG] AI_SERVICE_PROVIDER: {cls.AI_SERVICE_PROVIDER}")
        
        if cls.AI_SERVICE_PROVIDER == 'AZURE_OPENAI':
            # Validate Azure OpenAI settings
            if not cls.AZURE_OPENAI_ENDPOINT:
                missing.append("AZURE_OPENAI_ENDPOINT")
                print("[ERROR] AZURE_OPENAI_ENDPOINT is not set")
            else:
                print(f"[CONFIG] AZURE_OPENAI_ENDPOINT: {cls.AZURE_OPENAI_ENDPOINT}")
                
            if not cls.AZURE_OPENAI_API_KEY:
                missing.append("AZURE_OPENAI_API_KEY")
                print("[ERROR] AZURE_OPENAI_API_KEY is not set")
            else:
                print(f"[CONFIG] AZURE_OPENAI_API_KEY: {'*' * (len(cls.AZURE_OPENAI_API_KEY) - 4) + cls.AZURE_OPENAI_API_KEY[-4:]}")
                
            if not cls.AZURE_OPENAI_DEPLOYMENT_NAME:
                missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
                print("[ERROR] AZURE_OPENAI_DEPLOYMENT_NAME is not set")
            else:
                print(f"[CONFIG] AZURE_OPENAI_DEPLOYMENT_NAME: {cls.AZURE_OPENAI_DEPLOYMENT_NAME}")
        else:
            # Validate OpenAI settings
            if not cls.OPENAI_API_KEY:
                missing.append("OPENAI_API_KEY")
                print("[ERROR] OPENAI_API_KEY is not set")
            else:
                print(f"[CONFIG] OPENAI_API_KEY: {'*' * (len(cls.OPENAI_API_KEY) - 4) + cls.OPENAI_API_KEY[-4:]}")

        print(f"[CONFIG] Work Item Types - Story: {cls.STORY_EXTRACTION_TYPE}, Test Case: {cls.TEST_CASE_EXTRACTION_TYPE}")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        print("[CONFIG] All required settings are present")
        return True

    @classmethod
    def reload_config(cls):
        """Reload configuration from .env file"""
        print("[CONFIG] Reloading configuration...")
        load_dotenv(override=True)  # Force reload with override
        
        # Platform selection
        cls.PLATFORM_TYPE = os.getenv('PLATFORM_TYPE', 'ADO')
        print(f"[CONFIG] Platform Type: {cls.PLATFORM_TYPE}")
        
        # Reload Azure DevOps settings
        cls.ADO_ORGANIZATION = os.getenv('ADO_ORGANIZATION')
        cls.ADO_PROJECT = os.getenv('ADO_PROJECT')
        cls.ADO_PAT = os.getenv('ADO_PAT')
        
        # Reload JIRA settings
        cls.JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
        cls.JIRA_USERNAME = os.getenv('JIRA_USERNAME')
        cls.JIRA_TOKEN = os.getenv('JIRA_TOKEN')
        cls.JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')
        
        # Work item types based on platform
        if cls.PLATFORM_TYPE == 'JIRA':
            cls.REQUIREMENT_TYPE = os.getenv('JIRA_REQUIREMENT_TYPE', 'Epic')
            cls.USER_STORY_TYPE = os.getenv('JIRA_USER_STORY_TYPE', 'Story')
            cls.STORY_EXTRACTION_TYPE = os.getenv('JIRA_USER_STORY_TYPE', 'Story')
            cls.TEST_CASE_EXTRACTION_TYPE = os.getenv('JIRA_TEST_CASE_TYPE', 'Test')
        else:
            cls.REQUIREMENT_TYPE = os.getenv('ADO_REQUIREMENT_TYPE', 'Epic')
            cls.USER_STORY_TYPE = os.getenv('ADO_USER_STORY_TYPE', 'User Story')
            cls.STORY_EXTRACTION_TYPE = os.getenv('ADO_STORY_EXTRACTION_TYPE', 'User Story')
            cls.TEST_CASE_EXTRACTION_TYPE = os.getenv('ADO_TEST_CASE_EXTRACTION_TYPE', 'Issue')
        
        cls.AUTO_TEST_CASE_EXTRACTION = os.getenv('ADO_AUTO_TEST_CASE_EXTRACTION', 'true').lower() == 'true'
        
        # AI service configuration
        cls.AI_SERVICE_PROVIDER = os.getenv('AI_SERVICE_PROVIDER', 'OPENAI')
        
        # OpenAI settings
        cls.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        cls.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        cls.OPENAI_MAX_RETRIES = int(os.getenv('OPENAI_MAX_RETRIES', 3))
        
        # Azure OpenAI settings
        cls.AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
        cls.AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
        cls.AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        cls.AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        cls.AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL', 'gpt-35-turbo')
        
        try:
            cls.OPENAI_RETRY_DELAY = int(os.getenv('OPENAI_RETRY_DELAY', 5))
        except Exception:
            cls.OPENAI_RETRY_DELAY = 5
        
        print(f"[CONFIG] Reloaded - REQUIREMENT_TYPE: {cls.REQUIREMENT_TYPE}")
        print(f"[CONFIG] Reloaded - USER_STORY_TYPE: {cls.USER_STORY_TYPE}")
        print(f"[CONFIG] Reloaded - STORY_EXTRACTION_TYPE: {cls.STORY_EXTRACTION_TYPE}")
        print(f"[CONFIG] Reloaded - TEST_CASE_EXTRACTION_TYPE: {cls.TEST_CASE_EXTRACTION_TYPE}")
        
        return True

    @classmethod
    def get_current_config(cls):
        """Get current configuration values for verification"""
        return {
            'ADO_USER_STORY_TYPE': cls.USER_STORY_TYPE,
            'ADO_STORY_EXTRACTION_TYPE': cls.STORY_EXTRACTION_TYPE,
            'ADO_TEST_CASE_EXTRACTION_TYPE': cls.TEST_CASE_EXTRACTION_TYPE,
            'ADO_AUTO_TEST_CASE_EXTRACTION': str(cls.AUTO_TEST_CASE_EXTRACTION).lower(),
            'ADO_ORGANIZATION': cls.ADO_ORGANIZATION,
            'ADO_PROJECT': cls.ADO_PROJECT,
            'OPENAI_MAX_RETRIES': cls.OPENAI_MAX_RETRIES,
            'OPENAI_RETRY_DELAY': cls.OPENAI_RETRY_DELAY
        }

    @classmethod
    def verify_env_file_update(cls, key, expected_value):
        """Verify that a specific key in .env file has the expected value"""
        env_path = os.path.join(os.path.dirname(__file__), '../.env')
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.strip().startswith(f'{key}='):
                    actual_value = line.strip().split('=', 1)[1]
                    if actual_value == expected_value:
                        print(f"[CONFIG] Verified - {key}={actual_value} matches expected value")
                        return True
                    else:
                        print(f"[CONFIG] Mismatch - {key}={actual_value} != {expected_value}")
                        return False
            
            print(f"[CONFIG] Key {key} not found in .env file")
            return False
        except Exception as e:
            print(f"[CONFIG] Error verifying .env file: {e}")
            return False

    @classmethod
    def print_current_config(cls):
        """Print current configuration for debugging"""
        print("="*50)
        print("[CONFIG] Current Configuration:")
        print(f"  ADO_USER_STORY_TYPE: {cls.USER_STORY_TYPE}")
        print(f"  ADO_STORY_EXTRACTION_TYPE: {cls.STORY_EXTRACTION_TYPE}")  
        print(f"  ADO_TEST_CASE_EXTRACTION_TYPE: {cls.TEST_CASE_EXTRACTION_TYPE}")
        print(f"  ADO_AUTO_TEST_CASE_EXTRACTION: {cls.AUTO_TEST_CASE_EXTRACTION}")
        print(f"  ADO_ORGANIZATION: {cls.ADO_ORGANIZATION}")
        print(f"  ADO_PROJECT: {cls.ADO_PROJECT}")
        print("="*50)
