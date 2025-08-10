#!/usr/bin/env python3
"""
Clean working test server to verify configuration functionality
"""

import sys
import os
import json
from flask import Flask, request, jsonify, send_file

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.env_utils import EnvFileManager, get_masked_value, is_env_file_writable
    from config.settings import Settings
    
    app = Flask(__name__)
    env_manager = EnvFileManager('.env')
    
    @app.route('/')
    def index():
        """Serve the test dashboard"""
        return send_file('test_dashboard.html')
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        try:
            config_dict = {
                'ado_org_url': f"https://dev.azure.com/{Settings.ADO_ORGANIZATION}" if Settings.ADO_ORGANIZATION else '',
                'ado_organization': Settings.ADO_ORGANIZATION or '',
                'ado_project': Settings.ADO_PROJECT or '',
                'ado_pat': get_masked_value(Settings.ADO_PAT or ''),
                'openai_api_key': get_masked_value(Settings.OPENAI_API_KEY or ''),
                'openai_model': Settings.OPENAI_MODEL or 'gpt-4',
                'story_extraction_type': Settings.STORY_EXTRACTION_TYPE or 'User Story',
                'test_case_extraction_type': Settings.TEST_CASE_EXTRACTION_TYPE or 'Issue',
                'env_file_path': env_manager.get_env_file_path(),
                'env_file_directory': env_manager.get_env_file_directory(),
                'env_file_writable': is_env_file_writable('.env')
            }
            
            return jsonify(config_dict)
        except Exception as e:
            import traceback
            error_msg = f'API Error: {str(e)}'
            traceback.print_exc()
            return jsonify({'error': error_msg}), 500
    
    @app.route('/api/config', methods=['PUT'])
    def update_config():
        """Update configuration and .env file"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            env_updates = {}
            
            # Handle organization and project (required)
            if 'ado_organization' in data:
                if not data['ado_organization'].strip():
                    return jsonify({'error': 'Organization is required'}), 400
                env_updates['ADO_ORGANIZATION'] = data['ado_organization'].strip()
            
            if 'ado_project' in data:
                if not data['ado_project'].strip():
                    return jsonify({'error': 'Project Name is required'}), 400
                env_updates['ADO_PROJECT'] = data['ado_project'].strip()
            
            # Handle sensitive fields - only update if provided and not masked
            if 'ado_pat' in data and data['ado_pat'] and not data['ado_pat'].startswith('*'):
                env_updates['ADO_PAT'] = data['ado_pat'].strip()
            
            if 'openai_api_key' in data and data['openai_api_key'] and not data['openai_api_key'].startswith('*'):
                env_updates['OPENAI_API_KEY'] = data['openai_api_key'].strip()
            
            # Handle other settings
            if 'openai_model' in data:
                env_updates['OPENAI_MODEL'] = data['openai_model']
            
            if 'story_extraction_type' in data:
                env_updates['ADO_STORY_EXTRACTION_TYPE'] = data['story_extraction_type']
            
            if 'test_case_extraction_type' in data:
                env_updates['ADO_TEST_CASE_EXTRACTION_TYPE'] = data['test_case_extraction_type']
            
            # Update .env file
            env_update_success = True
            if env_updates:
                env_update_success = env_manager.update_env_variables(env_updates)
                if env_update_success:
                    Settings.reload_config()
                    print(f"✅ Updated .env file with: {list(env_updates.keys())}")
                else:
                    print("❌ Failed to update .env file")
                    return jsonify({'error': 'Failed to update environment file'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully',
                'env_updated': bool(env_updates and env_update_success),
                'updated_keys': list(env_updates.keys()) if env_updates else []
            })
        
        except Exception as e:
            import traceback
            error_msg = f'Update Error: {str(e)}'
            traceback.print_exc()
            return jsonify({'error': error_msg}), 500
    
    if __name__ == '__main__':
        print("🚀 Starting Clean Configuration API Test Server...")
        print("📍 Access at: http://localhost:8081")
        print("📁 .env file location:", env_manager.get_env_file_path())
        print("🔧 Writable:", is_env_file_writable('.env'))
        print("🔑 Current settings check:")
        print(f"   Organization: {Settings.ADO_ORGANIZATION}")
        print(f"   Project: {Settings.ADO_PROJECT}")
        print(f"   OpenAI Model: {Settings.OPENAI_MODEL}")
        app.run(host='0.0.0.0', port=8081, debug=True, threaded=True)

except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
