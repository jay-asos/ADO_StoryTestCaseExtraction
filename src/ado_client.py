import base64
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from config.settings import Settings
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient
from msrest.authentication import BasicAuthentication

from config.settings import Settings
from src.models import Requirement, ExistingUserStory, RequirementSnapshot

class ADOClient:
    """Client for interacting with Azure DevOps APIs"""
    
    def __init__(self):
        Settings.validate()
        self.organization = Settings.ADO_ORGANIZATION
        self.project = Settings.ADO_PROJECT
        self.pat = Settings.ADO_PAT
        self.base_url = f"https://dev.azure.com/{self.organization}"

        try:
            print("[DEBUG] Initializing work item tracking client...")
            # Create credentials
            credentials = BasicAuthentication('', self.pat)

            # Create work item tracking client directly
            self.wit_client = WorkItemTrackingClient(
                base_url=self.base_url,
                creds=credentials
            )
            print("[DEBUG] Work item tracking client created successfully")
        except Exception as e:
            raise Exception(f"Failed to establish connection to Azure DevOps: {str(e)}")

    def get_requirements(self, state_filter: Optional[str] = None, work_item_type: Optional[str] = None) -> List[Requirement]:
        """Get all requirements from the project, optionally filtered by work item type (e.g., 'Epic')."""
        try:
            # Build WIQL query
            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.Description], [System.State]
            FROM WorkItems
            WHERE [System.TeamProject] = '{self.project}'
            """
            if work_item_type:
                wiql_query += f" AND [System.WorkItemType] = '{work_item_type}'"
            else:
                wiql_query += f" AND [System.WorkItemType] = '{Settings.REQUIREMENT_TYPE}'"
            if state_filter:
                wiql_query += f" AND [System.State] = '{state_filter}'"
            # Execute query
            wiql_result = self.wit_client.query_by_wiql({"query": wiql_query})
            if not wiql_result.work_items:
                return []
            # Get work item IDs
            work_item_ids = [item.id for item in wiql_result.work_items]
            # Get full work items
            work_items = self.wit_client.get_work_items(
                ids=work_item_ids,
                fields=["System.Id", "System.Title", "System.Description", "System.State"]
            )
            requirements = []
            for item in work_items:
                fields = item.fields
                requirement = Requirement(
                    id=str(item.id),  # Ensure id is always a string
                    title=fields.get("System.Title", ""),
                    description=fields.get("System.Description", ""),
                    state=fields.get("System.State", ""),
                    url=item.url
                )
                requirements.append(requirement)
            return requirements
        except Exception as e:
            raise Exception(f"Failed to get requirements: {str(e)}")
    
    def get_requirement_by_id(self, requirement_id: str) -> Optional[Requirement]:
        """Get a single requirement by string ID with detailed error messages"""
        try:
            work_item = self.wit_client.get_work_item(id=requirement_id)
            if not work_item:
                print(f"[ERROR] No work item found for ID: {requirement_id}")
                return None
            return Requirement.from_ado_work_item(work_item)
        except Exception as e:
            print(f"[AUTH/ADO ERROR] Failed to fetch requirement '{requirement_id}': {e}.\n"
                  f"Check if your PAT is valid, has correct permissions, and if the organization/project/ID are correct.")
            return None

    def create_user_story(self, story_data: Dict[str, Any], parent_requirement_id: Optional[int] = None, item_type: Optional[str] = None) -> Any:
        """Create a user story with the specified type"""
        try:
            print(f"[DEBUG] Creating {story_data}")
            
            # Prepare document for create
            document = []
            for field, value in story_data.items():
                document.append({
                    "op": "add",
                    "path": f"/fields/{field}",
                    "value": value
                })
            
            print(f"[DEBUG] Document prepared for Azure DevOps: {document}")
            
            # Create the work item
            work_item = self.wit_client.create_work_item(
                document=document,
                project=self.project,
                type=item_type or Settings.STORY_EXTRACTION_TYPE or "Task"  # Use provided type, fallback to config, then Task
            )
            
            print(f"[DEBUG] Successfully created work item with ID: {work_item.id}")
            
            # Create parent-child relationship if needed
            if parent_requirement_id:
                try:
                    print(f"[DEBUG] Creating parent-child link for {work_item.id}")
                    self._create_parent_child_link(parent_requirement_id, work_item.id)
                except Exception as e:
                    print(f"[WARNING] Failed to create parent-child link: {str(e)}")
                    
            return work_item
            
        except Exception as e:
            print(f"[ERROR] Error in create_user_story: {str(e)}")
            raise

    def _create_parent_child_link(self, parent_id: int, child_id: int):
        """Create a parent-child relationship between work items"""
        try:
            # Create the link
            document = [{
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Forward",
                    "url": f"{self.base_url}/{self.organization}/_apis/wit/workItems/{child_id}"
                }
            }]
            
            self.wit_client.update_work_item(
                document=document,
                id=parent_id
            )
            
        except Exception as e:
            raise Exception(f"Failed to create parent-child link: {str(e)}")
    
    def detect_changes_in_epic(self, epic_id: int) -> Optional[RequirementSnapshot]:
        """Detect changes in an EPIC based on its requirement snapshot"""
        try:
            work_item = self.wit_client.get_work_item(
                id=epic_id,
                fields=["System.Id", "System.Title", "System.Description", "System.State", "System.ChangedDate"]
            )
            
            fields = work_item.fields
            
            # Calculate a hash of the title and description for change detection
            title = fields.get("System.Title", "")
            description = fields.get("System.Description", "")
            content_hash = hashlib.sha256((title + description).encode()).hexdigest()
            
            return RequirementSnapshot(
                id=work_item.id,
                title=title,
                description=description,
                state=fields.get("System.State", ""),
                last_modified=datetime.strptime(fields.get("System.ChangedDate", "2000-01-01T00:00:00.000Z"), "%Y-%m-%dT%H:%M:%S.%fZ"),
                content_hash=content_hash
            )
            
        except Exception as e:
            raise Exception(f"Failed to detect changes in EPIC {epic_id}: {str(e)}")

    def get_existing_user_stories(self, epic_id: int) -> List[ExistingUserStory]:
        """Retrieve existing user stories for a given epic ID"""
        try:
            child_ids = self.get_child_stories(epic_id)
            stories = []
            if child_ids:
                work_items = self.wit_client.get_work_items(
                    ids=child_ids,
                    fields=["System.Id", "System.Title", "System.Description", "System.State"]
                )
                for item in work_items:
                    fields = item.fields
                    story = ExistingUserStory(
                        id=item.id,
                        title=fields.get("System.Title", ""),
                        description=fields.get("System.Description", ""),
                        state=fields.get("System.State", ""),
                        parent_id=epic_id
                    )
                    stories.append(story)
            return stories
        except Exception as e:
            raise Exception(f"Failed to retrieve existing user stories for epic {epic_id}: {str(e)}")

    def get_child_stories(self, requirement_id: int) -> List[int]:
        """Get all child user stories for a requirement"""
        try:
            work_item = self.wit_client.get_work_item(
                id=requirement_id,
                expand="Relations"
            )
            child_ids = []
            if work_item.relations:
                for relation in work_item.relations:
                    if relation.rel == "System.LinkTypes.Hierarchy-Forward":
                        url_parts = relation.url.split('/')
                        child_id = int(url_parts[-1])
                        child_ids.append(child_id)
            return child_ids
        except Exception as e:
            raise Exception(f"Failed to get child stories for requirement {requirement_id}: {str(e)}")

    def get_child_work_items(self, parent_id: int) -> List[Dict[str, Any]]:
        """Get all child work items for a parent work item"""
        try:
            work_item = self.wit_client.get_work_item(
                id=parent_id,
                expand="Relations"
            )
            child_work_items = []
            if work_item.relations:
                child_ids = []
                for relation in work_item.relations:
                    if relation.rel == "System.LinkTypes.Hierarchy-Forward":
                        url_parts = relation.url.split('/')
                        child_id = int(url_parts[-1])
                        child_ids.append(child_id)
                
                if child_ids:
                    children = self.wit_client.get_work_items(
                        ids=child_ids,
                        fields=["System.Id", "System.Title", "System.WorkItemType", "System.State"]
                    )
                    for child in children:
                        child_work_items.append({
                            'id': child.id,
                            'title': child.fields.get('System.Title', ''),
                            'type': child.fields.get('System.WorkItemType', ''),
                            'state': child.fields.get('System.State', '')
                        })
            return child_work_items
        except Exception as e:
            raise Exception(f"Failed to get child work items for parent {parent_id}: {str(e)}")

    def get_requirement_by_id(self, requirement_id) -> Optional[Requirement]:
        """Get a single requirement by numeric ID or by title if not numeric"""
        try:
            # Try to convert to int for numeric IDs
            try:
                numeric_id = int(requirement_id)
                work_item = self.wit_client.get_work_item(id=numeric_id)
                if not work_item:
                    print(f"[ERROR] No work item found for ID: {requirement_id}")
                    return None
                return Requirement.from_ado_work_item(work_item)
            except ValueError:
                # Not a numeric ID, search by title
                print(f"[INFO] Requirement ID '{requirement_id}' is not numeric. Searching by title...")
                wiql_query = f"""
                SELECT [System.Id], [System.Title], [System.Description], [System.State]
                FROM WorkItems
                WHERE [System.Title] = '{requirement_id}'
                AND [System.TeamProject] = '{self.project}'
                """
                wiql_result = self.wit_client.query_by_wiql({"query": wiql_query})
                if not wiql_result.work_items:
                    print(f"[ERROR] No work item found with title: {requirement_id}")
                    return None
                work_item_id = wiql_result.work_items[0].id
                work_item = self.wit_client.get_work_item(id=work_item_id)
                return Requirement.from_ado_work_item(work_item)
        except Exception as e:
            print(f"[ERROR] Failed to get requirement by id or title: {str(e)}")
            return None

    def update_work_item(self, work_item_id: int, update_data: Dict[str, Any]) -> bool:
        """Update an existing work item"""
        try:
            # Prepare update document
            document = []
            for field, value in update_data.items():
                document.append({
                    "op": "replace",
                    "path": f"/fields/{field}",
                    "value": value
                })
            
            # Update the work item
            self.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to update work item {work_item_id}: {str(e)}")
    
    def get_work_item_types(self) -> List[str]:
        """Get all available work item types in the project"""
        try:
            work_item_types = self.wit_client.get_work_item_types(project=self.project)
            return [wit.name for wit in work_item_types]
        except Exception as e:
            raise Exception(f"Failed to get work item types: {str(e)}")

    def create_test_case(self, test_case_data: Dict[str, Any], parent_story_id: str) -> int:
        """Create a test case and link it to a parent user story"""
        try:
            print(f"[DEBUG] Attempting to create test case for parent story {parent_story_id}")
            
            # Prepare work item data for test case
            document = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": test_case_data.get("System.Title", "New Test Case")
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": test_case_data.get("System.Description", "")
                }
            ]

            # Add any additional fields from test_case_data
            for field, value in test_case_data.items():
                if field not in ["System.Title", "System.Description"]:
                    document.append({
                        "op": "add",
                        "path": f"/fields/{field}",
                        "value": value
                    })

            print(f"[DEBUG] Test case document prepared for Azure DevOps: {document}")

            # Create the test case work item
            try:
                work_item = self.wit_client.create_work_item(
                    document=document,
                    project=self.project,
                    type="Test Case"  # Standard ADO test case work item type
                )
                print(f"[DEBUG] Successfully created test case with ID: {work_item.id}")
            except Exception as e:
                print(f"[ERROR] Failed to create test case work item: {str(e)}")
                raise Exception(f"Failed to create test case work item: {str(e)}")

            # Create parent-child relationship with the user story
            if parent_story_id:
                try:
                    print(f"[DEBUG] Creating parent-child link between story {parent_story_id} and test case {work_item.id}")
                    self._create_parent_child_link(int(parent_story_id), work_item.id)
                except Exception as e:
                    print(f"[WARNING] Failed to create parent-child link for test case: {str(e)}")
                    # Don't raise here, as the test case was created successfully

            return work_item.id
            
        except Exception as e:
            print(f"[ERROR] Error in create_test_case: {str(e)}")
            raise

    def create_test_case_as_issue(self, test_case_data: Dict[str, Any], parent_story_id: Optional[int] = None) -> int:
        """Create a test case as an Issue work item in Azure DevOps"""
        try:
            print(f"[DEBUG] Creating test case as Issue: {test_case_data.get('title', 'Unknown')}")

            # Prepare the document for Issue creation
            document = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": f"[TEST] {test_case_data.get('title', '')}"
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": self._format_test_case_description(test_case_data)
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": self._map_priority_to_number(test_case_data.get('priority', 'Medium'))
                },
                {
                    "op": "add",
                    "path": "/fields/System.Tags",
                    "value": f"TestCase;{test_case_data.get('test_type', 'functional')};AutoGenerated"
                }
            ]

            print(f"[DEBUG] Document prepared for test case Issue: {document}")

            # Create the Issue work item
            try:
                work_item = self.wit_client.create_work_item(
                    document=document,
                    project=self.project,
                    type="Issue"
                )
                print(f"[DEBUG] Successfully created test case Issue with ID: {work_item.id}")
            except Exception as e:
                print(f"[ERROR] Failed to create test case Issue: {str(e)}")
                print(f"[DEBUG] Project: {self.project}")
                print(f"[DEBUG] Type: Issue")
                raise Exception(f"Failed to create test case Issue: {str(e)}")

            # Create parent-child relationship if parent_story_id is provided
            if parent_story_id:
                try:
                    print(f"[DEBUG] Creating parent-child link between {parent_story_id} and {work_item.id}")
                    self._create_parent_child_link(parent_story_id, work_item.id)
                except Exception as e:
                    print(f"[WARNING] Failed to create parent-child link: {str(e)}")
                    # Don't raise here, as the test case Issue was created successfully

            return work_item.id

        except Exception as e:
            print(f"[ERROR] Error in create_test_case_as_issue: {str(e)}")
            raise

    def create_test_case_with_config(self, test_case_data: Dict[str, Any], parent_story_id: Optional[int] = None) -> int:
        """Create a test case using the configured work item type (Issue or Test Case)"""
        if Settings.TEST_CASE_EXTRACTION_TYPE.lower() == 'issue':
            return self.create_test_case_as_issue(test_case_data, parent_story_id)
        else:
            # Use traditional Test Case work item type
            return self.create_test_case_as_test_case(test_case_data, parent_story_id)

    def create_test_case_as_test_case(self, test_case_data: Dict[str, Any], parent_story_id: Optional[int] = None) -> int:
        """Create a test case as a Test Case work item in Azure DevOps"""
        try:
            print(f"[DEBUG] Creating test case as Test Case: {test_case_data.get('title', 'Unknown')}")

            # Prepare the document for Test Case creation
            document = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": test_case_data.get('title', '')
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": self._format_test_case_description(test_case_data)
                },
                {
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.Priority",
                    "value": self._map_priority_to_number(test_case_data.get('priority', 'Medium'))
                }
            ]

            print(f"[DEBUG] Document prepared for Test Case: {document}")

            # Create the Test Case work item
            try:
                work_item = self.wit_client.create_work_item(
                    document=document,
                    project=self.project,
                    type="Test Case"
                )
                print(f"[DEBUG] Successfully created Test Case with ID: {work_item.id}")
            except Exception as e:
                print(f"[ERROR] Failed to create Test Case: {str(e)}")
                raise Exception(f"Failed to create Test Case: {str(e)}")

            # Create parent-child relationship if parent_story_id is provided
            if parent_story_id:
                try:
                    print(f"[DEBUG] Creating parent-child link between {parent_story_id} and {work_item.id}")
                    self._create_parent_child_link(parent_story_id, work_item.id)
                except Exception as e:
                    print(f"[WARNING] Failed to create parent-child link: {str(e)}")

            return work_item.id

        except Exception as e:
            print(f"[ERROR] Error in create_test_case_as_test_case: {str(e)}")
            raise

    def create_work_item(self, work_item_type: str, title: str = None, description: str = None, additional_fields: Optional[Dict[str, Any]] = None, fields: Optional[Dict[str, Any]] = None, parent_id: Optional[int] = None) -> Dict[str, Any]:
        """Generic method to create any type of work item
        
        Supports both old interface (title, description, additional_fields) and new interface (fields, parent_id)
        """
        try:
            # Handle new interface with fields parameter
            if fields is not None:
                title = fields.get('System.Title', title)
                description = fields.get('System.Description', description)
                # Use fields as additional_fields, excluding System.Title and System.Description
                additional_fields = {k: v for k, v in fields.items() 
                                   if k not in ['System.Title', 'System.Description']}
            
            # Default values if not provided
            if title is None:
                title = "New Work Item"
            if description is None:
                description = ""
            
            print(f"[DEBUG] Creating {work_item_type} work item: {title}")

            # Prepare the basic document
            document = [
                {
                    "op": "add",
                    "path": "/fields/System.Title",
                    "value": title
                },
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": description
                }
            ]

            # Add any additional fields
            if additional_fields:
                for field, value in additional_fields.items():
                    if field not in ["System.Title", "System.Description"]:
                        document.append({
                            "op": "add",
                            "path": f"/fields/{field}",
                            "value": value
                        })

            print(f"[DEBUG] Document prepared for {work_item_type}: {document}")

            # Create the work item
            try:
                work_item = self.wit_client.create_work_item(
                    document=document,
                    project=self.project,
                    type=work_item_type
                )
                print(f"[DEBUG] Successfully created {work_item_type} with ID: {work_item.id}")
            except Exception as e:
                print(f"[ERROR] Failed to create {work_item_type}: {str(e)}")
                print(f"[DEBUG] Project: {self.project}")
                print(f"[DEBUG] Type: {work_item_type}")
                raise Exception(f"Failed to create {work_item_type}: {str(e)}")

            # Create parent-child relationship if parent_id is provided
            if parent_id:
                try:
                    print(f"[DEBUG] Creating parent-child link between {parent_id} and {work_item.id}")
                    self._create_parent_child_link(parent_id, work_item.id)
                except Exception as e:
                    print(f"[WARNING] Failed to create parent-child link: {str(e)}")
                    # Don't raise here, as the work item was created successfully

            # Return work item data in the expected format
            return {
                'id': work_item.id,
                'fields': work_item.fields if hasattr(work_item, 'fields') else {},
                'url': work_item.url if hasattr(work_item, 'url') else ''
            }

        except Exception as e:
            print(f"[ERROR] Error in create_work_item: {str(e)}")
            raise

    def _format_test_case_description(self, test_case_data: Dict[str, Any]) -> str:
        """Format test case data into a comprehensive description for Issue work item"""
        description_parts = []

        # Test case description
        if test_case_data.get('description'):
            description_parts.append(f"**Test Description:**\n{test_case_data['description']}")

        # Test type
        if test_case_data.get('test_type'):
            description_parts.append(f"**Test Type:** {test_case_data['test_type'].title()}")

        # Preconditions
        if test_case_data.get('preconditions'):
            preconditions_text = "\n".join([f"- {pc}" for pc in test_case_data['preconditions']])
            description_parts.append(f"**Preconditions:**\n{preconditions_text}")

        # Test steps
        if test_case_data.get('test_steps'):
            steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(test_case_data['test_steps'])])
            description_parts.append(f"**Test Steps:**\n{steps_text}")

        # Expected result
        if test_case_data.get('expected_result'):
            description_parts.append(f"**Expected Result:**\n{test_case_data['expected_result']}")

        return "\n\n".join(description_parts)

    def _map_priority_to_number(self, priority_text: str) -> int:
        """Map priority text to Azure DevOps priority number"""
        priority_mapping = {
            'High': 1,
            'Medium': 2,
            'Low': 3
        }
        return priority_mapping.get(priority_text, 2)

    def get_work_item(self, work_item_id: int):
        """Get a work item by ID (compatibility method for monitor)"""
        try:
            work_item = self.wit_client.get_work_item(
                id=work_item_id,
                fields=["System.Id", "System.Title", "System.Description", "System.WorkItemType", "System.State"]
            )
            return work_item
        except Exception as e:
            raise Exception(f"Failed to get work item {work_item_id}: {str(e)}")

    def get_work_item_by_id(self, work_item_id: str):
        """Get a work item by ID with work item type information"""
        try:
            numeric_id = int(work_item_id)
            work_item = self.wit_client.get_work_item(
                id=numeric_id,
                fields=["System.Id", "System.Title", "System.Description", "System.WorkItemType", "System.State"]
            )
            return work_item
        except ValueError:
            raise Exception(f"Invalid work item ID: {work_item_id}")
        except Exception as e:
            raise Exception(f"Failed to get work item {work_item_id}: {str(e)}")

    def get_work_item_type(self, work_item_id: str) -> str:
        """Get the work item type for a specific work item ID"""
        try:
            work_item = self.get_work_item_by_id(work_item_id)
            return work_item.fields.get("System.WorkItemType", "Unknown")
        except Exception as e:
            raise Exception(f"Failed to get work item type for {work_item_id}: {str(e)}")

    def is_valid_work_item_for_test_extraction(self, work_item_id: str) -> tuple[bool, str]:
        """Check if a work item is valid for test case extraction"""
        try:
            work_item_type = self.get_work_item_type(work_item_id)

            # Define allowed work item types for test case extraction
            allowed_types = ['User Story', 'Task']

            if work_item_type in allowed_types:
                return True, work_item_type
            else:
                return False, work_item_type

        except Exception as e:
            return False, f"Error: {str(e)}"
