#!/usr/bin/env python3
"""
REST API interface for controlling the EPIC monitoring service.
"""

import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from typing import Optional
import os

from src.monitor import EpicChangeMonitor, MonitorConfig, load_config_from_file, create_default_config
from src.agent import StoryExtractionAgent


class MonitorAPI:
    """REST API wrapper for the EPIC monitor"""
    
    def __init__(self, config: MonitorConfig):
        self.app = Flask(__name__, 
                        template_folder='../templates',
                        static_folder='../static')
        self.monitor: Optional[EpicChangeMonitor] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.config = config
        self.agent = StoryExtractionAgent()  # Add agent for test case extraction
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get monitoring status"""
            if self.monitor:
                status = self.monitor.get_status()
                return jsonify(status)
            else:
                return jsonify({
                    'is_running': False,
                    'message': 'Monitor not initialized'
                })
        
        @self.app.route('/api/start', methods=['POST'])
        def start_monitor():
            """Start the monitoring service"""
            try:
                if self.monitor and self.monitor.is_running:
                    return jsonify({
                        'success': False,
                        'message': 'Monitor is already running'
                    }), 400
                
                # Initialize monitor if not exists
                if not self.monitor:
                    self.monitor = EpicChangeMonitor(self.config)
                
                # Start in background thread
                self.monitor_thread = threading.Thread(target=self.monitor.start)
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
                
                return jsonify({
                    'success': True,
                    'message': 'Monitor started successfully'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_monitor():
            """Stop the monitoring service"""
            try:
                if self.monitor:
                    self.monitor.stop()
                    return jsonify({
                        'success': True,
                        'message': 'Monitor stopped successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Monitor is not running'
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/epics', methods=['GET'])
        def list_epics():
            """List monitored EPICs"""
            if self.monitor:
                status = self.monitor.get_status()
                return jsonify({
                    'epics': list(status['monitored_epics'].keys()),
                    'details': status['monitored_epics']
                })
            else:
                return jsonify({
                    'epics': [],
                    'message': 'Monitor not initialized'
                })
        
        @self.app.route('/api/epics/<epic_id>', methods=['POST'])
        def add_epic(epic_id):
            """Add an EPIC to monitoring"""
            try:
                if not self.monitor:
                    self.monitor = EpicChangeMonitor(self.config)
                
                success = self.monitor.add_epic(epic_id)
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'EPIC {epic_id} added to monitoring'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'Failed to add EPIC {epic_id}'
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/epics/<epic_id>', methods=['DELETE'])
        def remove_epic(epic_id):
            """Remove an EPIC from monitoring"""
            try:
                if self.monitor:
                    success = self.monitor.remove_epic(epic_id)
                    if success:
                        return jsonify({
                            'success': True,
                            'message': f'EPIC {epic_id} removed from monitoring'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': f'EPIC {epic_id} not found'
                        }), 404
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Monitor not initialized'
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get current configuration"""
            try:
                from config.settings import Settings
                return jsonify({
                    'config': {
                        'poll_interval_seconds': self.config.poll_interval_seconds,
                        'auto_sync': self.config.auto_sync,
                        'auto_extract_new_epics': self.config.auto_extract_new_epics,
                        'story_extraction_type': self.config.story_extraction_type,
                        'test_case_extraction_type': self.config.test_case_extraction_type,
                        'skip_duplicate_check': self.config.skip_duplicate_check,
                        'retry_attempts': self.config.retry_attempts,
                        'retry_delay_seconds': self.config.retry_delay_seconds,
                        'log_level': self.config.log_level
                    },
                    'available_types': Settings.get_available_work_item_types()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update configuration"""
            try:
                data = request.get_json()
                
                # Update configuration
                if 'poll_interval_seconds' in data:
                    self.config.poll_interval_seconds = int(data['poll_interval_seconds'])
                if 'auto_sync' in data:
                    self.config.auto_sync = bool(data['auto_sync'])
                if 'auto_extract_new_epics' in data:
                    self.config.auto_extract_new_epics = bool(data['auto_extract_new_epics'])
                if 'story_extraction_type' in data:
                    self.config.story_extraction_type = data['story_extraction_type']
                if 'test_case_extraction_type' in data:
                    self.config.test_case_extraction_type = data['test_case_extraction_type']
                if 'skip_duplicate_check' in data:
                    self.config.skip_duplicate_check = bool(data['skip_duplicate_check'])
                if 'retry_attempts' in data:
                    self.config.retry_attempts = int(data['retry_attempts'])
                if 'retry_delay_seconds' in data:
                    self.config.retry_delay_seconds = int(data['retry_delay_seconds'])
                if 'log_level' in data:
                    self.config.log_level = data['log_level']

                # Save updated config
                config_data = {
                    'poll_interval_seconds': self.config.poll_interval_seconds,
                    'auto_sync': self.config.auto_sync,
                    'auto_extract_new_epics': self.config.auto_extract_new_epics,
                    'story_extraction_type': self.config.story_extraction_type,
                    'test_case_extraction_type': self.config.test_case_extraction_type,
                    'skip_duplicate_check': self.config.skip_duplicate_check,
                    'retry_attempts': self.config.retry_attempts,
                    'retry_delay_seconds': self.config.retry_delay_seconds,
                    'log_level': self.config.log_level
                }

                with open('monitor_config.json', 'w') as f:
                    json.dump(config_data, f, indent=2)

                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully',
                    'config': config_data
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/force-check', methods=['POST'])
        def force_check():
            """Force check for changes"""
            try:
                data = request.get_json() or {}
                epic_id = data.get('epic_id')

                if self.monitor:
                    results = self.monitor.force_check(epic_id)
                    return jsonify({
                        'success': True,
                        'results': results
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Monitor not initialized'
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/test-cases/extract', methods=['POST'])
        def extract_test_cases():
            """Extract test cases for a story"""
            try:
                data = request.get_json()
                if not data or 'story_id' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'story_id is required'
                    }), 400
                
                story_id = data['story_id']
                work_item_type = data.get('work_item_type', self.config.test_case_extraction_type)

                # Extract test cases using the test case extractor
                from src.test_case_extractor import TestCaseExtractor
                extractor = TestCaseExtractor()

                result = extractor.extract_and_create_test_cases(
                    story_id=story_id,
                    work_item_type=work_item_type
                )

                return jsonify({
                    'success': True,
                    'message': f'Test cases extracted for story {story_id}',
                    'result': result
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Get recent logs"""
            try:
                lines = int(request.args.get('lines', 50))
                log_file = 'logs/epic_monitor.log'

                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        log_lines = f.readlines()

                    # Return the last N lines
                    recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
                    return jsonify({
                        'logs': [line.strip() for line in recent_logs],
                        'total_lines': len(log_lines)
                    })
                else:
                    return jsonify({
                        'logs': [],
                        'total_lines': 0
                    })

            except Exception as e:
                return jsonify({
                    'logs': [f"Error reading logs: {str(e)}"],
                    'total_lines': 0
                })

        @self.app.route('/api/logs/clear', methods=['DELETE'])
        def clear_logs():
            """Clear logs from display (doesn't delete log file)"""
            try:
                # This endpoint just returns success - it's for clearing the display only
                # The actual log file remains intact on disk
                return jsonify({
                    'success': True,
                    'message': 'Logs cleared from display'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/')
        def dashboard():
            """Serve the dashboard"""
            return render_template('dashboard.html')

        @self.app.route('/api/update_extraction_type', methods=['POST'])
        def update_extraction_type():
            """Update the user story extraction type in the .env file"""
            data = request.get_json()
            new_type = data.get('user_story_type')
            if not new_type:
                return jsonify({'success': False, 'message': 'Missing user_story_type'}), 400
            env_path = os.path.join(os.path.dirname(__file__), '../.env')
            try:
                # Read current .env
                with open(env_path, 'r') as f:
                    lines = f.readlines()

                # Update or add both ADO_USER_STORY_TYPE and ADO_STORY_EXTRACTION_TYPE
                variables_to_update = ['ADO_USER_STORY_TYPE', 'ADO_STORY_EXTRACTION_TYPE']
                updated_vars = {}

                for var_name in variables_to_update:
                    updated = False
                    for i, line in enumerate(lines):
                        if line.startswith(f'{var_name}='):
                            lines[i] = f'{var_name}={new_type}\n'
                            updated = True
                            updated_vars[var_name] = 'updated'
                            break
                    if not updated:
                        lines.append(f'{var_name}={new_type}\n')
                        updated_vars[var_name] = 'added'

                # Write back
                with open(env_path, 'w') as f:
                    f.writelines(lines)

                # Reload Settings class to reflect changes immediately
                from config.settings import Settings
                Settings.reload_config()

                # Verify both updates
                verification_results = {}
                verification_results['ADO_USER_STORY_TYPE'] = Settings.verify_env_file_update('ADO_USER_STORY_TYPE', new_type)
                verification_results['ADO_STORY_EXTRACTION_TYPE'] = Settings.verify_env_file_update('ADO_STORY_EXTRACTION_TYPE', new_type)

                return jsonify({
                    'success': True,
                    'message': 'Extraction type updated for both USER_STORY_TYPE and STORY_EXTRACTION_TYPE.',
                    'new_value': new_type,
                    'updated_variables': updated_vars,
                    'verification_results': verification_results,
                    'current_settings': {
                        'USER_STORY_TYPE': Settings.USER_STORY_TYPE,
                        'STORY_EXTRACTION_TYPE': Settings.STORY_EXTRACTION_TYPE
                    }
                })
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        @self.app.route('/api/config/verify', methods=['GET'])
        def verify_config():
            """Verify current configuration values"""
            try:
                from config.settings import Settings

                # Reload configuration to get latest values
                Settings.reload_config()

                # Get current config
                current_config = Settings.get_current_config()

                # Verify specific values in .env file
                env_verification = {}
                env_verification['ADO_USER_STORY_TYPE'] = Settings.verify_env_file_update(
                    'ADO_USER_STORY_TYPE', current_config['ADO_USER_STORY_TYPE']
                )
                env_verification['ADO_STORY_EXTRACTION_TYPE'] = Settings.verify_env_file_update(
                    'ADO_STORY_EXTRACTION_TYPE', current_config['ADO_STORY_EXTRACTION_TYPE']
                )

                Settings.print_current_config()

                return jsonify({
                    'success': True,
                    'current_config': current_config,
                    'env_file_verification': env_verification,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the Flask API server"""
        print(f"Starting Monitor API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# Expose Flask app for Flask CLI discovery
config = None
try:
    config = load_config_from_file('monitor_config.json')
except Exception:
    config = create_default_config('monitor_config.json')
app = MonitorAPI(config).app


def main():
    """Main entry point for the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EPIC Change Monitor API Server')
    parser.add_argument('--config', default='monitor_config.json', help='Configuration file')
    parser.add_argument('--host', default='127.0.0.1', help='API server host')
    parser.add_argument('--port', type=int, default=5000, help='API server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--create-config', action='store_true', help='Create default config file')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config(args.config)
        return
    
    # Load configuration
    try:
        config = load_config_from_file(args.config)
    except:
        print(f"Failed to load config from {args.config}, creating default...")
        config = create_default_config(args.config)
    
    # Start API server
    api = MonitorAPI(config)
    print(f"Starting EPIC Change Monitor API on {args.host}:{args.port}")
    print(f"Configuration: {args.config}")
    print(f"Monitoring {len(config.epic_ids or [])} EPICs")
    print(f"API Documentation: http://{args.host}:{args.port}/")
    
    try:
        api.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        if api.monitor:
            api.monitor.stop()


if __name__ == '__main__':
    main()
