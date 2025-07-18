#!/usr/bin/env python3
"""Test script to verify the application components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils import log_activity, initialize_data_files
from src.feedback_manager import FeedbackManager
from src.analytics import Analytics
from config.config import Config

def test_logging():
    print("Testing logging...")
    try:
        log_activity("Test", "Testing log functionality")
        print("✓ Logging works")
    except Exception as e:
        print(f"✗ Logging failed: {e}")

def test_feedback():
    print("Testing feedback...")
    try:
        fm = FeedbackManager()
        fm.process_feedback(
            response_id="test_1",
            user_query="test query",
            bot_response="test response",
            model_source="Test",
            feedback_type="positive"
        )
        print("✓ Feedback processing works")
    except Exception as e:
        print(f"✗ Feedback processing failed: {e}")

def test_analytics():
    print("Testing analytics...")
    try:
        analytics = Analytics()
        metrics = analytics.get_performance_metrics()
        print(f"✓ Analytics works: {metrics}")
    except Exception as e:
        print(f"✗ Analytics failed: {e}")

def test_chat_history():
    print("Testing chat history...")
    try:
        fm = FeedbackManager()
        fm.save_chat_history("test question", {
            "response": "test answer",
            "confidence": 0.95,
            "model_source": "Test"
        })
        print("✓ Chat history works")
    except Exception as e:
        print(f"✗ Chat history failed: {e}")

if __name__ == "__main__":
    print("=== Testing MetaConverse Components ===")
    initialize_data_files()
    test_logging()
    test_feedback()
    test_analytics()
    test_chat_history()
    print("=== Test Complete ===")
