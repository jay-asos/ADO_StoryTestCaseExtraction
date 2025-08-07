#!/usr/bin/env python3
"""
Demo script showcasing the Enhanced ADO Story Extractor with EPIC change detection
and synchronization capabilities.

This demo simulates the workflow without requiring actual ADO credentials.
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

# Mock classes to simulate the functionality
class MockUserStory:
    def __init__(self, heading: str, description: str, acceptance_criteria: List[str]):
        self.heading = heading
        self.description = description
        self.acceptance_criteria = acceptance_criteria
    
    def to_ado_format(self) -> dict:
        acceptance_criteria_html = "<br>".join([f"• {criteria}" for criteria in self.acceptance_criteria])
        full_description = f"{self.description}<br><br><strong>Acceptance Criteria:</strong><br>{acceptance_criteria_html}"
        
        return {
            "System.Title": self.heading,
            "System.Description": full_description
        }

class MockExistingUserStory:
    def __init__(self, id: int, title: str, description: str, state: str = "Active"):
        self.id = id
        self.title = title
        self.description = description
        self.state = state

class MockEpicSyncResult:
    def __init__(self, epic_id: str, epic_title: str, sync_successful: bool = True):
        self.epic_id = epic_id
        self.epic_title = epic_title
        self.sync_successful = sync_successful
        self.created_stories = []
        self.updated_stories = []
        self.unchanged_stories = []
        self.error_message = None

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"🎯 {title}")
    print("=" * 80)

def print_subheader(title: str):
    print(f"\n📋 {title}")
    print("-" * 40)

def create_sample_epic_content():
    """Create sample EPIC content for demonstration"""
    return {
        "id": 12345,
        "title": "User Authentication and Profile Management System",
        "description": """
        Implement a comprehensive user authentication system that allows users to:
        - Register new accounts with email verification
        - Login securely with username/password or social media
        - Manage their profile information
        - Reset passwords when forgotten
        - Enable two-factor authentication for enhanced security
        
        The system should support multiple authentication providers and maintain
        user session management with proper security measures.
        """,
        "state": "Active"
    }

def create_extracted_stories() -> List[MockUserStory]:
    """Create sample user stories extracted from the EPIC"""
    return [
        MockUserStory(
            heading="User Registration with Email Verification",
            description="As a new user, I want to register an account with email verification so that I can securely access the system",
            acceptance_criteria=[
                "User can enter email, username, and password on registration form",
                "System sends verification email with unique token",
                "User can click verification link to activate account",
                "Account remains inactive until email is verified",
                "System shows appropriate success/error messages"
            ]
        ),
        MockUserStory(
            heading="Secure User Login",
            description="As a registered user, I want to login securely so that I can access my account",
            acceptance_criteria=[
                "User can enter username/email and password",
                "System validates credentials against database",
                "Successful login redirects to user dashboard",
                "Failed login shows appropriate error message",
                "System implements rate limiting for security"
            ]
        ),
        MockUserStory(
            heading="Social Media Authentication",
            description="As a user, I want to login using my social media accounts so that I can access the system quickly",
            acceptance_criteria=[
                "System supports Google OAuth integration",
                "System supports Facebook OAuth integration", 
                "User can link multiple social accounts to one profile",
                "First-time social login creates new user account",
                "Social login maintains same security standards"
            ]
        ),
        MockUserStory(
            heading="Profile Management",
            description="As a logged-in user, I want to manage my profile information so that my account details are current",
            acceptance_criteria=[
                "User can view current profile information",
                "User can edit name, email, and other personal details",
                "System validates email format and uniqueness",
                "Changes are saved and confirmed to user",
                "User can upload and update profile picture"
            ]
        ),
        MockUserStory(
            heading="Password Reset Functionality",
            description="As a user who forgot their password, I want to reset it securely so that I can regain access to my account",
            acceptance_criteria=[
                "User can request password reset via email",
                "System sends secure reset link with expiration",
                "Reset link allows user to set new password",
                "Old password is invalidated after reset",
                "User receives confirmation of password change"
            ]
        ),
        MockUserStory(
            heading="Two-Factor Authentication",
            description="As a security-conscious user, I want to enable two-factor authentication so that my account is more secure",
            acceptance_criteria=[
                "User can enable 2FA in account settings",
                "System supports TOTP authenticator apps",
                "User can generate and save backup codes",
                "2FA is required on login when enabled",
                "User can disable 2FA with proper verification"
            ]
        )
    ]

def create_existing_stories() -> List[MockExistingUserStory]:
    """Create sample existing stories that are already in ADO"""
    return [
        MockExistingUserStory(
            id=101,
            title="User Registration Feature",  # Similar but not exact match
            description="Basic user registration functionality"
        ),
        MockExistingUserStory(
            id=102,
            title="User Login System",  # Similar match
            description="Allow users to login with credentials"
        ),
        MockExistingUserStory(
            id=103,
            title="Password Recovery",  # Similar match
            description="Help users recover forgotten passwords"
        )
    ]

def analyze_story_changes(existing_stories: List[MockExistingUserStory], 
                         new_stories: List[MockUserStory]):
    """Demo version of story change analysis"""
    from difflib import SequenceMatcher
    
    stories_to_create = []
    stories_to_update = []
    unchanged_stories = []
    
    existing_by_title = {story.title: story for story in existing_stories}
    
    print_subheader("Analyzing Story Changes")
    
    for new_story in new_stories:
        best_match = None
        best_similarity = 0.0
        
        # Find best matching existing story
        for existing_title, existing_story in existing_by_title.items():
            similarity = SequenceMatcher(None, new_story.heading.lower(), existing_title.lower()).ratio()
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing_story
        
        print(f"\n🔍 Analyzing: '{new_story.heading}'")
        
        if best_match and best_similarity > 0.6:  # Lowered threshold for demo
            print(f"   📝 Best match: '{best_match.title}' (similarity: {best_similarity:.2f})")
            
            # Check content similarity
            existing_content = f"{best_match.title} {best_match.description}"
            new_content = f"{new_story.heading} {new_story.description} {' '.join(new_story.acceptance_criteria)}"
            content_similarity = SequenceMatcher(None, existing_content.lower(), new_content.lower()).ratio()
            
            print(f"   📊 Content similarity: {content_similarity:.2f}")
            
            if content_similarity < 0.5:  # Lowered threshold for demo
                stories_to_update.append({
                    'id': best_match.id,
                    'existing_story': best_match,
                    'new_story': new_story
                })
                print(f"   🔄 Action: UPDATE (content changed significantly)")
                del existing_by_title[best_match.title]
            else:
                unchanged_stories.append(best_match)
                print(f"   ⏸️  Action: NO CHANGE (content similar)")
                del existing_by_title[best_match.title]
        else:
            stories_to_create.append(new_story)
            print(f"   ✨ Action: CREATE (no similar existing story)")
    
    # Remaining existing stories
    for remaining_story in existing_by_title.values():
        unchanged_stories.append(remaining_story)
        print(f"\n📋 Existing story '{remaining_story.title}' remains unchanged")
    
    return stories_to_create, stories_to_update, unchanged_stories

def demonstrate_change_detection():
    """Demonstrate the change detection process"""
    print_header("EPIC Change Detection Demo")
    
    # Sample EPIC content
    epic = create_sample_epic_content()
    print(f"🎯 EPIC: {epic['title']}")
    print(f"📝 Description: {epic['description'][:100]}...")
    
    # Calculate content hash for change detection
    content_hash = hashlib.sha256((epic['title'] + epic['description']).encode()).hexdigest()
    print(f"🔐 Content Hash: {content_hash[:16]}...")
    
    # Simulate previous snapshot
    previous_hash = "a1b2c3d4e5f6g7h8"  # Simulated different hash
    print(f"🔍 Previous Hash: {previous_hash}")
    
    has_changes = content_hash[:16] != previous_hash
    print(f"🚨 Changes Detected: {'YES' if has_changes else 'NO'}")
    
    return epic, has_changes

def demonstrate_story_extraction():
    """Demonstrate story extraction from EPIC"""
    print_header("Story Extraction from EPIC")
    
    extracted_stories = create_extracted_stories()
    print(f"📊 Extracted {len(extracted_stories)} stories from EPIC:")
    
    for i, story in enumerate(extracted_stories, 1):
        print(f"\n{i}. 📝 {story.heading}")
        print(f"   Description: {story.description[:80]}...")
        print(f"   Acceptance Criteria: {len(story.acceptance_criteria)} items")
        
        # Show first few acceptance criteria
        for j, criteria in enumerate(story.acceptance_criteria[:3], 1):
            print(f"      {j}) {criteria}")
        if len(story.acceptance_criteria) > 3:
            print(f"      ... and {len(story.acceptance_criteria) - 3} more")
    
    return extracted_stories

def demonstrate_synchronization():
    """Demonstrate the synchronization process"""
    print_header("EPIC Synchronization Process")
    
    # Get existing stories from "ADO"
    existing_stories = create_existing_stories()
    new_stories = create_extracted_stories()
    
    print(f"📋 Found {len(existing_stories)} existing stories in ADO:")
    for story in existing_stories:
        print(f"   • {story.id}: {story.title}")
    
    print(f"\n🆕 Extracted {len(new_stories)} new stories from updated EPIC")
    
    # Analyze changes
    stories_to_create, stories_to_update, unchanged_stories = analyze_story_changes(
        existing_stories, new_stories
    )
    
    print_subheader("Synchronization Plan")
    print(f"✨ Stories to CREATE: {len(stories_to_create)}")
    print(f"🔄 Stories to UPDATE: {len(stories_to_update)}")
    print(f"⏸️  Stories UNCHANGED: {len(unchanged_stories)}")
    
    # Simulate sync result
    sync_result = MockEpicSyncResult("12345", "User Authentication and Profile Management System")
    
    # Simulate creating new stories
    for story in stories_to_create:
        new_id = 200 + len(sync_result.created_stories)
        sync_result.created_stories.append(new_id)
        print(f"✨ Created story {new_id}: {story.heading}")
    
    # Simulate updating existing stories
    for update_info in stories_to_update:
        story_id = update_info['id']
        sync_result.updated_stories.append(story_id)
        print(f"🔄 Updated story {story_id}: {update_info['new_story'].heading}")
    
    # Simulate unchanged stories
    for story in unchanged_stories:
        sync_result.unchanged_stories.append(story.id)
    
    return sync_result

def demonstrate_ado_format():
    """Demonstrate the ADO formatting with HTML"""
    print_header("ADO Format Demo - HTML Formatting for Acceptance Criteria")
    
    sample_story = MockUserStory(
        heading="User Registration with Email Verification",
        description="As a new user, I want to register an account with email verification so that I can securely access the system",
        acceptance_criteria=[
            "User can enter email, username, and password on registration form",
            "System sends verification email with unique token",
            "User can click verification link to activate account",
            "Account remains inactive until email is verified"
        ]
    )
    
    print("📝 Original Story:")
    print(f"   Title: {sample_story.heading}")
    print(f"   Description: {sample_story.description}")
    print("   Acceptance Criteria:")
    for i, criteria in enumerate(sample_story.acceptance_criteria, 1):
        print(f"      {i}. {criteria}")
    
    print("\n🔄 ADO Format (with HTML):")
    ado_format = sample_story.to_ado_format()
    print(f"   System.Title: {ado_format['System.Title']}")
    print(f"   System.Description: {ado_format['System.Description']}")
    
    print("\n📺 How it appears in Azure DevOps:")
    rendered = ado_format['System.Description'].replace('<br>', '\n').replace('<strong>', '**').replace('</strong>', '**')
    print(rendered)

def demonstrate_snapshot_tracking():
    """Demonstrate snapshot tracking for change detection"""
    print_header("Snapshot Tracking Demo")
    
    epic = create_sample_epic_content()
    
    # Create current snapshot
    current_snapshot = {
        "content_hash": hashlib.sha256((epic['title'] + epic['description']).encode()).hexdigest(),
        "last_modified": datetime.now().isoformat(),
        "title": epic['title'],
        "state": epic['state']
    }
    
    print("📸 Current EPIC Snapshot:")
    print(json.dumps(current_snapshot, indent=2))
    
    print("\n💾 This snapshot would be saved to track future changes")
    print("🔍 Next sync will compare against this snapshot to detect changes")
    
    return current_snapshot

def main():
    """Run the complete demo"""
    print("🚀 Enhanced ADO Story Extractor - EPIC Synchronization Demo")
    print("=" * 80)
    print("This demo showcases the new EPIC change detection and synchronization capabilities")
    
    # Demo 1: Change Detection
    epic, has_changes = demonstrate_change_detection()
    
    # Demo 2: Story Extraction
    if has_changes:
        extracted_stories = demonstrate_story_extraction()
    
    # Demo 3: ADO Formatting
    demonstrate_ado_format()
    
    # Demo 4: Synchronization Process
    sync_result = demonstrate_synchronization()
    
    # Demo 5: Final Results
    print_header("Synchronization Results")
    print(f"🎯 EPIC: {sync_result.epic_title}")
    print(f"✅ Sync Status: {'SUCCESS' if sync_result.sync_successful else 'FAILED'}")
    print(f"✨ Created Stories: {len(sync_result.created_stories)} (IDs: {sync_result.created_stories})")
    print(f"🔄 Updated Stories: {len(sync_result.updated_stories)} (IDs: {sync_result.updated_stories})")
    print(f"⏸️  Unchanged Stories: {len(sync_result.unchanged_stories)} (IDs: {sync_result.unchanged_stories})")
    
    total_changes = len(sync_result.created_stories) + len(sync_result.updated_stories)
    print(f"📊 Total Changes Made: {total_changes}")
    
    # Demo 6: Snapshot Tracking
    snapshot = demonstrate_snapshot_tracking()
    
    # Demo 7: CLI Usage Examples
    print_header("CLI Usage Examples")
    print("Here's how you would use the enhanced CLI:")
    print()
    print("# Synchronize an EPIC with change detection")
    print("python main_enhanced.py sync-epic 12345")
    print()
    print("# Synchronize with snapshot tracking")
    print("python main_enhanced.py sync-epic 12345 --snapshot snapshots/epic_12345.json")
    print()
    print("# Preview changes without applying them")
    print("python main_enhanced.py preview-epic 12345")
    print()
    print("# Process single requirement (original functionality)")
    print("python main_enhanced.py process 12345")
    
    print_header("Demo Complete! 🎉")
    print("Key Features Demonstrated:")
    print("✅ EPIC change detection using content hashing")
    print("✅ Automatic story extraction from updated EPICs")
    print("✅ Intelligent story matching and update detection")
    print("✅ HTML formatting for proper ADO display")
    print("✅ Snapshot tracking for change management")
    print("✅ Comprehensive synchronization reporting")

if __name__ == "__main__":
    main()
