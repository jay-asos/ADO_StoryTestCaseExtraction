import os
import pytest
from unittest.mock import patch
from config.settings import Settings

class TestSettings:
    def test_settings_with_valid_env(self):
        """Test settings validation with valid environment variables"""
        # Environment variables are set in conftest.py
        assert Settings.validate() is True
        assert Settings.ADO_ORGANIZATION == "test-org"
        assert Settings.ADO_PROJECT == "test-project"
        assert Settings.ADO_PAT == "test-pat"
        assert Settings.OPENAI_API_KEY == "test-key"
    
    def test_settings_missing_required_vars(self):
        """Test settings validation with missing required variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as excinfo:
                Settings.validate()
            
            assert "Missing required settings" in str(excinfo.value)
            assert "ADO_ORGANIZATION" in str(excinfo.value)
            assert "ADO_PROJECT" in str(excinfo.value)
            assert "ADO_PAT" in str(excinfo.value)
            assert "OPENAI_API_KEY" in str(excinfo.value)
    
    def test_default_base_url(self):
        """Test default base URL is set correctly"""
        assert Settings.ADO_BASE_URL == "https://dev.azure.com"
    
    def test_custom_base_url(self):
        """Test custom base URL from environment"""
        with patch.dict(os.environ, {"ADO_BASE_URL": "https://custom.azure.com"}):
            # Reload the Settings class to pick up the new environment variable
            from importlib import reload
            import config.settings
            reload(config.settings)
            from config.settings import Settings as ReloadedSettings
            
            assert ReloadedSettings.ADO_BASE_URL == "https://custom.azure.com"
    
    def test_work_item_types(self):
        """Test work item type constants"""
        assert Settings.REQUIREMENT_TYPE == "Requirement"
        assert Settings.USER_STORY_TYPE == "User Story"
