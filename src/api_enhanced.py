from flask import Flask, request, jsonify
from src.enhanced_story_creator import EnhancedStoryCreator
from src.models_enhanced import EnhancedUserStory
from src.ado_client import ADOClient
from config.settings import Settings

app = Flask(__name__)
app.debug = False  # Disable debug mode
story_creator = EnhancedStoryCreator()
ado_client = ADOClient()

# Configure port
PORT = 8080

@app.route('/')
def test_connection():
    """Test endpoint to verify server is up"""
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/api/stories/enhanced/auto', methods=['POST'])
def create_enhanced_story():
    """Create an enhanced story with complexity analysis and upload to ADO"""
    try:
        app.logger.info("Received request for story creation")
        data = request.get_json()
        if not data:
            app.logger.error("No data provided in request")
            return jsonify({"error": "No data provided", "success": False}), 400
            
        app.logger.info("Received data:", extra={'data': data})
        
        # Extract data from request - try both title and heading
        title = data.get('title') or data.get('heading')  # Support both field names
        description = data.get('description')
        acceptance_criteria = data.get('acceptance_criteria', [])
        work_item_type = data.get('work_item_type', Settings.STORY_EXTRACTION_TYPE)  # Use configured default type
        
        # Validate required fields
        if not title or not acceptance_criteria:
            app.logger.error(f"Missing required fields. Title present: {bool(title)}, AC present: {bool(acceptance_criteria)}")
            return jsonify({"error": "Missing required fields", "success": False}), 400
            
        # Create enhanced story with complexity analysis
        app.logger.info("Creating enhanced story with input data", extra={
            'title': title,
            'description': description,
            'acceptance_criteria': acceptance_criteria
        })
        
        # Ensure the data is in the right format
        if isinstance(acceptance_criteria, str):
            acceptance_criteria = acceptance_criteria.split('\n')
        elif not isinstance(acceptance_criteria, list):
            app.logger.error(f"Invalid acceptance criteria format. Expected string or list, got {type(acceptance_criteria)}")
            return jsonify({"error": "Invalid acceptance criteria format", "success": False}), 400
            
        try:
            app.logger.info("Calling story creator with prepared data", extra={
                'heading': title,
                'description': description,
                'acceptance_criteria': acceptance_criteria
            })
            story = story_creator.create_enhanced_story(
                heading=title,  # Using title as heading
                description=description,
                acceptance_criteria=acceptance_criteria
            )
        except Exception as e:
            app.logger.error(f"Error creating enhanced story: {str(e)}")
            return jsonify({"error": "Failed to create enhanced story", "details": str(e), "success": False}), 500
        
        # Convert to ADO format
        app.logger.info("Converting story to ADO format")
        try:
            story_data = story.to_ado_format()
        except Exception as e:
            app.logger.error(f"Error converting story to ADO format: {str(e)}")
            return jsonify({"error": "Failed to convert story to ADO format", "details": str(e), "success": False}), 500
        
        # Create work item in ADO with specified type
        app.logger.info(f"Creating work item in ADO with type: {work_item_type}")
        try:
            work_item = ado_client.create_user_story(story_data, item_type=work_item_type)
        except Exception as e:
            app.logger.error(f"Error creating ADO work item: {str(e)}")
            return jsonify({"error": "Failed to create ADO work item", "details": str(e), "success": False}), 500
        
        if not work_item:
            return jsonify({
                "error": f"Failed to create work item of type {work_item_type}",
                "success": False
            }), 500
            
        # Get the created work item URL
        work_item_url = f"https://dev.azure.com/{Settings.ADO_ORGANIZATION}/{Settings.ADO_PROJECT}/_workitems/edit/{work_item.id}"
        
        return jsonify({
            "success": True,
            "story_id": work_item.id,
            "story_url": work_item_url,
            "message": "Story created successfully",
            "complexity_level": str(story.complexity_analysis.overall_complexity),
            "story_points": story.complexity_analysis.story_points,
            "rationale": story.complexity_analysis.rationale
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

if __name__ == '__main__':
    Settings.validate()
    app.run(host='0.0.0.0', port=PORT)  # Using PORT=8080 defined at the top
