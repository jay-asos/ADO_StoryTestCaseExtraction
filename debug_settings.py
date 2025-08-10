#!/usr/bin/env python3
"""
Debug script to check Settings class structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.settings import Settings
    
    print("Settings class attributes:")
    print(f"ADO_ORGANIZATION: {getattr(Settings, 'ADO_ORGANIZATION', 'NOT_FOUND')}")
    print(f"ADO_PROJECT: {getattr(Settings, 'ADO_PROJECT', 'NOT_FOUND')}")
    print(f"ADO_PAT: {getattr(Settings, 'ADO_PAT', 'NOT_FOUND')}")
    print(f"OPENAI_API_KEY: {getattr(Settings, 'OPENAI_API_KEY', 'NOT_FOUND')}")
    print(f"OPENAI_MODEL: {getattr(Settings, 'OPENAI_MODEL', 'NOT_FOUND')}")
    print(f"STORY_EXTRACTION_TYPE: {getattr(Settings, 'STORY_EXTRACTION_TYPE', 'NOT_FOUND')}")
    
    # Try with instance
    print("\nWith instance:")
    settings_instance = Settings()
    print(f"Instance ADO_ORGANIZATION: {getattr(settings_instance, 'ADO_ORGANIZATION', 'NOT_FOUND')}")
    print(f"Instance ADO_PROJECT: {getattr(settings_instance, 'ADO_PROJECT', 'NOT_FOUND')}")
    
    # List all attributes
    print("\nAll class attributes:")
    for attr in dir(Settings):
        if not attr.startswith('_') and not callable(getattr(Settings, attr)):
            print(f"  {attr}: {getattr(Settings, attr)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
