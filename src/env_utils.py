"""
Utility functions for reading and writing .env files safely
"""

import os
import re
from typing import Dict, List, Optional


class EnvFileManager:
    """Manages reading and writing to .env files"""
    
    def __init__(self, env_file_path: str = '.env'):
        self.env_file_path = env_file_path
        
    def read_env_file(self) -> Dict[str, str]:
        """Read all variables from .env file"""
        env_vars = {}
        
        if not os.path.exists(self.env_file_path):
            return env_vars
            
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                        
        except Exception as e:
            print(f"Error reading .env file: {e}")
            
        return env_vars
    
    def write_env_file(self, env_vars: Dict[str, str], preserve_comments: bool = True) -> bool:
        """Write variables to .env file, optionally preserving comments and order"""
        try:
            lines = []
            processed_keys = set()
            
            # Read existing file to preserve structure and comments
            if os.path.exists(self.env_file_path) and preserve_comments:
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()
                
                for line in existing_lines:
                    stripped_line = line.strip()
                    
                    # Preserve comments and empty lines
                    if not stripped_line or stripped_line.startswith('#'):
                        lines.append(line.rstrip() + '\n')
                    elif '=' in stripped_line:
                        # Update existing variable
                        key = stripped_line.split('=', 1)[0].strip()
                        if key in env_vars:
                            lines.append(f"{key}={env_vars[key]}\n")
                            processed_keys.add(key)
                        else:
                            # Keep existing variable unchanged
                            lines.append(line.rstrip() + '\n')
                    else:
                        # Keep other lines as-is
                        lines.append(line.rstrip() + '\n')
            
            # Add new variables that weren't in the original file
            for key, value in env_vars.items():
                if key not in processed_keys:
                    lines.append(f"{key}={value}\n")
            
            # Write updated content
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error writing .env file: {e}")
            return False
    
    def update_env_variables(self, updates: Dict[str, str]) -> bool:
        """Update specific environment variables in the .env file"""
        try:
            # Read current variables
            current_vars = self.read_env_file()
            
            # Update with new values
            current_vars.update(updates)
            
            # Write back to file
            return self.write_env_file(current_vars)
            
        except Exception as e:
            print(f"Error updating .env variables: {e}")
            return False
    
    def get_env_file_path(self) -> str:
        """Get the absolute path to the .env file"""
        return os.path.abspath(self.env_file_path)
    
    def get_env_file_directory(self) -> str:
        """Get the directory containing the .env file"""
        return os.path.dirname(self.get_env_file_path())
    
    def validate_required_keys(self, required_keys: List[str]) -> List[str]:
        """Check which required keys are missing from the .env file"""
        env_vars = self.read_env_file()
        missing_keys = []
        
        for key in required_keys:
            if key not in env_vars or not env_vars[key].strip():
                missing_keys.append(key)
                
        return missing_keys


def get_masked_value(value: str, show_last: int = 4) -> str:
    """Return a masked version of a sensitive value"""
    if not value or len(value) <= show_last:
        return '*' * len(value) if value else ''
    
    return '*' * (len(value) - show_last) + value[-show_last:]


def is_env_file_writable(env_file_path: str = '.env') -> bool:
    """Check if the .env file is writable"""
    try:
        abs_path = os.path.abspath(env_file_path)
        
        # If file exists, check if it's writable
        if os.path.exists(abs_path):
            return os.access(abs_path, os.W_OK)
        
        # If file doesn't exist, check if directory is writable
        directory = os.path.dirname(abs_path)
        return os.access(directory, os.W_OK)
        
    except Exception:
        return False
