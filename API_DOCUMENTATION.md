## Starting and Stopping the API Server

To interact with the API, you first need to start the server. The server can be easily started and stopped using the `monitor_daemon.py` script.

### Starting the Server
1. Open your terminal.
2. Navigate to the directory where the ADO Story Extractor is located.
3. Run the command to start the server:
   ```bash
   python monitor_daemon.py --mode api --host 0.0.0.0 --port 5001
   ```
   - This will start the server on all available network interfaces (`0.0.0.0`) at port `5001`.
   - Note: Use port 5001 instead of 5000 to avoid conflicts with macOS AirPlay Receiver.

### Stopping the Server
- To stop the server, you can simply terminate the process by pressing `Ctrl+C` in the terminal where it's running.

# API Documentation

The ADO Story Extractor provides a REST API for controlling and interacting with the EPIC change monitoring service. Below is a comprehensive description of the available endpoints and their usage.

---

### **GET /api/health**
**Description**: Performs a health check on the API service.

**Response**: 
- **200 OK**: Returns the health status with a timestamp and whether the monitor is running.

Example Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-07T15:36:25Z",
  "monitor_running": true
}
```

---

### **GET /api/status**
**Description**: Retrieves the current status of the EPIC monitoring service.

**Response**: 
- **200 OK**: Returns the monitoring status or indicates if the monitor is not initialized.

Example Response:
```json
{
  "is_running": true,
  "config": {
    "poll_interval_seconds": 300,
    "auto_sync": true,
    "story_extraction_type": "User Story",
    "test_case_extraction_type": "Issue"
  },
  "monitored_epics": {
    "123": {
      "last_check": "2025-08-07T15:30:00Z",
      "consecutive_errors": 0,
      "has_snapshot": true,
      "last_sync_result": {
        "timestamp": "2025-08-07T15:30:00Z",
        "success": true,
        "created_stories": ["456", "789"]
      }
    }
  }
}
```

---

### **POST /api/start**
**Description**: Starts the EPIC monitoring service.

**Response**:
- **200 OK**: Indicates that the monitor started successfully.
- **400 BAD REQUEST**: Monitor is already running.
- **500 INTERNAL SERVER ERROR**: An error occurred starting the monitor.

Example Response:
```json
{
  "success": true,
  "message": "Monitor started successfully"
}
```

---

### **POST /api/stop**
**Description**: Stops the EPIC monitoring service.

**Response**:
- **200 OK**: Monitor stopped successfully.
- **400 BAD REQUEST**: Monitor is not running.
- **500 INTERNAL SERVER ERROR**: An error occurred stopping the monitor.

Example Response:
```json
{
  "success": true,
  "message": "Monitor stopped successfully"
}
```

---

### **GET /api/epics**
**Description**: Lists all EPICs currently being monitored.

**Response**:
- **200 OK**: Returns a list of monitored EPICs with details.

Example Response:
```json
{
  "epics": ["123", "456", "789"],
  "details": {
    "123": {
      "last_check": "2025-08-07T15:30:00Z",
      "consecutive_errors": 0,
      "has_snapshot": true,
      "last_sync_result": {
        "success": true,
        "created_stories": 3
      }
    }
  }
}
```

---

### **POST /api/epics/{epic_id}**
**Description**: Adds an EPIC to the monitoring list.

**Parameters**:
- `epic_id` (path): The ID of the EPIC to add to monitoring.

**Response**:
- **200 OK**: EPIC added successfully.
- **400 BAD REQUEST**: Failed to add EPIC or EPIC ID is invalid.
- **500 INTERNAL SERVER ERROR**: An error occurred adding the EPIC.

Example Response:
```json
{
  "success": true,
  "message": "EPIC 123 added to monitoring"
}
```

---

### **DELETE /api/epics/{epic_id}**
**Description**: Removes an EPIC from the monitoring list.

**Parameters**:
- `epic_id` (path): The ID of the EPIC to remove from monitoring.

**Response**:
- **200 OK**: EPIC removed successfully.
- **404 NOT FOUND**: EPIC not found in monitoring list.
- **500 INTERNAL SERVER ERROR**: An error occurred removing the EPIC.

Example Response:
```json
{
  "success": true,
  "message": "EPIC 123 removed from monitoring"
}
```

---

### **GET /api/config**
**Description**: Retrieves the current monitoring configuration.

**Response**:
- **200 OK**: Returns the current configuration settings and available work item types.

Example Response:
```json
{
  "config": {
    "poll_interval_seconds": 300,
    "auto_sync": true,
    "auto_extract_new_epics": true,
    "story_extraction_type": "User Story",
    "test_case_extraction_type": "Issue",
    "skip_duplicate_check": false,
    "retry_attempts": 3,
    "retry_delay_seconds": 60,
    "log_level": "INFO"
  },
  "available_types": {
    "story_types": ["User Story", "Task"],
    "test_case_types": ["Issue", "Test Case"]
  }
}
```

---

### **POST /api/config**
**Description**: Updates the monitoring configuration.

**Request Body**:
```json
{
  "poll_interval_seconds": 300,
  "auto_sync": true,
  "auto_extract_new_epics": true,
  "story_extraction_type": "Task",
  "test_case_extraction_type": "Test Case",
  "skip_duplicate_check": false,
  "retry_attempts": 3,
  "retry_delay_seconds": 60,
  "log_level": "INFO"
}
```

**Response**:
- **200 OK**: Configuration updated successfully.
- **500 INTERNAL SERVER ERROR**: An error occurred updating the configuration.

Example Response:
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config": {
    "poll_interval_seconds": 300,
    "story_extraction_type": "Task",
    "test_case_extraction_type": "Test Case"
  }
}
```

---

### **POST /api/force-check**
**Description**: Forces an immediate check for changes across all monitored EPICs or a specific EPIC.

**Request Body** (Optional):
```json
{
  "epic_id": "123"
}
```

**Response**:
- **200 OK**: Force check completed successfully.
- **400 BAD REQUEST**: Monitor is not initialized.
- **500 INTERNAL SERVER ERROR**: An error occurred during the force check.

Example Response:
```json
{
  "success": true,
  "results": {
    "123": {
      "has_changes": true,
      "check_time": "2025-08-07T15:30:00Z",
      "sync_result": {
        "success": true,
        "created_stories": ["456", "789"],
        "updated_stories": [],
        "error_message": null
      }
    }
  }
}
```

---

### **GET /api/logs**
**Description**: Retrieves recent log entries from the monitoring service.

**Query Parameters**:
- `lines` (optional): Number of recent log lines to retrieve (default: 50).

**Response**:
- **200 OK**: Returns recent log entries.

Example Response:
```json
{
  "logs": [
    "2025-08-07 15:30:00 - INFO - Starting EPIC monitoring loop",
    "2025-08-07 15:30:05 - INFO - Checking EPIC 123 for changes",
    "2025-08-07 15:30:10 - INFO - No changes detected for EPIC 123"
  ],
  "total_lines": 150
}
```

---

### **POST /api/test-cases/extract**
**Description**: Extracts test cases for a specific user story using AI analysis.

**Request Body**:
```json
{
  "story_id": "456",
  "work_item_type": "Test Case"
}
```

**Response**:
- **200 OK**: Test cases extracted and uploaded successfully.
- **400 BAD REQUEST**: Missing or invalid story_id.
- **500 INTERNAL SERVER ERROR**: An error occurred during test case extraction.

Example Response:
```json
{
  "success": true,
  "message": "Test cases extracted for story 456",
  "result": {
    "story_id": "456",
    "story_title": "User Login Feature",
    "test_cases": [
      {
        "title": "Valid Login with Correct Credentials",
        "description": "Test successful login with valid email and password",
        "test_type": "positive",
        "priority": "High",
        "preconditions": ["User has valid account"],
        "test_steps": [
          "Navigate to login page",
          "Enter valid email",
          "Enter valid password",
          "Click login button"
        ],
        "expected_result": "User successfully logged in and redirected to dashboard"
      }
    ],
    "total_uploaded": 6,
    "total_errors": 0
  }
}
```

---

## Configuration Parameters

### Work Item Type Configuration
The API now supports configurable work item types for maximum flexibility:

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `story_extraction_type` | "User Story", "Task" | "User Story" | Work item type for extracted stories |
| `test_case_extraction_type` | "Issue", "Test Case" | "Issue" | Work item type for extracted test cases |

### Monitoring Configuration
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `poll_interval_seconds` | integer | 300 | How often to check for changes |
| `auto_sync` | boolean | true | Automatically sync when changes detected |
| `auto_extract_new_epics` | boolean | true | Automatically extract stories from new epics |
| `skip_duplicate_check` | boolean | false | Skip duplicate detection (may create duplicates) |
| `retry_attempts` | integer | 3 | Number of retry attempts on failure |
| `retry_delay_seconds` | integer | 60 | Delay between retry attempts |
| `log_level` | string | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Duplicate Prevention
The API includes intelligent duplicate prevention:
- **State Tracking**: Maintains `monitor_state.json` with processed epic information
- **Epic Validation**: Checks if epics already have stories before extraction
- **Smart Detection**: Uses multiple validation layers to prevent re-processing
- **Persistent State**: Survives service restarts and maintains processing history

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "timestamp": "2025-08-07T15:30:00Z"
}
```

Common HTTP status codes:
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error (system error)

## Rate Limiting & Performance

- **Azure DevOps**: Respects ADO API rate limits with built-in retry logic
- **OpenAI**: Implements exponential backoff for AI API calls
- **Concurrent Processing**: Configurable max concurrent operations
- **Efficient Polling**: Smart change detection minimizes unnecessary API calls
