# Enhanced EPIC Monitor Features

This document describes the enhanced features added to the EPIC monitoring system to improve change detection, prevent duplicates, and provide better control over story extraction.

## 🆕 New Features

### 1. Content Hash-Based Change Detection

The monitor now uses MD5 hashing to efficiently detect changes in EPIC content.

**Benefits:**
- More precise change detection
- Reduced false positives
- Better performance for large EPICs

**Configuration:**
```json
{
  "enable_content_hash_comparison": true
}
```

**Usage:**
```python
# Calculate hash for an EPIC snapshot
hash_value = monitor._calculate_content_hash(epic_snapshot)

# Automatic hash comparison in change detection
has_changes = monitor._check_for_epic_changes(epic_id)
```

### 2. Extraction Cooldown Period

Prevents re-extraction of stories within a configurable time period.

**Benefits:**
- Reduces unnecessary API calls
- Prevents duplicate story creation
- Configurable per deployment

**Configuration:**
```json
{
  "extraction_cooldown_hours": 12
}
```

**Usage:**
```python
# Check if EPIC is in cooldown period
can_extract = monitor._check_cooldown_period(epic_id, hours=12)

# Cooldown is automatically checked in story extraction logic
```

### 3. Reset Processed State

Allows resetting an EPIC's processed state to enable re-extraction when needed.

**Benefits:**
- Manual override for re-extraction
- Useful for testing and troubleshooting
- Maintains data integrity

**Usage:**
```python
# Reset processed state for an EPIC
success = monitor.reset_epic_processed_state(epic_id)

# The EPIC can now have stories extracted again
```

### 4. Enhanced Monitoring Statistics

Provides detailed statistics about monitoring performance and status.

**Available Statistics:**
- Total EPICs monitored
- EPICs with stories extracted
- EPICs with errors
- EPICs with snapshots
- Total extracted stories
- Successful/failed syncs

**Usage:**
```python
# Get detailed statistics
stats = monitor.get_monitoring_statistics()

# Access specific metrics
total_epics = stats['total_epics_monitored']
success_rate = stats['successful_syncs'] / (stats['successful_syncs'] + stats['failed_syncs'])
```

### 5. Enhanced Status Reporting

The status endpoint now includes comprehensive monitoring information.

**New Status Fields:**
- `statistics`: Detailed monitoring metrics
- `stories_extracted`: Per-EPIC story extraction status
- `extracted_stories_count`: Number of stories per EPIC

**Usage:**
```python
# Get enhanced status
status = monitor.get_status()

# Access statistics
stats = status['statistics']
epic_info = status['monitored_epics']['123']
```

## 🔧 Configuration Options

### New Configuration Parameters

```json
{
  "extraction_cooldown_hours": 12,
  "enable_content_hash_comparison": true
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extraction_cooldown_hours` | int | 24 | Hours to wait before re-extraction (0 to disable) |
| `enable_content_hash_comparison` | bool | true | Use hash-based change detection |

### Complete Configuration Example

```json
{
  "poll_interval_seconds": 180,
  "max_concurrent_syncs": 5,
  "auto_sync": true,
  "auto_extract_new_epics": true,
  "skip_duplicate_check": false,
  "extraction_cooldown_hours": 12,
  "enable_content_hash_comparison": true,
  "retry_attempts": 3,
  "retry_delay_seconds": 60
}
```

## 🚀 Usage Examples

### Basic Setup with Enhanced Features

```python
from src.monitor import MonitorConfig, EpicChangeMonitor

# Create configuration with enhanced features
config = MonitorConfig(
    poll_interval_seconds=180,
    extraction_cooldown_hours=12,
    enable_content_hash_comparison=True,
    skip_duplicate_check=False
)

# Initialize monitor
monitor = EpicChangeMonitor(config)
```

### Managing EPIC Processing State

```python
# Check if EPIC has been processed
epic_id = "123"
is_processed = epic_id in monitor.processed_epics

# Reset EPIC for re-extraction
if is_processed:
    monitor.reset_epic_processed_state(epic_id)
    print(f"Reset EPIC {epic_id} for re-extraction")
```

### Monitoring Performance

```python
# Get comprehensive statistics
stats = monitor.get_monitoring_statistics()

print(f"Monitoring {stats['total_epics_monitored']} EPICs")
print(f"Stories extracted for {stats['epics_with_stories_extracted']} EPICs")
print(f"Success rate: {stats['successful_syncs']}/{stats['successful_syncs'] + stats['failed_syncs']}")
```

### Change Detection with Hashing

```python
# The monitor automatically uses hash-based comparison
# when enable_content_hash_comparison is True

# Manual hash calculation for custom logic
epic_snapshot = monitor.agent.get_epic_snapshot(epic_id)
hash_value = monitor._calculate_content_hash(epic_snapshot)
print(f"EPIC content hash: {hash_value}")
```

## 🛡️ Duplicate Prevention Mechanisms

The enhanced monitor includes multiple layers of duplicate prevention:

### 1. Processed State Tracking
- Maintains a persistent set of processed EPICs
- Stored in `monitor_state.json`
- Survives service restarts

### 2. Cooldown Period
- Configurable time-based restriction
- Prevents rapid re-extraction
- Bypassed only by manual reset

### 3. Existing Story Detection
- Checks Azure DevOps for existing stories
- Automatically marks EPICs as processed if stories exist
- Prevents duplicate creation

### 4. Content Hash Comparison
- Efficient change detection
- Reduces unnecessary processing
- Improves performance

## 🧪 Testing

Run the test suite to verify enhanced features:

```bash
python3 test_enhanced_monitor_features.py
```

Run the demonstration script:

```bash
python3 demo_enhanced_monitor.py
```

## 📊 Monitoring Dashboard Integration

The enhanced statistics are automatically available through the monitoring API:

```python
# Get status with enhanced information
GET /api/status

# Response includes:
{
  "statistics": {
    "total_epics_monitored": 15,
    "epics_with_stories_extracted": 12,
    "successful_syncs": 45,
    "failed_syncs": 2
  },
  "monitored_epics": {
    "123": {
      "stories_extracted": true,
      "extracted_stories_count": 5,
      "has_snapshot": true
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues

1. **EPIC stuck in processed state**
   - Use `reset_epic_processed_state(epic_id)` to reset
   - Check cooldown period configuration

2. **No changes detected despite EPIC updates**
   - Verify `enable_content_hash_comparison` setting
   - Check if changes are in tracked fields (title, description, state, priority)

3. **Stories extracted multiple times**
   - Ensure `skip_duplicate_check` is `false`
   - Verify processed state persistence

### Debug Commands

```python
# Check EPIC processing state
epic_id = "123"
print(f"Processed: {epic_id in monitor.processed_epics}")
print(f"Cooldown active: {not monitor._check_cooldown_period(epic_id)}")

# Get detailed status
status = monitor.get_status()
epic_status = status['monitored_epics'].get(epic_id, {})
print(f"Epic status: {epic_status}")
```

## 📝 Migration Notes

### From Previous Version

1. **Configuration**: Add new parameters to your config file
2. **State Files**: Existing state files are automatically migrated
3. **API**: All existing API endpoints remain compatible

### Backward Compatibility

All existing functionality remains unchanged. New features are opt-in through configuration.

---

## 📚 API Reference

### New Methods

- `reset_epic_processed_state(epic_id: str) -> bool`
- `get_monitoring_statistics() -> Dict`
- `_calculate_content_hash(snapshot: Dict) -> str`
- `_check_cooldown_period(epic_id: str, hours: int) -> bool`

### Enhanced Methods

- `get_status()`: Now includes statistics and enhanced EPIC information
- `_check_for_epic_changes()`: Uses content hashing for better performance
- `_should_extract_stories()`: Includes cooldown period checks
