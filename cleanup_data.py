#!/usr/bin/env python3
"""
Data cleanup script to fix corrupted JSON files
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils import safe_load_json, safe_save_json, log_activity, cleanup_data_files
from config.config import Config

def main():
    """Clean up all data files"""
    print("🔧 Starting data cleanup...")
    
    # Initialize data files
    try:
        cleanup_data_files()
        print("✅ Data files cleaned up successfully")
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return
    
    # Verify all files
    files_to_check = [
        Config.LOGS_FILE,
        Config.CHAT_HISTORY_FILE,
        Config.FEEDBACK_DATA_FILE,
        os.path.join(Config.DATA_DIR, "processed_reviews.json"),
        os.path.join(Config.DATA_DIR, "rejected.json"),
        os.path.join(Config.DATA_DIR, "settings.json")
    ]
    
    print("\n📁 Checking file integrity:")
    for file_path in files_to_check:
        try:
            data = safe_load_json(file_path)
            print(f"✅ {file_path}: OK ({type(data).__name__} with {len(data) if isinstance(data, (list, dict)) else 'N/A'} items)")
        except Exception as e:
            print(f"❌ {file_path}: Error - {str(e)}")
    
    print("\n🎯 Cleanup completed!")

if __name__ == "__main__":
    main()
