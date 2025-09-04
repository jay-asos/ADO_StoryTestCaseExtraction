"""Test script to verify enhanced story creation functionality with complexity analysis."""

import requests
import json
import time
import sys
import os
from config.settings import Settings

def test_auto_story_creation():
    """Test the automatic story creation endpoint with complexity analysis."""
    print("\n=== Starting Story Creation Test ===")
    print("Python executable:", sys.executable)
    print("Current working directory:", os.getcwd())
    print("Testing connection to server...")
    
    # Test server connection
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:8080')
            if response.status_code == 200:
                print(f"Server connection successful (status code: {response.status_code})")
                break
            else:
                print(f"Server responded with unexpected status code: {response.status_code}")
                if i < max_retries - 1:
                    print(f"Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    raise Exception(f"Server did not respond with 200 OK after {max_retries} retries")
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"Connection attempt {i+1} failed. Retrying in 2 seconds...")
                time.sleep(2)
            else:
                raise Exception("Failed to connect to server after all retries.")
    Settings.validate()  # Only validate settings
    
    description = """As a project manager, I want to create a dashboard that displays real-time project metrics
so that I can monitor project progress and make data-driven decisions.

Technical Context:
- Need to implement real-time data updates using WebSockets
- Must integrate with existing monitoring systems
- Requires secure authentication for sensitive metrics
- Performance optimization for large datasets
- Cross-browser compatibility required

Business Requirements:
- Critical for daily operations monitoring
- Must support multiple team views
- Required for quarterly performance reviews
- Integration with existing reporting tools"""

    acceptance_criteria = """Acceptance Criteria:

1. Real-time Dashboard Updates
Given: A project manager is viewing the metrics dashboard
When: New project data is available
Then: The dashboard should update automatically without page refresh
And: The update should occur within 2 seconds of data change

2. Authentication and Authorization
Given: A user attempts to access the dashboard
When: They provide their credentials
Then: They should only see metrics based on their role permissions
And: All sensitive data should be encrypted in transit

3. Performance Under Load
Given: The dashboard is being accessed by 100 concurrent users
When: All users are actively viewing and interacting with the dashboard
Then: The response time should remain under 3 seconds
And: The system should maintain data accuracy

4. Multi-team View Access
Given: A user with multi-team access permissions
When: They switch between different team views
Then: They should see relevant metrics for each selected team
And: The transition should be seamless

5. System Integration
Given: The dashboard is connected to existing monitoring systems
When: Data is updated in any connected system
Then: The dashboard should reflect these changes accurately
And: Maintain data consistency across all systems"""

        # Format acceptance criteria for ADO
    criteria_formatted = []
    current_scenario = []
    
    for line in acceptance_criteria.split("\n"):
        line = line.strip()
        if not line:
            if current_scenario:
                criteria_formatted.append(" ".join(current_scenario))
                current_scenario = []
            continue
        
        if line[0].isdigit() and "." in line:
            if current_scenario:
                criteria_formatted.append(" ".join(current_scenario))
                current_scenario = []
            current_scenario.append(line.split(".", 1)[1].strip())
        elif line.startswith(("Given:", "When:", "Then:", "And:")):
            current_scenario.append(line)
            
    if current_scenario:
        criteria_formatted.append(" ".join(current_scenario))

    # Request payload with new format
    payload = {
        "title": "Implement Real-time Project Metrics Dashboard",  # Using title instead of heading
        "description": description,
        "acceptance_criteria": criteria_formatted,  # Using our cleaned up format
        "work_item_type": "User Story"
    }
    
    print("=== Enhanced Story Creation Test ===")
    print("This test will create a story with:")
    print("- Automatic complexity analysis")
    print("- Story points assignment")
    print("- Initial 'New' status")
    print("- Separate description and acceptance criteria fields")
    print("- Given/When/Then formatted acceptance criteria")

    print("\nMaking request to create story...")
    print("\nPayload:", json.dumps(payload, indent=2))
    
    try:
        # Make request to create story
        print("Sending request to API...")
        response = requests.post(
            'http://localhost:8080/api/stories/enhanced/auto',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Set a longer timeout for story creation
        )
        print(f"Request sent. Response status code: {response.status_code}")
        
        # Process response
        print("\n=== Auto Story Creation Test Results ===")
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("Story Details:")
            print(f"Success: {result.get('success', False)}")
            print(f"Story ID: {result.get('story_id')}\n")
            
            print("Complexity Analysis:")
            print(f"Overall Complexity: {result.get('complexity_level')}")
            print(f"Story Points: {result.get('story_points')}\n")
            
            print("Rationale:")
            print(f"{result.get('rationale')}\n")
            
            print("Message:")
            print(f"{result.get('message')}")
        else:
            print("Error Response:")
            print(f"Status Code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            
    except Exception as e:
        print(f"\nNetwork Error: {str(e)}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_auto_story_creation()
