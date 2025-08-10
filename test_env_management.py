#!/usr/bin/env python3
"""
Test script to verify the environment file management functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.env_utils import EnvFileManager, get_masked_value, is_env_file_writable
    print("✅ Successfully imported env_utils")
    
    # Test the env file manager
    env_manager = EnvFileManager('.env')
    
    # Test reading env file
    print("\n📁 Testing .env file reading:")
    env_vars = env_manager.read_env_file()
    print(f"Found {len(env_vars)} environment variables")
    
    for key in ['ADO_ORGANIZATION', 'ADO_PROJECT', 'OPENAI_API_KEY', 'ADO_PAT']:
        if key in env_vars:
            masked_value = get_masked_value(env_vars[key])
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: NOT FOUND")
    
    # Test file path information
    print(f"\n📍 File path info:")
    print(f"  Env file path: {env_manager.get_env_file_path()}")
    print(f"  Directory: {env_manager.get_env_file_directory()}")
    print(f"  Is writable: {is_env_file_writable('.env')}")
    
    # Test masking function
    print(f"\n🔒 Testing value masking:")
    test_values = [
        "short",
        "medium_length_key",
        "very_long_api_key_with_many_characters_1234567890",
        ""
    ]
    
    for value in test_values:
        print(f"  '{value}' -> '{get_masked_value(value)}'")
    
    print("\n✅ All tests completed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
