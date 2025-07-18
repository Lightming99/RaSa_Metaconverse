#!/usr/bin/env python3
"""Test logging functionality"""

import json
import os
from config.config import Config
from src.utils import log_activity

def test_logging():
    print("Testing logging functionality...")
    
    # Check logs file before logging
    if os.path.exists(Config.LOGS_FILE):
        with open(Config.LOGS_FILE, 'r') as f:
            logs_before = json.load(f)
        print(f"Logs before: {type(logs_before)} - {logs_before}")
    
    # Test logging
    try:
        log_activity("Test", "This is a test log entry")
        print("✓ Log activity called successfully")
    except Exception as e:
        print(f"✗ Log activity failed: {str(e)}")
        return
    
    # Check logs file after logging
    if os.path.exists(Config.LOGS_FILE):
        with open(Config.LOGS_FILE, 'r') as f:
            logs_after = json.load(f)
        print(f"Logs after: {type(logs_after)} - {logs_after}")
    
    print("✓ Logging test completed")

if __name__ == "__main__":
    test_logging()
