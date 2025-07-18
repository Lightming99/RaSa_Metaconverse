# Chatbot implementation
import requests
import json
import logging
from config.config import Config
from src.utils import log_activity
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self):
        self.config = Config()
        self.rasa_url = Config.RASA_SERVER_URL
        self.groq_headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        self.start_rasa_server()
    
    def start_rasa_server(self):
        """Start Rasa server if not running"""
        try:
            # Check if Rasa server is running
            response = requests.get(f"{self.rasa_url}/status", timeout=5)
            if response.status_code == 200:
                logger.info("Rasa server is already running")
                return
        except requests.exceptions.RequestException:
            pass
        
        # Start Rasa server
        try:
            logger.info("Starting Rasa server...")
            subprocess.Popen([
                "rasa", "run", "--enable-api", "--cors", "*",
                "--port", "5005", "--model", f"{Config.RASA_PROJECT_PATH}/models"
            ], cwd=Config.RASA_PROJECT_PATH)
            
            # Wait for server to start
            import time
            time.sleep(10)
            
            log_activity("System", "Rasa server started")
            logger.info("Rasa server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Rasa server: {str(e)}")
            log_activity("Error", f"Failed to start Rasa server: {str(e)}")
    
    def get_response(self, user_message):
        """Get response from Rasa or Groq based on confidence"""
        try:
            # First, try Rasa
            rasa_response = self.query_rasa(user_message)
            
            if rasa_response and rasa_response.get("confidence", 0) >= Config.RASA_CONFIDENCE_THRESHOLD:
                return {
                    "response": rasa_response["response"],
                    "confidence": rasa_response["confidence"],
                    "model_source": "Rasa"
                }
            
            # If Rasa confidence is low, use Groq
            groq_response = self.query_groq(user_message)
            
            return {
                "response": groq_response,
                "confidence": 0.9,  # Groq responses are considered high confidence
                "model_source": "Groq"
            }
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            log_activity("Error", f"Error getting response: {str(e)}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "confidence": 0.0,
                "model_source": "Error"
            }
    
    def query_rasa(self, message):
        """Query Rasa server"""
        try:
            payload = {
                "sender": "user",
                "message": message
            }
            
            response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Get confidence from parse endpoint
                    parse_response = requests.post(
                        f"{self.rasa_url}/model/parse",
                        json={"text": message},
                        timeout=10
                    )
                    
                    confidence = 0.0
                    if parse_response.status_code == 200:
                        parse_data = parse_response.json()
                        confidence = parse_data.get("intent", {}).get("confidence", 0.0)
                    
                    return {
                        "response": data[0].get("text", "I don't understand."),
                        "confidence": confidence
                    }
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Rasa query failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Rasa query: {str(e)}")
            return None
    
    def query_groq(self, message):
        """Query Groq API"""
        try:
            # Create IT support context
            system_message = """You are an IT support specialist. Provide concise, accurate, and helpful responses to IT-related questions. 
            Keep responses short and focused on practical solutions. If the question is not IT-related, politely redirect to IT topics."""
            
            payload = {
                "model": Config.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{Config.GROQ_BASE_URL}/chat/completions",
                headers=self.groq_headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to the knowledge base. Please try again."
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq query failed: {str(e)}")
            return "I'm experiencing connectivity issues. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in Groq query: {str(e)}")
            return "I encountered an unexpected error. Please try again."
