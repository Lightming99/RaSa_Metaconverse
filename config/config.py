# Configuration settings
import os
from datetime import datetime

class Config:
    # API Configuration
    GROQ_API_KEY = "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"
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "llama-3.1-8b-instant"
    
    GEMINI_API_KEY = "AIzaSyBbIfLAWs5TuA0ID0l1KIeTXM9y2eQLzds"
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Rasa Configuration
    RASA_CONFIDENCE_THRESHOLD = 0.67
    RASA_PROJECT_PATH = "rasa_project"
    RASA_SERVER_URL = "http://localhost:5005"
    
    # File Paths
    DATA_DIR = "data"
    CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
    FEEDBACK_DATA_FILE = os.path.join(DATA_DIR, "feedback_data.json")
    LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
    
    # UI Configuration
    LOGO_PATH = "assets/logo.png"
    ADMIN_PASSWORD = "Anmol@123"
    
    # Training Configuration
    FEEDBACK_THRESHOLD = 10
    BATCH_SIZE = 5
    
    # Metrics
    SUPPORTED_METRICS = ["BLEU", "F1", "Precision", "Recall", "Accuracy"]
    
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
