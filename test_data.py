import json
import os
from config.config import Config

# Test the data files
def test_data_files():
    print("Testing data files...")
    
    # Test chat history
    if os.path.exists(Config.CHAT_HISTORY_FILE):
        with open(Config.CHAT_HISTORY_FILE, 'r') as f:
            chat_history = json.load(f)
        print(f"Chat history entries: {len(chat_history)}")
    else:
        print("Chat history file does not exist")
    
    # Test feedback data
    if os.path.exists(Config.FEEDBACK_DATA_FILE):
        with open(Config.FEEDBACK_DATA_FILE, 'r') as f:
            feedback_data = json.load(f)
        print(f"Feedback entries: {len(feedback_data)}")
    else:
        print("Feedback data file does not exist")
    
    # Test logs
    if os.path.exists(Config.LOGS_FILE):
        with open(Config.LOGS_FILE, 'r') as f:
            logs = json.load(f)
        print(f"Log entries: {len(logs)}")
    else:
        print("Logs file does not exist")

if __name__ == "__main__":
    test_data_files()
