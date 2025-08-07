# ADO Story Extractor 🚀

## Overview

A **Python-based Azure DevOps (ADO) Story Extractor** that uses AI to automatically extract user stories from requirements/epics and manage them in Azure DevOps. The system provides intelligent monitoring, change detection, and synchronization capabilities with both CLI and API interfaces.

## 🎯 Key Features

- **🌐 Modern Web Dashboard**: Beautiful, responsive interface with dark theme support
- **🤖 AI-Powered Extraction**: Uses OpenAI GPT to analyze requirements and generate user stories
- **🔄 Change Detection**: Monitors epics using content hashing for automatic updates
- **⚡ Automatic Synchronization**: Creates, updates, and manages user stories in ADO
- **📸 Snapshot Tracking**: Maintains history for change detection and rollback
- **🛡️ Persistent State Management**: Tracks processed epics to prevent duplicate extractions
- **💾 Graceful Shutdown**: Saves snapshots before shutdown and resumes from last state
- **🧠 Smart Epic Processing**: Skips unchanged epics and prevents re-extraction of existing stories
- **🔌 REST API**: Provides API endpoints for integration with other systems
- **⌨️ Comprehensive CLI**: Multiple interfaces for different use cases
- **🔄 Background Monitoring**: Continuous epic monitoring with configurable polling
- **🚀 Production Ready**: Comprehensive logging, error handling, and retry mechanisms
- **🎨 Real-time UI**: Live updates, toast notifications, and intuitive controls
- **🔒 Safe Log Management**: UI-only log clearing that preserves files and snapshots
- **⚙️ Configurable Work Item Types**: Choose between User Story/Task for stories and Issue/Test Case for test cases
- **🔍 Test Case Extraction**: Built-in AI-powered test case generation from user stories
- **🚫 Duplicate Prevention**: Intelligent duplicate detection prevents story re-creation
- **🎛️ Dashboard Configuration**: Complete configuration management through the web interface

## 📁 Project Structure

```
ado-story-extractor/
├── src/                    # Core application logic
│   ├── agent.py           # Main orchestrator/coordinator
│   ├── ado_client.py      # Azure DevOps API client
│   ├── story_extractor.py # AI-powered story extraction
│   ├── test_case_extractor.py # AI-powered test case extraction
│   ├── models.py          # Data models (Pydantic)
│   ├── monitor.py         # Background monitoring service
│   └── monitor_api.py     # REST API for monitoring
├── templates/             # Web dashboard templates
│   └── dashboard.html     # Modern web interface with configuration UI
├── static/                # Static assets for web dashboard
│   └── styles.css         # Custom CSS styles
├── config/
│   └── settings.py        # Configuration management with work item types
├── tests/                 # Test suite
├── snapshots/             # Epic snapshots for change detection
├── logs/                  # Application logs
├── monitor_state.json     # Persistent state tracking for processed epics
├── monitor_config.json    # Monitor configuration settings
├── main.py               # Basic CLI interface
├── main_enhanced.py      # Enhanced CLI with epic sync
├── monitor_daemon.py     # Monitoring daemon runner
└── demo_epic_sync.py     # Demo/showcase script
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Azure DevOps** account with appropriate permissions
3. **OpenAI API** key for story extraction

### Setup

1. **Clone and Install Dependencies**:
   ```bash
   git clone <your-repo>
   cd ado-story-extractor
   pip install -r requirements.txt
   ```

   **Dependencies include:**
   - `flask` - Web framework for the dashboard
   - `azure-devops` - Azure DevOps integration
   - `openai` - AI-powered story extraction
   - `requests` - HTTP client for API calls
   - `pydantic` - Data validation and modeling
   - `pytest` - Testing framework

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   Required variables:
   ```env
   ADO_ORGANIZATION=your-organization
   ADO_PROJECT=your-project
   ADO_PAT=your-personal-access-token
   OPENAI_API_KEY=your-openai-api-key
   ```

3. **Validate Setup**:
   ```bash
   python main.py validate-config
   ```

### 🎯 Starting Points

#### **Option 1: Web Dashboard (Recommended for New Users)**
**Modern, user-friendly interface with no command-line required:**

```bash
# Start the web dashboard
python monitor_daemon.py --mode api --host 127.0.0.1 --port 5000

# Open your browser to: http://127.0.0.1:5000/
```

**Features available in the dashboard:**
- ✅ Start/stop monitoring with one click
- ✅ Add/remove epics visually
- ✅ Edit configuration through forms
- ✅ View real-time logs
- ✅ Dark/light theme toggle
- ✅ Responsive design for all devices

#### **Option 2: Demo Mode (Great for Understanding the System)**
**Best way to understand the system without real credentials:**

```bash
python demo_epic_sync.py
```

This showcases all features with mock data and explains the workflow.

#### **Option 3: Basic CLI Usage**
**Primary entry point for basic functionality:**

```bash
# Validate your configuration
python main.py validate-config

# Check available work item types in your project
python main.py check-types

# Process a single requirement/epic
python main.py process 123

# Preview stories without uploading to ADO
python main.py preview 123

# Process all requirements with filtering
python main.py process-all --state Active

# Get requirement summary
python main.py summary 123

# Show how stories will appear in ADO
python main.py show-format 123
```

#### **Option 3: Enhanced Epic Synchronization**
**For advanced epic synchronization with change detection:**

```bash
# Synchronize an epic with automatic change detection
python main_enhanced.py sync-epic 12345

# Synchronize with snapshot tracking for history
python main_enhanced.py sync-epic 12345 --snapshot snapshots/epic_12345.json

# Preview what changes would be made
python main_enhanced.py preview-epic 12345

# Process single requirement (original functionality)
python main_enhanced.py process 12345
```

#### **Option 4: Continuous Monitoring**
**For background monitoring and automatic synchronization:**

```bash
# Create default monitoring configuration
python monitor_daemon.py --create-config

# Edit monitor_config.json to add your epic IDs
# Then run in standalone mode
python monitor_daemon.py --mode standalone

# Or run with REST API for external integration
python monitor_daemon.py --mode api --host 0.0.0.0 --port 8080
```

## 📖 Usage Examples

### Basic Story Extraction
```bash
# Extract stories from a requirement and upload to ADO
python main.py process 456

# Just extract and preview (no upload)
python main.py preview 456
```

### Epic Synchronization with Change Detection
```bash
# Initial sync of an epic
python main_enhanced.py sync-epic 789

# Subsequent syncs will detect changes automatically
python main_enhanced.py sync-epic 789 --snapshot snapshots/epic_789.json
```

### Monitoring Setup
```bash
# Setup monitoring configuration
python monitor_daemon.py --create-config

# Edit monitor_config.json:
{
  "poll_interval_seconds": 300,
  "epic_ids": ["123", "456", "789"],
  "auto_sync": true,
  "log_level": "INFO"
}

# Start monitoring
python monitor_daemon.py --mode standalone
```

### API Integration
```bash
# Start API server
python monitor_daemon.py --mode api --port 5000

# API endpoints will be available at:
# http://localhost:5000/api/health
# http://localhost:5000/api/status
# http://localhost:5000/api/force-check
```

### Web Dashboard Integration
```bash
# Start API server with web dashboard
python monitor_daemon.py --mode api --port 5000

# Access the modern web dashboard at:
# http://localhost:5000/

# API endpoints available at:
# http://localhost:5000/api/health
# http://localhost:5000/api/status
# http://localhost:5000/api/force-check
```

## 🌐 Web Dashboard

### Modern Management Interface
The system now includes a **beautiful, modern web dashboard** built with Tailwind CSS and Alpine.js for comprehensive EPIC monitoring management.

#### 🎨 Dashboard Features
- **Monitor Control Panel**: Start/stop monitoring service with real-time status
- **Epic Management**: Add/remove epics from monitoring with live updates
- **Configuration Editor**: Edit monitor settings through an intuitive modal interface
- **Live Log Viewer**: Real-time log streaming with UI-only clearing (preserves files)
- **Dark Theme Support**: Toggle between light and dark modes with persistence
- **Toast Notifications**: User-friendly feedback for all actions
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Real-time Updates**: Auto-refreshing status and epic information

#### 📋 Dashboard Sections

1. **Monitor Status Panel**
   - Current monitoring state (Running/Stopped)
   - Start/stop buttons with loading states
   - Real-time status indicators

2. **Epic Management**
   - List all monitored epics with details
   - Add new epics with validation
   - Remove epics with confirmation
   - Epic status and last sync information

3. **Configuration Panel**
   - Edit poll intervals, retry settings
   - Toggle auto-sync and auto-extraction
   - Modify log levels and epic lists
   - Validation and error handling

4. **Log Viewer**
   - Real-time log streaming (last 50 lines)
   - Clear logs from display (preserves actual log files)
   - Formatted log display with timestamps
   - Auto-scroll to latest entries

5. **System Information**
   - Health status monitoring
   - Configuration summary
   - Performance metrics

#### 🔧 Dashboard Configuration
```json
{
  "poll_interval_seconds": 30,
  "max_concurrent_syncs": 3,
  "auto_sync": true,
  "auto_extract_new_epics": true,
  "log_level": "INFO",
  "epic_ids": ["123", "456"]
}
```

#### 🚀 Getting Started with Dashboard
1. **Start the API server**:
   ```bash
   python monitor_daemon.py --mode api --host 127.0.0.1 --port 5000
   ```

2. **Open your browser** to `http://127.0.0.1:5000/`

3. **Key Features Available**:
   - ✅ Start/stop monitor with one click
   - ✅ Add/remove epics dynamically
   - ✅ Edit configuration without restarting
   - ✅ View real-time logs
   - ✅ Toggle dark/light theme
   - ✅ Clear log display (keeps files intact)

#### 🎯 Dashboard Benefits
- **User-Friendly**: No command-line knowledge required
- **Real-time**: Live updates and instant feedback
- **Professional**: Modern, clean interface design
- **Responsive**: Works on all screen sizes
- **Safe**: UI-only log clearing preserves snapshots
- **Persistent**: Settings and preferences saved locally

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ADO_ORGANIZATION` | Azure DevOps organization name | Yes |
| `ADO_PROJECT` | Project name in ADO | Yes |
| `ADO_PAT` | Personal Access Token with work item permissions | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT access | Yes |
| `ADO_REQUIREMENT_TYPE` | Work item type for requirements (default: "Epic") | No |
| `ADO_USER_STORY_TYPE` | Work item type for user stories (default: "User Story") | No |
| `OPENAI_MAX_RETRIES` | Max retry attempts for OpenAI API (default: 3) | No |
| `OPENAI_RETRY_DELAY` | Delay between retries in seconds (default: 5) | No |
| `ADO_STORY_EXTRACTION_TYPE` | Work item type for story extraction (User Story/Task) | No |
| `ADO_TEST_CASE_EXTRACTION_TYPE` | Work item type for test case extraction (Issue/Test Case) | No |

### Monitor Configuration (`monitor_config.json`)

```json
{
  "poll_interval_seconds": 300,
  "max_concurrent_syncs": 3,
  "snapshot_directory": "snapshots",
  "log_level": "INFO",
  "epic_ids": ["123", "456"],
  "auto_sync": true,
  "auto_extract_new_epics": true,
  "notification_webhook": null,
  "retry_attempts": 3,
  "retry_delay_seconds": 60
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_story_extractor.py
```

## 📊 How It Works

### Story Extraction Process
1. **Fetch Requirement**: Retrieves epic/requirement from Azure DevOps
2. **AI Analysis**: Uses OpenAI GPT to analyze content and extract user stories
3. **Story Generation**: Creates structured user stories with acceptance criteria
4. **ADO Integration**: Uploads stories as work items linked to parent requirement
5. **Relationship Management**: Maintains parent-child relationships in ADO

### Change Detection & Monitoring
1. **Content Hashing**: Generates SHA256 hash of epic title + description
2. **Snapshot Comparison**: Compares current hash with stored snapshot
3. **Change Triggering**: Automatic re-extraction when changes detected
4. **Smart Synchronization**: Updates existing stories or creates new ones
5. **Continuous Monitoring**: Background service polls for changes
6. **Graceful Shutdown**: Saves all snapshots before stopping
7. **Persistent State**: Tracks processed epics to prevent duplicate extractions
8. **Resume Capability**: Continues monitoring from last known state after restart

### Story Synchronization Logic
- **New Stories**: Creates fresh work items in ADO
- **Similar Stories**: Uses fuzzy matching to identify existing stories
- **Updates**: Modifies existing stories when content changes significantly
- **Preservation**: Leaves unchanged stories untouched

## 🛠️ Troubleshooting

### Common Issues

1. **Configuration Errors**:
   ```bash
   python main.py validate-config
   ```

2. **ADO Connection Issues**:
   ```bash
   python main.py check-types
   ```

3. **Work Item Type Mismatches**:
   - Check available types with `check-types` command
   - Update `ADO_REQUIREMENT_TYPE` and `ADO_USER_STORY_TYPE` in `.env`

4. **OpenAI API Issues**:
   - Verify API key is valid
   - Check rate limits and quotas
   - Review logs for specific error messages

### Logs
- Application logs: `logs/epic_monitor.log`
- Console output with debug information
- Structured logging with timestamps and levels

## 🔒 Data Safety Features

### UI-Only Log Clearing
The dashboard includes a **safe log clearing feature** that preserves important data:

- **Display Clearing**: Clears logs from the web interface only
- **File Preservation**: Actual log files remain untouched
- **Snapshot Protection**: All epic snapshots and history are preserved
- **User Confirmation**: Clear confirmation dialog explains the behavior
- **Status Messages**: Success notifications confirm files are safe

```javascript
// Dashboard implementation ensures data safety
clearLogs() {
    // Only clears UI display: this.logs = []
    // Never deletes: logs/epic_monitor.log
    // Never deletes: snapshots/*.json
}
```

### Duplicate Prevention System
Advanced state management prevents duplicate story extraction:

- **State Tracking**: `monitor_state.json` tracks processed epics
- **Epic Flags**: Each epic has a `stories_extracted` boolean flag
- **Persistent Storage**: State survives service restarts
- **Smart Checks**: Multiple validation layers prevent re-processing
- **Logging**: Clear audit trail of what was processed when

## Daemon Enhancement: Smart State Management and Snapshot Handling

The Enhanced ADO Story Extractor daemon now includes sophisticated state management that prevents duplicate story extractions and ensures reliable operation across restarts.

### 🆕 **LATEST**: Persistent State Management
- **Snapshot on Shutdown**: Automatically saves all epic snapshots before stopping
- **State Persistence**: Tracks which epics have been processed to prevent re-extraction
- **Resume from Last State**: Continues monitoring exactly where it left off after restart
- **Skip Unchanged Epics**: Only processes epics that have actual content changes
- **Duplicate Prevention**: Never re-extracts stories for epics that already have them

### 🔥 **ENHANCED**: Auto-Extract Stories from New Epics

## Features

### 🔥 **NEW**: Auto-Extract Stories from New Epics
- **Automatic Discovery**: Daemon continuously scans Azure DevOps for new epics
- **Immediate Processing**: When a new epic is detected, stories are automatically extracted using AI
- **Configurable**: Can be enabled/disabled via the `auto_extract_new_epics` configuration option
- **Smart Integration**: Works alongside existing change detection for modified epics

### 🔄 **EXISTING**: Change Detection and Sync
- **Content Monitoring**: Tracks changes in epic title and description using SHA256 hashing
- **Automatic Re-sync**: Re-extracts and updates stories when epic content changes
- **Snapshot Management**: Maintains historical snapshots for change comparison

## Configuration

### New Configuration Option

Add the following to your `monitor_config.json`:

```json
{
  "poll_interval_seconds": 30,
  "auto_sync": true,
  "auto_extract_new_epics": true,
  "epic_ids": ["1"],
  ...
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_extract_new_epics` | boolean | `true` | Enable/disable automatic story extraction for new epics |
| `auto_sync` | boolean | `true` | Enable/disable automatic sync for changed epics |
| `poll_interval_seconds` | integer | `300` | How often to check for new epics and changes |

## How It Works

### 1. Epic Detection Process
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Scan Azure DevOps│ -[200d>[200d│ Compare with    │ -[200d>[200d│ Identify New    │
│ for All Epics   │    │ Monitored List  │    │ Epics           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. New Epic Processing
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Add Epic to     │ -[200d>[200d│ Extract Stories │ -[200d>[200d│ Create Stories  │
│ Monitoring      │    │ using AI        │    │ in Azure DevOps │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Ongoing Monitoring
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Monitor for     │ -[200d>[200d│ Detect Changes  │ -[200d>[200d│ Re-sync Stories │
│ Content Changes │    │ via Hashing     │    │ if Changed      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4. Test Case Generation Process
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ User Story      │ -[200d>[200d│ AI Analysis     │ -[200d>[200d│ Generate Test   │
│ Created         │    │ & Test Planning │    │ Cases           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ↓                       ↓                       ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Upload to ADO   │ ←--│ Categorize by   │ ←--│ Include:        │
│ as Child Items  │    │ Type & Priority │    │ • Positive Tests│
└─────────────────┘    └─────────────────┘    │ • Negative Tests│
                                              │ • Edge Cases    │
                                              └─────────────────┘
```

### 🧪 Test Case Extraction Workflow

#### Automatic Integration
- **Seamless Workflow**: Test cases are automatically generated after each user story creation
- **Smart Analysis**: AI analyzes user story content, description, and acceptance criteria
- **Comprehensive Coverage**: Generates positive, negative, and edge test scenarios

#### Test Case Types
- **Positive Tests**: Happy path scenarios with valid inputs and expected user behavior
- **Negative Tests**: Error conditions, invalid inputs, and unauthorized access scenarios  
- **Edge Cases**: Boundary values, extreme conditions, and limit testing scenarios

#### Generated Information
Each test case includes:
- **Title**: Clear, descriptive test case name
- **Description**: What the test case validates
- **Type**: positive, negative, or edge
- **Priority**: High, Medium, or Low
- **Preconditions**: Prerequisites for test execution
- **Test Steps**: Detailed step-by-step instructions
- **Expected Results**: Clear description of expected outcomes

#### ADO Integration
- Test cases are created as "Test Case" work items in Azure DevOps
- Automatically linked as child items to their parent user stories
- Properly formatted with HTML for rich text display in ADO
- Include all test metadata and categorization

## Benefits

### For Development Teams
- **Zero Manual Intervention**: New epics are automatically processed
- **Consistent Story Quality**: AI-powered extraction ensures consistent user story format
- **Real-time Updates**: Stories are available immediately after epic creation
- **Change Tracking**: Modifications to epics trigger automatic story updates

### For Project Managers
- **Complete Coverage**: No epics are missed or forgotten
- **Audit Trail**: Full history of when stories were created/updated
- **Flexible Control**: Can disable auto-extraction if manual review is preferred
- **Status Visibility**: Clear logging shows what was processed and when

## Migration Guide

### Existing Users
1. Update your `monitor_config.json` to include `"auto_extract_new_epics": true`
2. Restart the daemon - no other changes required
3. New epics will be automatically processed on the next polling cycle

### New Users
1. Follow the standard setup process in the main README
2. The enhanced functionality is enabled by default
3. Start the daemon with `python3 monitor_daemon.py --mode standalone`

## Technical Details

### Epic Detection Algorithm
- Fetches all epics from Azure DevOps using work item type filtering
- Compares against currently monitored epic set
- Identifies new epics using set difference operation
- Processes new epics immediately upon detection

### Story Extraction Process
- Uses OpenAI GPT to analyze epic content
- Generates structured user stories with acceptance criteria
- Creates work items in Azure DevOps with proper parent-child relationships
- Maintains snapshots for future change detection

### Error Handling
- Retry logic for failed API calls (configurable attempts and delays)
- Graceful handling of epic access issues
- Automatic removal of epics that become inaccessible
- Comprehensive logging for troubleshooting

## Performance Considerations

- **Polling Frequency**: Default 30-second intervals balance responsiveness with API usage
- **Concurrent Processing**: Configurable max concurrent syncs (default: 3)
- **API Rate Limits**: Built-in retry logic respects Azure DevOps and OpenAI limits
- **Memory Usage**: Efficient snapshot storage and cleanup

## Troubleshooting

### Common Issues

1. **Stories not being extracted for new epics**
   - Check `auto_extract_new_epics` is set to `true`
   - Verify Azure DevOps and OpenAI credentials
   - Review logs for specific error messages

2. **Duplicate processing**
   - Daemon prevents duplicate processing through state tracking
   - Snapshots ensure epics are only processed when actually new

3. **Performance issues**
   - Adjust `poll_interval_seconds` to reduce API calls
   - Decrease `max_concurrent_syncs` if hitting rate limits

### Log Analysis
```bash
# Monitor daemon activity
tail -f logs/epic_monitor.log

# Check for specific epic processing
grep "Epic 42" logs/epic_monitor.log
```

## Future Enhancements

- Webhook support for real-time epic notifications
- Custom story templates per epic type
- Integration with project management tools
- Advanced story prioritization based on epic metadata

## 🤝 Contributing

Feel free to explore the code and adapt it to your needs! The project is well-structured with:
- Comprehensive test coverage
- Clean separation of concerns
- Extensive documentation
- Production-ready error handling

---

**Ready to get started? Run the demo first:** `python demo_epic_sync.py` 🎉

## 🔌 REST API Endpoints

### Test Case Management

#### Extract Test Cases
```http
POST /api/stories/{story_id}/test-cases
```

Extracts comprehensive test cases for a specific user story without uploading to ADO.

**Response Example:**
```json
{
  "success": true,
  "story_id": "12345",
  "story_title": "User Login Feature",
  "test_cases": [
    {
      "title": "Valid Login with Email and Password",
      "description": "Test successful login with valid credentials",
      "test_type": "positive",
      "preconditions": ["User has valid account", "System is online"],
      "test_steps": [
        "Navigate to login page",
        "Enter valid email address",
        "Enter valid password",
        "Click login button"
      ],
      "expected_result": "User is successfully logged in and redirected to dashboard",
      "priority": "High"
    },
    {
      "title": "Login with Invalid Credentials",
      "description": "Test system behavior with incorrect login information",
      "test_type": "negative",
      "preconditions": ["System is online"],
      "test_steps": [
        "Navigate to login page",
        "Enter invalid email address",
        "Enter incorrect password",
        "Click login button"
      ],
      "expected_result": "Error message displayed: 'Invalid credentials'",
      "priority": "High"
    }
  ],
  "total_test_cases": 6
}
```

#### Extract and Upload Test Cases
```http
POST /api/stories/{story_id}/test-cases/upload
```

Extracts test cases and uploads them directly to Azure DevOps as child work items.

**Response Example:**
```json
{
  "success": true,
  "story_id": "12345",
  "story_title": "User Login Feature", 
  "uploaded_test_cases": [
    {
      "id": 67890,
      "title": "Valid Login with Email and Password",
      "type": "positive"
    }
  ],
  "errors": [],
  "total_uploaded": 6,
  "total_errors": 0
}
```

### Monitor Control
- `GET /api/status` - Get monitoring service status
- `POST /api/start` - Start monitoring service
- `POST /api/stop` - Stop monitoring service
- `POST /api/check` - Force check for changes

### Epic Management
- `GET /api/epics` - List monitored epics
- `POST /api/epics/{epic_id}` - Add epic to monitoring
- `DELETE /api/epics/{epic_id}` - Remove epic from monitoring

### Configuration & Logs
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration
- `GET /api/logs?lines=50` - Get recent log entries
- `DELETE /api/logs/clear` - Clear logs from UI display

