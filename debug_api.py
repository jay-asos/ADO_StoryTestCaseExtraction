#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Settings
    from src.env_utils import EnvFileManager, get_masked_value
    
    print("Direct access to Settings:")
    print(f"Settings.ADO_ORGANIZATION: {Settings.ADO_ORGANIZATION}")
    print(f"Settings.ADO_PROJECT: {Settings.ADO_PROJECT}")
    
    env_manager = EnvFileManager('.env')
    print(f"\nMasked PAT: {get_masked_value(Settings.ADO_PAT or '')}")
    print(f"Masked API Key: {get_masked_value(Settings.OPENAI_API_KEY or '')}")
    
    # Test the config dict creation like in the API
    config_dict = {
        'ado_org_url': f"https://dev.azure.com/{Settings.ADO_ORGANIZATION}" if Settings.ADO_ORGANIZATION else '',
        'ado_organization': Settings.ADO_ORGANIZATION or '',
        'ado_project': Settings.ADO_PROJECT or '',
        'ado_pat': get_masked_value(Settings.ADO_PAT or ''),
        'openai_api_key': get_masked_value(Settings.OPENAI_API_KEY or ''),
        'openai_model': getattr(Settings, 'OPENAI_MODEL', 'gpt-4'),
        'story_extraction_type': getattr(Settings, 'STORY_EXTRACTION_TYPE', 'User Story'),
        'test_case_extraction_type': getattr(Settings, 'TEST_CASE_EXTRACTION_TYPE', 'Issue'),
        'env_file_path': env_manager.get_env_file_path(),
        'env_file_directory': env_manager.get_env_file_directory(),
    }
    
    print("\nConfig dict created successfully:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
