#!/usr/bin/env python3
"""
Simple test script to debug the logs API issue
"""

import os
from datetime import datetime

def test_log_parsing():
    """Test the log parsing logic"""
    log_file_path = 'logs/epic_monitor.log'
    
    print(f"Testing log file: {log_file_path}")
    print(f"File exists: {os.path.exists(log_file_path)}")
    
    if not os.path.exists(log_file_path):
        print("Log file doesn't exist!")
        return
    
    try:
        # Read the log file
        print("Reading log file...")
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        print(f"Total lines: {len(lines)}")
        
        # Test with just the first 5 lines
        recent_lines = lines[-5:] if len(lines) > 5 else lines
        print(f"Processing {len(recent_lines)} lines...")
        
        logs = []
        for i, line in enumerate(recent_lines):
            line = line.strip()
            if line:
                print(f"Processing line {i+1}: {line[:100]}...")
                
                # Parse the log line format: timestamp - logger - level - message
                parts = line.split(' - ', 3)
                if len(parts) >= 4:
                    timestamp_str, logger_name, level, message = parts
                    print(f"  Parsed parts: timestamp='{timestamp_str}', logger='{logger_name}', level='{level}'")
                    
                    try:
                        # Try to parse the timestamp
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        print(f"  Timestamp parsed successfully: {timestamp}")
                        logs.append({
                            'timestamp': timestamp.isoformat(),
                            'level': level.lower(),
                            'logger': logger_name,
                            'message': message
                        })
                    except ValueError as e:
                        print(f"  Timestamp parsing failed: {e}")
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'level': 'info',
                            'logger': 'system',
                            'message': line
                        })
                else:
                    print(f"  Line doesn't match expected format (only {len(parts)} parts)")
                    logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'info',
                        'logger': 'system',
                        'message': line
                    })
        
        print(f"Successfully parsed {len(logs)} log entries")
        for i, log in enumerate(logs):
            print(f"  Log {i+1}: {log['timestamp']} - {log['level']} - {log['message'][:50]}...")
        
        return logs
        
    except Exception as e:
        print(f"Error reading logs: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_log_parsing()
