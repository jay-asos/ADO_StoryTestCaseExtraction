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
        
        @self.app.route('/', methods=['GET'])
        def dashboard():
            """Serve the main dashboard"""
            return render_template('dashboard.html')

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
                upload = data.get('upload', False)
                work_item_type = data.get('work_item_type', self.config.test_case_extraction_type)

                # Extract test cases using the agent
                result = self.agent.extract_test_cases_for_story(story_id)

                if result.extraction_successful:
                    response_data = {
                        'success': True,
                        'story_id': story_id,
                        'story_title': result.story_title,
                        'test_cases': [
                            {
                                'title': tc.title,
                                'description': tc.description,
                                'steps': tc.steps,
                                'expected_outcome': tc.expected_outcome,
                                'priority': tc.priority,
                                'category': tc.category
                            } for tc in result.test_cases
                        ],
                        'test_case_count': len(result.test_cases)
                    }

                    # If upload is requested, create work items
                    if upload:
                        created_items = []
                        for test_case in result.test_cases:
                            try:
                                work_item_id = self.agent.ado_client.create_work_item(
                                    work_item_type=work_item_type,
                                    title=test_case.title,
                                    description=test_case.description,
                                    additional_fields={
                                        'System.Tags': f'TestCase;AutoGenerated;Story-{story_id}',
                                        'Microsoft.VSTS.TCM.Steps': test_case.get_formatted_steps(),
                                        'Custom.TestCaseCategory': test_case.category,
                                        'Microsoft.VSTS.Common.Priority': str(test_case.priority)
                                    }
                                )
                                created_items.append({
                                    'id': work_item_id,
                                    'title': test_case.title
                                })
                            except Exception as e:
                                print(f"Error creating test case work item: {e}")

                        response_data['uploaded'] = True
                        response_data['created_items'] = created_items
                        response_data['message'] = f'Extracted {len(result.test_cases)} test cases and created {len(created_items)} work items'
                    else:
                        response_data['uploaded'] = False
                        response_data['message'] = f'Extracted {len(result.test_cases)} test cases (preview mode)'

                    return jsonify(response_data)
                else:
                    return jsonify({
                        'success': False,
                        'error': result.error_message
                    }), 400

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/stories/<story_id>/test-cases', methods=['GET'])
        def get_story_test_cases(story_id):
            """Get test cases for a specific story (preview without creating work items)"""
            try:
                result = self.agent.extract_test_cases_for_story(story_id)

                if result.extraction_successful:
                    return jsonify({
                        'success': True,
                        'story_id': story_id,
                        'story_title': result.story_title,
                        'test_cases': [
                            {
                                'title': tc.title,
                                'description': tc.description,
                                'steps': tc.steps,
                                'expected_outcome': tc.expected_outcome,
                                'priority': tc.priority,
                                'category': tc.category
                            } for tc in result.test_cases
                        ],
                        'test_case_count': len(result.test_cases)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.error_message
                    }), 400

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/stories/<story_id>/test-cases/upload', methods=['POST'])
        def upload_story_test_cases(story_id):
            """Extract and upload test cases for a story as work items"""
            try:
                data = request.get_json() or {}
                work_item_type = data.get('work_item_type', self.config.test_case_extraction_type)

                result = self.agent.extract_test_cases_for_story(story_id)

                if not result.extraction_successful:
                    return jsonify({
                        'success': False,
                        'error': result.error_message
                    }), 400

                created_items = []
                errors = []

                for test_case in result.test_cases:
                    try:
                        work_item_id = self.agent.ado_client.create_work_item(
                            work_item_type=work_item_type,
                            title=test_case.title,
                            description=test_case.description,
                            additional_fields={
                                'System.Tags': f'TestCase;AutoGenerated;Story-{story_id}',
                                'Microsoft.VSTS.TCM.Steps': test_case.get_formatted_steps(),
                                'Custom.TestCaseCategory': test_case.category,
                                'Microsoft.VSTS.Common.Priority': str(test_case.priority)
                            }
                        )
                        created_items.append({
                            'id': work_item_id,
                            'title': test_case.title
                        })
                    except Exception as e:
                        errors.append(f"Error creating '{test_case.title}': {str(e)}")

                return jsonify({
                    'success': True,
                    'story_id': story_id,
                    'story_title': result.story_title,
                    'created_items': created_items,
                    'total_extracted': len(result.test_cases),
                    'total_created': len(created_items),
                    'errors': errors,
                    'message': f'Created {len(created_items)} test case work items from {len(result.test_cases)} extracted test cases'
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/epics/<epic_id>/test-cases', methods=['POST'])
        def extract_epic_test_cases(epic_id):
            """Extract test cases for all stories in an epic"""
            try:
                data = request.get_json() or {}
                upload = data.get('upload', False)
                work_item_type = data.get('work_item_type', self.config.test_case_extraction_type)

                # Get epic stories first
                epic_result = self.agent.get_epic_stories(epic_id)
                if not epic_result or not epic_result.get('stories'):
                    return jsonify({
                        'success': False,
                        'error': f'No stories found for epic {epic_id}'
                    }), 404

                results = []
                total_test_cases = 0
                total_created_items = 0

                for story in epic_result['stories']:
                    story_id = story.get('id')
                    if not story_id:
                        continue

                    # Extract test cases for this story
                    test_result = self.agent.extract_test_cases_for_story(story_id)
                    if test_result.extraction_successful:
                        story_result = {
                            'story_id': story_id,
                            'story_title': story.get('title', test_result.story_title),
                            'test_cases': len(test_result.test_cases),
                            'created_items': []
                        }

                        total_test_cases += len(test_result.test_cases)

                        # Upload if requested
                        if upload:
                            for test_case in test_result.test_cases:
                                try:
                                    work_item_id = self.agent.ado_client.create_work_item(
                                        work_item_type=work_item_type,
                                        title=test_case.title,
                                        description=test_case.description,
                                        additional_fields={
                                            'System.Tags': f'TestCase;AutoGenerated;Epic-{epic_id};Story-{story_id}',
                                            'Microsoft.VSTS.TCM.Steps': test_case.get_formatted_steps(),
                                            'Custom.TestCaseCategory': test_case.category,
                                            'Microsoft.VSTS.Common.Priority': str(test_case.priority)
                                        }
                                    )
                                    story_result['created_items'].append(work_item_id)
                                    total_created_items += 1
                                except Exception as e:
                                    print(f"Error creating test case work item for story {story_id}: {e}")

                        results.append(story_result)

                return jsonify({
                    'success': True,
                    'epic_id': epic_id,
                    'stories_processed': len(results),
                    'total_test_cases_extracted': total_test_cases,
                    'total_work_items_created': total_created_items,
                    'uploaded': upload,
                    'results': results,
                    'message': f'Processed {len(results)} stories, extracted {total_test_cases} test cases' +
                              (f', created {total_created_items} work items' if upload else ' (preview mode)')
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

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

        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Get recent log entries"""
            try:
                log_file_path = 'logs/epic_monitor.log'
                lines_to_read = int(request.args.get('lines', 100))

                if not os.path.exists(log_file_path):
                    return jsonify({
                        'success': True,
                        'logs': [],
                        'message': 'No log file found'
                    })

                # Read the last N lines from the log file
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-lines_to_read:] if len(lines) > lines_to_read else lines

                # Parse log entries
                log_entries = []
                for line in recent_lines:
                    line = line.strip()
                    if line:
                        # Try to parse timestamp and level from log line
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            level = parts[1]
                            message = parts[2]
                        else:
                            timestamp = datetime.now().isoformat()
                            level = 'INFO'
                            message = line

                        log_entries.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })

                return jsonify({
                    'success': True,
                    'logs': log_entries,
                    'total_lines': len(log_entries)
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/logs/clear', methods=['POST', 'DELETE'])
        def clear_logs():
            """Clear the log file"""
            try:
                log_file_path = 'logs/epic_monitor.log'

                if os.path.exists(log_file_path):
                    # Clear the log file
                    with open(log_file_path, 'w') as f:
                        f.write('')

                    return jsonify({
                        'success': True,
                        'message': 'Logs cleared successfully'
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': 'No log file to clear'
                    })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/update_extraction_type', methods=['POST'])
        def update_extraction_type():
            """Update extraction type in environment configuration"""
            try:
                data = request.get_json()
                if not data or 'user_story_type' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'user_story_type is required'
                    }), 400

                user_story_type = data['user_story_type']

                # Update the configuration using Settings
                from config.settings import Settings

                # Update both ADO_USER_STORY_TYPE and ADO_STORY_EXTRACTION_TYPE
                success1 = Settings.update_env_file('ADO_USER_STORY_TYPE', user_story_type)
                success2 = Settings.update_env_file('ADO_STORY_EXTRACTION_TYPE', user_story_type)

                if success1 and success2:
                    # Reload settings to reflect changes
                    Settings.reload_config()

                    return jsonify({
                        'success': True,
                        'message': f'Extraction type updated to {user_story_type}',
                        'updated_values': {
                            'ADO_USER_STORY_TYPE': user_story_type,
                            'ADO_STORY_EXTRACTION_TYPE': user_story_type
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update environment file'
                    }), 500

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
