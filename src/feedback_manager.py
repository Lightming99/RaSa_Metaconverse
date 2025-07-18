import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config.config import Config
from src.utils import safe_load_json, safe_save_json, log_activity

class FeedbackManager:
    def __init__(self):
        self.feedback_file = Config.FEEDBACK_DATA_FILE
        self.chat_history_file = Config.CHAT_HISTORY_FILE
        
        # Ensure files exist and are valid
        self._initialize_feedback_files()
    
    def _initialize_feedback_files(self) -> None:
        """Initialize feedback files with proper structure"""
        try:
            # Initialize feedback data file
            feedback_data = safe_load_json(self.feedback_file, [])
            if not isinstance(feedback_data, list):
                safe_save_json(self.feedback_file, [])
            
            # Initialize chat history file
            chat_history = safe_load_json(self.chat_history_file, [])
            if not isinstance(chat_history, list):
                safe_save_json(self.chat_history_file, [])
            
            log_activity("FeedbackManager", "Feedback files initialized successfully")
            
        except Exception as e:
            log_activity("Error", f"Failed to initialize feedback files: {str(e)}")
    
    def process_feedback(self, message_index: int, user_query: str, bot_response: str, 
                        model_source: str, feedback_type: str, 
                        issue_description: Optional[str] = None, 
                        expected_answer: Optional[str] = None) -> bool:
        """Process and store feedback with enhanced error handling"""
        try:
            # Create feedback entry
            feedback_entry = {
                "id": str(uuid.uuid4()),
                "message_index": message_index,
                "user_query": user_query.strip() if user_query else "",
                "bot_response": bot_response.strip() if bot_response else "",
                "model_source": model_source,
                "feedback_type": feedback_type,
                "issue_description": issue_description.strip() if issue_description else "",
                "expected_answer": expected_answer.strip() if expected_answer else "",
                "timestamp": datetime.now().isoformat(),
                "processed": False,
                "retry_count": 0
            }
            
            # Load existing feedback
            feedback_data = safe_load_json(self.feedback_file, [])
            
            # Ensure it's a list
            if not isinstance(feedback_data, list):
                feedback_data = []
            
            # Add new feedback
            feedback_data.append(feedback_entry)
            
            # Save feedback
            success = safe_save_json(self.feedback_file, feedback_data)
            
            if success:
                log_activity("Feedback", f"Feedback stored: {feedback_type} for {model_source}")
                log_activity("Feedback", f"User query: {user_query[:100]}...")
                
                # Check if auto-training threshold is reached
                self._check_auto_training_threshold()
                
                return True
            else:
                log_activity("Error", "Failed to save feedback data")
                return False
            
        except Exception as e:
            log_activity("Error", f"Failed to process feedback: {str(e)}")
            return False
    
    def _check_auto_training_threshold(self) -> None:
        """Check if auto-training threshold is reached"""
        try:
            # Get unprocessed feedback count
            unprocessed_count = len(self.get_unprocessed_feedback())
            
            # Get threshold
            from src.training_manager import TrainingManager
            training_manager = TrainingManager()
            threshold = training_manager.load_feedback_threshold()
            
            if unprocessed_count >= threshold:
                log_activity("Training", f"Auto-training threshold reached: {unprocessed_count}/{threshold}")
                
                # Trigger training in a separate thread to avoid blocking UI
                import threading
                training_thread = threading.Thread(
                    target=self._trigger_auto_training,
                    args=(training_manager,)
                )
                training_thread.daemon = True
                training_thread.start()
                
        except Exception as e:
            log_activity("Error", f"Auto-training check failed: {str(e)}")
    
    def _trigger_auto_training(self, training_manager) -> None:
        """Trigger auto-training in background"""
        try:
            log_activity("Training", "Triggering automatic training")
            result = training_manager.process_reviews_manual()
            log_activity("Training", f"Auto-training result: {result}")
        except Exception as e:
            log_activity("Error", f"Auto-training failed: {str(e)}")
    
    def save_chat_history(self, user_query: str, response_data: Dict[str, Any]) -> None:
        """Save chat history with enhanced error handling"""
        try:
            # Create chat entry
            chat_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query.strip() if user_query else "",
                "bot_response": response_data.get("response", "").strip(),
                "confidence": response_data.get("confidence", 0.0),
                "model_source": response_data.get("model_source", "Unknown")
            }
            
            # Load existing chat history
            chat_history = safe_load_json(self.chat_history_file, [])
            
            # Ensure it's a list
            if not isinstance(chat_history, list):
                chat_history = []
            
            # Add new chat entry
            chat_history.append(chat_entry)
            
            # Keep only last 1000 entries to prevent file bloat
            if len(chat_history) > 1000:
                chat_history = chat_history[-1000:]
            
            # Save chat history
            success = safe_save_json(self.chat_history_file, chat_history)
            
            if success:
                log_activity("Chat", f"Chat saved: {user_query[:50]}... -> {response_data.get('model_source', 'Unknown')}")
            else:
                log_activity("Error", "Failed to save chat history")
            
        except Exception as e:
            log_activity("Error", f"Failed to save chat history: {str(e)}")
    
    def get_unprocessed_feedback(self) -> List[Dict[str, Any]]:
        """Get unprocessed feedback with error handling"""
        try:
            feedback_data = safe_load_json(self.feedback_file, [])
            
            if not isinstance(feedback_data, list):
                return []
            
            # Filter unprocessed feedback
            unprocessed = [
                feedback for feedback in feedback_data
                if not feedback.get("processed", False)
            ]
            
            return unprocessed
            
        except Exception as e:
            log_activity("Error", f"Failed to get unprocessed feedback: {str(e)}")
            return []
    
    def mark_feedback_processed(self, feedback_ids: List[str]) -> None:
        """Mark feedback as processed"""
        try:
            feedback_data = safe_load_json(self.feedback_file, [])
            
            if not isinstance(feedback_data, list):
                return
            
            # Mark specified feedback as processed
            updated_count = 0
            for feedback in feedback_data:
                if feedback.get("id") in feedback_ids:
                    feedback["processed"] = True
                    feedback["processed_timestamp"] = datetime.now().isoformat()
                    updated_count += 1
            
            # Save updated feedback
            if updated_count > 0:
                success = safe_save_json(self.feedback_file, feedback_data)
                if success:
                    log_activity("Feedback", f"Marked {updated_count} feedback entries as processed")
                else:
                    log_activity("Error", "Failed to save processed feedback updates")
            
        except Exception as e:
            log_activity("Error", f"Failed to mark feedback as processed: {str(e)}")
    
    def get_feedback_stats(self) -> Dict[str, int]:
        """Get feedback statistics"""
        try:
            feedback_data = safe_load_json(self.feedback_file, [])
            
            if not isinstance(feedback_data, list):
                return {"total": 0, "processed": 0, "unprocessed": 0, "positive": 0, "negative": 0}
            
            total = len(feedback_data)
            processed = sum(1 for f in feedback_data if f.get("processed", False))
            unprocessed = total - processed
            positive = sum(1 for f in feedback_data if f.get("feedback_type") == "positive")
            negative = sum(1 for f in feedback_data if f.get("feedback_type") == "negative")
            
            return {
                "total": total,
                "processed": processed,
                "unprocessed": unprocessed,
                "positive": positive,
                "negative": negative
            }
            
        except Exception as e:
            log_activity("Error", f"Failed to get feedback stats: {str(e)}")
            return {"total": 0, "processed": 0, "unprocessed": 0, "positive": 0, "negative": 0}
    
    def cleanup_old_feedback(self, days: int = 30) -> None:
        """Clean up old feedback entries"""
        try:
            feedback_data = safe_load_json(self.feedback_file, [])
            
            if not isinstance(feedback_data, list):
                return
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter out old feedback
            filtered_feedback = []
            removed_count = 0
            
            for feedback in feedback_data:
                try:
                    feedback_date = datetime.fromisoformat(feedback.get("timestamp", ""))
                    if feedback_date >= cutoff_date:
                        filtered_feedback.append(feedback)
                    else:
                        removed_count += 1
                except:
                    # Keep feedback with invalid timestamps
                    filtered_feedback.append(feedback)
            
            # Save cleaned feedback
            if removed_count > 0:
                success = safe_save_json(self.feedback_file, filtered_feedback)
                if success:
                    log_activity("Cleanup", f"Removed {removed_count} old feedback entries")
            
        except Exception as e:
            log_activity("Error", f"Failed to cleanup old feedback: {str(e)}")
