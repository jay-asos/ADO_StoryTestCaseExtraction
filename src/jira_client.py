"""
JIRA Client for integrating with JIRA Cloud/Server
Handles authentication, work item creation, and queries
"""

import requests
import json
import base64
from typing import List, Dict, Optional, Any
from config.settings import Settings

class JiraClient:
    """JIRA REST API Client"""
    
    def __init__(self, base_url: str = None, username: str = None, token: str = None):
        self.base_url = base_url or Settings.JIRA_BASE_URL
        self.username = username or Settings.JIRA_USERNAME
        self.token = token or Settings.JIRA_TOKEN
        self.project_key = Settings.JIRA_PROJECT_KEY
        
        # Create basic auth header
        credentials = f"{self.username}:{self.token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"[JIRA] Initialized client for {self.base_url}")
    
    def test_connection(self) -> bool:
        """Test JIRA connection and authentication"""
        try:
            url = f"{self.base_url}/rest/api/2/myself"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"[JIRA] Connection successful. User: {user_data.get('displayName', 'Unknown')}")
                return True
            else:
                print(f"[JIRA] Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[JIRA] Connection error: {str(e)}")
            return False
    
    def get_project_info(self, project_key: str = None) -> Optional[Dict]:
        """Get project information"""
        try:
            key = project_key or self.project_key
            url = f"{self.base_url}/rest/api/2/project/{key}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[JIRA] Failed to get project info: {response.status_code}")
                return None
        except Exception as e:
            print(f"[JIRA] Error getting project info: {str(e)}")
            return None
    
    def get_issue_types(self, project_key: str = None) -> List[Dict]:
        """Get available issue types for a project"""
        try:
            key = project_key or self.project_key
            url = f"{self.base_url}/rest/api/2/issue/createmeta"
            params = {'projectKeys': key, 'expand': 'projects.issuetypes'}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data['projects']:
                    return data['projects'][0]['issuetypes']
            return []
        except Exception as e:
            print(f"[JIRA] Error getting issue types: {str(e)}")
            return []
    
    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Get a specific issue by key"""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[JIRA] Failed to get issue {issue_key}: {response.status_code}")
                return None
        except Exception as e:
            print(f"[JIRA] Error getting issue {issue_key}: {str(e)}")
            return None
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search for issues using JQL"""
        try:
            url = f"{self.base_url}/rest/api/2/search"
            data = {
                'jql': jql,
                'maxResults': max_results,
                'fields': ['key', 'summary', 'description', 'issuetype', 'status', 'assignee']
            }
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('issues', [])
            else:
                print(f"[JIRA] Search failed: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"[JIRA] Search error: {str(e)}")
            return []
    
    def create_issue(self, issue_type: str, summary: str, description: str = "", 
                    assignee: str = None, parent_key: str = None) -> Optional[Dict]:
        """Create a new issue"""
        try:
            url = f"{self.base_url}/rest/api/2/issue"
            
            fields = {
                'project': {'key': self.project_key},
                'issuetype': {'name': issue_type},
                'summary': summary,
                'description': description
            }
            
            # Add assignee if provided
            if assignee:
                fields['assignee'] = {'name': assignee}
            
            # Add parent for sub-tasks
            if parent_key:
                fields['parent'] = {'key': parent_key}
            
            data = {'fields': fields}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                print(f"[JIRA] Created issue: {result['key']}")
                return result
            else:
                print(f"[JIRA] Failed to create issue: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[JIRA] Error creating issue: {str(e)}")
            return None
    
    def update_issue(self, issue_key: str, fields: Dict) -> bool:
        """Update an existing issue"""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}"
            data = {'fields': fields}
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code == 204:
                print(f"[JIRA] Updated issue: {issue_key}")
                return True
            else:
                print(f"[JIRA] Failed to update issue: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[JIRA] Error updating issue: {str(e)}")
            return False
    
    def get_epics(self) -> List[Dict]:
        """Get all epics from the project"""
        jql = f"project = {self.project_key} AND issuetype = Epic"
        return self.search_issues(jql)
    
    def get_stories_for_epic(self, epic_key: str) -> List[Dict]:
        """Get all stories linked to an epic"""
        jql = f"project = {self.project_key} AND 'Epic Link' = {epic_key}"
        return self.search_issues(jql)
    
    def create_story(self, summary: str, description: str, epic_key: str = None) -> Optional[Dict]:
        """Create a user story"""
        issue_type = Settings.JIRA_USER_STORY_TYPE
        story = self.create_issue(issue_type, summary, description)
        
        # Link to epic if provided
        if story and epic_key:
            self.link_to_epic(story['key'], epic_key)
        
        return story
    
    def create_test_case(self, summary: str, description: str, parent_key: str = None) -> Optional[Dict]:
        """Create a test case"""
        issue_type = Settings.JIRA_TEST_CASE_TYPE
        return self.create_issue(issue_type, summary, description, parent_key=parent_key)
    
    def link_to_epic(self, issue_key: str, epic_key: str) -> bool:
        """Link an issue to an epic"""
        try:
            # Update the Epic Link field
            fields = {'customfield_10014': epic_key}  # Standard Epic Link field ID
            return self.update_issue(issue_key, fields)
        except Exception as e:
            print(f"[JIRA] Error linking to epic: {str(e)}")
            return False
    
    def get_issue_transitions(self, issue_key: str) -> List[Dict]:
        """Get available transitions for an issue"""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('transitions', [])
            return []
        except Exception as e:
            print(f"[JIRA] Error getting transitions: {str(e)}")
            return []
    
    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """Transition an issue to a new status"""
        try:
            url = f"{self.base_url}/rest/api/2/issue/{issue_key}/transitions"
            data = {'transition': {'id': transition_id}}
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 204:
                print(f"[JIRA] Transitioned issue {issue_key}")
                return True
            else:
                print(f"[JIRA] Failed to transition issue: {response.status_code}")
                return False
        except Exception as e:
            print(f"[JIRA] Error transitioning issue: {str(e)}")
            return False
