"""
Monitor API for the ADO Story Extractor Dashboard
Provides REST API endpoints for the web dashboard
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

from src.agent import StoryExtractionAgent
from src.models import TestCaseExtractionResult, StoryExtractionResult
from config.settings import Settings


class MonitorAPI:
    """Flask-based API for monitoring and controlling the story extraction process"""

    def __init__(self):
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        CORS(self.app)

        self.agent = StoryExtractionAgent()
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html')

        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'ADO Story Extractor API'
            })

        @self.app.route('/api/test-cases/extract', methods=['POST'])
        def extract_test_cases():
            """Extract test cases for a story"""
            try:
                data = request.get_json()
                story_id = data.get('story_id', '').strip()
                upload_to_ado = data.get('upload_to_ado', True)

                if not story_id:
                    return jsonify({
                        'success': False,
                        'error': 'Story ID is required'
                    }), 400

                # Extract test cases using the agent
                result = self.agent.extract_test_cases_for_story(story_id)

                # If upload is requested and extraction was successful, upload to ADO
                if upload_to_ado and result.extraction_successful and result.test_cases:
                    try:
                        # Upload test cases as Issues (this functionality exists in the agent)
                        upload_result = self.agent.extract_test_cases_as_issues(story_id, upload_to_ado=True)
                        if upload_result.extraction_successful:
                            result = upload_result  # Use the upload result instead
                    except Exception as upload_error:
                        self.logger.error(f"Failed to upload test cases: {upload_error}")
                        # Continue with the extraction result even if upload fails

                return jsonify({
                    'success': result.extraction_successful,
                    'story_id': result.story_id,
                    'story_title': result.story_title,
                    'test_cases': [tc.to_dict() for tc in result.test_cases],
                    'total_test_cases': len(result.test_cases),
                    'error': result.error_message if not result.extraction_successful else None,
                    'uploaded_to_ado': upload_to_ado and result.extraction_successful
                })

            except Exception as e:
                self.logger.error(f"Error in extract_test_cases endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                }), 500

        @self.app.route('/api/test-cases/preview', methods=['POST'])
        def preview_test_cases():
            """Preview test cases for a story without uploading to ADO"""
            try:
                data = request.get_json()
                story_id = data.get('story_id', '').strip()

                if not story_id:
                    return jsonify({
                        'success': False,
                        'error': 'Story ID is required'
                    }), 400

                # Extract test cases without uploading
                result = self.agent.extract_test_cases_for_story(story_id)

                return jsonify({
                    'success': result.extraction_successful,
                    'story_id': result.story_id,
                    'story_title': result.story_title,
                    'test_cases': [tc.to_dict() for tc in result.test_cases],
                    'total_test_cases': len(result.test_cases),
                    'error': result.error_message if not result.extraction_successful else None,
                    'preview_mode': True
                })

            except Exception as e:
                self.logger.error(f"Error in preview_test_cases endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                }), 500

        @self.app.route('/api/test-cases/bulk-extract', methods=['POST'])
        def bulk_extract_test_cases():
            """Extract test cases for multiple stories in an epic"""
            try:
                data = request.get_json()
                epic_id = data.get('epic_id', '').strip()
                upload_to_ado = data.get('upload_to_ado', True)

                if not epic_id:
                    return jsonify({
                        'success': False,
                        'error': 'Epic ID is required'
                    }), 400

                # Extract test cases for all stories in the epic
                results = self.agent.extract_test_cases_for_epic_stories(epic_id, upload_to_ado)

                # Process results
                successful_extractions = 0
                total_test_cases = 0
                story_results = []

                for story_id, result in results.items():
                    if result.extraction_successful:
                        successful_extractions += 1
                        total_test_cases += len(result.test_cases)

                    story_results.append({
                        'story_id': result.story_id,
                        'story_title': result.story_title,
                        'success': result.extraction_successful,
                        'test_case_count': len(result.test_cases),
                        'error': result.error_message if not result.extraction_successful else None
                    })

                return jsonify({
                    'success': successful_extractions > 0,
                    'epic_id': epic_id,
                    'total_stories': len(results),
                    'successful_extractions': successful_extractions,
                    'total_test_cases': total_test_cases,
                    'story_results': story_results,
                    'uploaded_to_ado': upload_to_ado
                })

            except Exception as e:
                self.logger.error(f"Error in bulk_extract_test_cases endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                }), 500

        @self.app.route('/api/stories/extract', methods=['POST'])
        def extract_stories():
            """Extract user stories from requirements"""
            try:
                data = request.get_json()
                requirement_id = data.get('requirement_id', '').strip()
                upload_to_ado = data.get('upload_to_ado', True)

                if not requirement_id:
                    return jsonify({
                        'success': False,
                        'error': 'Requirement ID is required'
                    }), 400

                # Extract stories using the agent
                result = self.agent.process_requirement_by_id(requirement_id, upload_to_ado)

                return jsonify({
                    'success': result.extraction_successful,
                    'requirement_id': result.requirement_id,
                    'requirement_title': result.requirement_title,
                    'stories': [story.to_dict() for story in result.stories],
                    'total_stories': len(result.stories),
                    'error': result.error_message if not result.extraction_successful else None,
                    'uploaded_to_ado': upload_to_ado and result.extraction_successful
                })

            except Exception as e:
                self.logger.error(f"Error in extract_stories endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                }), 500

        @self.app.route('/api/stories/preview', methods=['POST'])
        def preview_stories():
            """Preview user stories from requirements without uploading"""
            try:
                data = request.get_json()
                requirement_id = data.get('requirement_id', '').strip()

                if not requirement_id:
                    return jsonify({
                        'success': False,
                        'error': 'Requirement ID is required'
                    }), 400

                # Preview stories without uploading
                result = self.agent.preview_stories(requirement_id)

                return jsonify({
                    'success': result.extraction_successful,
                    'requirement_id': result.requirement_id,
                    'requirement_title': result.requirement_title,
                    'stories': [story.to_dict() for story in result.stories],
                    'total_stories': len(result.stories),
                    'error': result.error_message if not result.extraction_successful else None,
                    'preview_mode': True
                })

            except Exception as e:
                self.logger.error(f"Error in preview_stories endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Internal server error: {str(e)}'
                }), 500

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        self.logger.info(f"Starting Monitor API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Create and configure the Flask application"""
    api = MonitorAPI()
    return api.app


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run the API
    api = MonitorAPI()
    api.run(debug=True)
