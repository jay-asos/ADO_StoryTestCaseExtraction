#!/usr/bin/env python3
"""
Simple test server to verify configuration API functionality
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
    
    @app.route('/simple')
    def simple_info():
        return """
        <html>
        <head><title>Configuration API Test</title></head>
        <body>
        <h1>Configuration API Test</h1>
        <p>Test the configuration endpoints:</p>
        <ul>
            <li><a href="/api/config">/api/config</a> - GET configuration</li>
            <li><strong>POST /api/config</strong> - Update configuration (use curl or postman)</li>
            <li><a href="/">Test Dashboard</a> - Interactive dashboard</li>
        </ul>
        
        <h2>Current .env file location:</h2>
        <p><strong>""" + env_manager.get_env_file_path() + """</strong></p>
        <p>Writable: """ + str(is_env_file_writable('.env')) + """</p>
        
        <h2>Test Update:</h2>
        <p>To test updating, use curl:</p>
        <pre>
curl -X PUT http://localhost:8080/api/config \\
  -H "Content-Type: application/json" \\
  -d '{
    "ado_organization": "papai0709",
    "ado_project": "Practice",
    "openai_model": "gpt-4"
  }'
        </pre>
        </body>
        </html>
        """
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        try:
            # Get current env values for display
            env_vars = env_manager.read_env_file()
            
            config_dict = {
                'ado_org_url': f"https://dev.azure.com/{Settings.ADO_ORGANIZATION}" if Settings.ADO_ORGANIZATION else '',
                'ado_organization': Settings.ADO_ORGANIZATION or '',
                'ado_project': Settings.ADO_PROJECT or '',
                'ado_pat': get_masked_value(Settings.ADO_PAT or ''),  # Masked but shows structure
                'openai_api_key': get_masked_value(Settings.OPENAI_API_KEY or ''),  # Masked but shows structure
                'openai_model': Settings.OPENAI_MODEL or 'gpt-4',
                'story_extraction_type': Settings.STORY_EXTRACTION_TYPE or 'User Story',
                'test_case_extraction_type': Settings.TEST_CASE_EXTRACTION_TYPE or 'Issue',
                
                # Add file path information
                'env_file_path': env_manager.get_env_file_path(),
                'env_file_directory': env_manager.get_env_file_directory(),
                'env_file_writable': is_env_file_writable('.env')
            }
            
            return jsonify(config_dict)
        except Exception as e:
            return jsonify({'error': f'Failed to get configuration: {str(e)}'}), 500
    
    @app.route('/api/config', methods=['PUT'])
    def update_config():
        """Update configuration and .env file"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            # Prepare environment variables updates
            env_updates = {}
            
            # Handle Azure DevOps settings - these are required
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
            
            # Handle other OpenAI settings
            if 'openai_model' in data:
                env_updates['OPENAI_MODEL'] = data['openai_model']
            
            # Handle work item types
            if 'story_extraction_type' in data:
                env_updates['ADO_STORY_EXTRACTION_TYPE'] = data['story_extraction_type']
            
            if 'test_case_extraction_type' in data:
                env_updates['ADO_TEST_CASE_EXTRACTION_TYPE'] = data['test_case_extraction_type']
            
            # Update .env file if we have environment updates
            env_update_success = True
            if env_updates:
                env_update_success = env_manager.update_env_variables(env_updates)
                if env_update_success:
                    # Reload settings to pick up changes
                    Settings.reload_config()
                    print(f"Updated .env file with: {list(env_updates.keys())}")
                else:
                    print("Failed to update .env file")
                    return jsonify({'error': 'Failed to update environment file'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully',
                'env_updated': bool(env_updates and env_update_success),
                'updated_keys': list(env_updates.keys()) if env_updates else []
            })
        
        except Exception as e:
            print(f"Error updating config: {str(e)}")
            return jsonify({'error': f'Failed to update configuration: {str(e)}'}), 500
    
    if __name__ == '__main__':
        print("🚀 Starting Configuration API Test Server...")
        print("📍 Access at: http://localhost:8080")
        print("📁 .env file location:", env_manager.get_env_file_path())
        print("🔧 Writable:", is_env_file_writable('.env'))
        app.run(host='0.0.0.0', port=8080, debug=True)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
