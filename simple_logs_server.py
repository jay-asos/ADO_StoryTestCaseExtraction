#!/usr/bin/env python3
"""
Simple test server to verify logs API works
"""

from flask import Flask, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent log entries from the monitor log file"""
    try:
        log_file_path = 'logs/epic_monitor.log'
        
        # Check if log file exists
        if not os.path.exists(log_file_path):
            return jsonify({
                'success': True,
                'logs': [],
                'message': 'No log file found'
            })
        
        # Get the number of lines to return (default 100)
        limit = request.args.get('limit', 100, type=int)
        limit = min(max(limit, 10), 1000)  # Clamp between 10 and 1000
        
        # Read the log file efficiently
        logs = []
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Get the last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            # Parse log entries with better error handling
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Parse the log line format: timestamp - logger - level - message
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str, logger_name, level, message = parts
                        try:
                            # Try to parse the timestamp
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            logs.append({
                                'timestamp': timestamp.isoformat(),
                                'level': level.lower(),
                                'logger': logger_name,
                                'message': message
                            })
                        except ValueError:
                            # If timestamp parsing fails, just use the raw line
                            logs.append({
                                'timestamp': datetime.now().isoformat(),
                                'level': 'info',
                                'logger': 'system',
                                'message': line
                            })
                    else:
                        # If parsing fails, treat as a simple message
                        logs.append({
                            'timestamp': datetime.now().isoformat(),
                            'level': 'info',
                            'logger': 'system',
                            'message': line
                        })
        except IOError as io_error:
            print(f"IO Error reading log file: {str(io_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to read log file: {str(io_error)}',
                'logs': []
            }), 500
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total_entries': len(logs),
            'limit': limit
        })
        
    except Exception as e:
        print(f"Error reading logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to read logs: {str(e)}',
            'logs': []
        }), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting simple logs server on port 5002...")
    app.run(host='localhost', port=5002, debug=False)
