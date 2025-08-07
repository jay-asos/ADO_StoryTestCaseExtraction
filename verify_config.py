#!/usr/bin/env python3
"""
Configuration verification script for ADO Extractor.
Use this script to verify that configuration changes made through the dashboard
are properly reflected in the .env file and Settings class.
"""

import os
import time
import requests
from config.settings import Settings

def print_separator():
    print("=" * 60)

def check_env_file():
    """Check current values in .env file"""
    print("📁 Checking .env file values:")
    env_path = '.env'

    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    relevant_vars = [
        'ADO_USER_STORY_TYPE',
        'ADO_STORY_EXTRACTION_TYPE',
        'ADO_TEST_CASE_EXTRACTION_TYPE'
    ]

    for var in relevant_vars:
        found = False
        for line in lines:
            if line.strip().startswith(f'{var}='):
                value = line.strip().split('=', 1)[1]
                print(f"  {var} = {value}")
                found = True
                break
        if not found:
            print(f"  {var} = (not set)")

def check_settings_class():
    """Check current values in Settings class"""
    print("🏗️  Checking Settings class values:")
    print(f"  USER_STORY_TYPE = {Settings.USER_STORY_TYPE}")
    print(f"  STORY_EXTRACTION_TYPE = {Settings.STORY_EXTRACTION_TYPE}")
    print(f"  TEST_CASE_EXTRACTION_TYPE = {Settings.TEST_CASE_EXTRACTION_TYPE}")

def reload_and_check():
    """Reload settings and check if values match"""
    print("🔄 Reloading configuration...")
    Settings.reload_config()
    print("✅ Configuration reloaded")

def verify_via_api(base_url="http://127.0.0.1:5000"):
    """Verify configuration via API"""
    print(f"🌐 Checking configuration via API ({base_url})...")
    try:
        response = requests.get(f"{base_url}/api/config/verify", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ API verification successful")
                print("📊 Current config from API:")
                config = data['current_config']
                for key, value in config.items():
                    if key in ['ADO_USER_STORY_TYPE', 'ADO_STORY_EXTRACTION_TYPE', 'ADO_TEST_CASE_EXTRACTION_TYPE']:
                        print(f"  {key} = {value}")

                print("🔍 Environment file verification:")
                env_verification = data['env_file_verification']
                for key, verified in env_verification.items():
                    status = "✅" if verified else "❌"
                    print(f"  {key}: {status}")
            else:
                print(f"❌ API verification failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        print("   Make sure the dashboard server is running on port 5000")

def test_configuration_update():
    """Test updating configuration through the dashboard"""
    print("🧪 Testing configuration update...")

    # Show current values
    print("Current values:")
    check_env_file()
    check_settings_class()

    print("\n" + "="*30)
    print("MANUAL TEST INSTRUCTIONS:")
    print("1. Open the dashboard at http://127.0.0.1:5000")
    print("2. Click 'Edit Config' button")
    print("3. Change 'Story Extraction Type' from current value to a different value")
    print("4. Click 'Save Configuration'")
    print("5. Run this script again to verify the changes")
    print("="*30)

def main():
    """Main verification function"""
    print_separator()
    print("🔧 ADO Extractor Configuration Verification")
    print_separator()

    # Check current state
    check_env_file()
    print()
    check_settings_class()
    print()

    # Reload and check again
    reload_and_check()
    print()
    check_settings_class()
    print()

    # Verify via API if server is running
    verify_via_api()

    print_separator()
    print("✨ Verification complete!")
    print()
    print("💡 To test dashboard updates:")
    print("   1. Run: python src/monitor_api.py")
    print("   2. Open: http://127.0.0.1:5000")
    print("   3. Change config in dashboard")
    print("   4. Run: python verify_config.py")
    print_separator()

if __name__ == "__main__":
    main()
