import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import shutil
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_load_json(file_path: str, default: Any = None) -> Any:
    """Safely load JSON with corruption recovery"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.info(f"File {file_path} does not exist, creating with default value")
            safe_save_json(file_path, default if default is not None else [])
            return default if default is not None else []
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            logger.info(f"File {file_path} is empty, initializing with default value")
            safe_save_json(file_path, default if default is not None else [])
            return default if default is not None else []
        
        # Try to load the JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Handle empty content
            if not content:
                logger.info(f"File {file_path} has empty content, initializing with default")
                safe_save_json(file_path, default if default is not None else [])
                return default if default is not None else []
            
            # Try to parse JSON
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError as e:
                logger.error(f"JSON corruption in {file_path}: {str(e)}")
                
                # Try to fix common JSON issues
                fixed_data = _attempt_json_repair(content, file_path)
                if fixed_data is not None:
                    logger.info(f"Successfully repaired JSON in {file_path}")
                    # Save the repaired data
                    safe_save_json(file_path, fixed_data)
                    return fixed_data
                else:
                    # Create backup and reinitialize
                    _backup_corrupted_file(file_path)
                    safe_save_json(file_path, default if default is not None else [])
                    return default if default is not None else []
    
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        # Ensure we return a valid default
        try:
            safe_save_json(file_path, default if default is not None else [])
        except:
            pass
        return default if default is not None else []

def safe_save_json(file_path: str, data: Any) -> bool:
    """Safely save JSON with atomic writes"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create temporary file for atomic write
        temp_fd, temp_path = tempfile.mkstemp(
            dir=os.path.dirname(file_path),
            prefix=os.path.basename(file_path) + '_',
            suffix='.tmp'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic move
            if os.name == 'nt':  # Windows
                if os.path.exists(file_path):
                    os.remove(file_path)
            shutil.move(temp_path, file_path)
            
            logger.debug(f"Successfully saved {file_path}")
            return True
            
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e
            
    except Exception as e:
        logger.error(f"Error saving {file_path}: {str(e)}")
        return False

def _attempt_json_repair(content: str, file_path: str) -> Optional[Any]:
    """Attempt to repair corrupted JSON"""
    try:
        # Remove null bytes
        content = content.replace('\x00', '')
        
        # Try to find valid JSON by removing trailing garbage
        for i in range(len(content) - 1, -1, -1):
            try:
                test_content = content[:i+1]
                if test_content.strip().endswith((']', '}', '"', 'true', 'false', 'null')) or test_content.strip().isdigit():
                    data = json.loads(test_content)
                    logger.info(f"Repaired JSON by truncating at position {i}")
                    return data
            except json.JSONDecodeError:
                continue
        
        # Try to extract valid JSON objects from the content
        if '[' in content and ']' in content:
            start = content.find('[')
            end = content.rfind(']') + 1
            try:
                data = json.loads(content[start:end])
                logger.info("Repaired JSON by extracting array")
                return data
            except json.JSONDecodeError:
                pass
        
        if '{' in content and '}' in content:
            start = content.find('{')
            end = content.rfind('}') + 1
            try:
                data = json.loads(content[start:end])
                logger.info("Repaired JSON by extracting object")
                return data
            except json.JSONDecodeError:
                pass
        
        return None
        
    except Exception as e:
        logger.error(f"JSON repair failed: {str(e)}")
        return None

def _backup_corrupted_file(file_path: str) -> None:
    """Backup corrupted file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.corrupted_{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up corrupted file to {backup_path}")
    except Exception as e:
        logger.error(f"Failed to backup corrupted file: {str(e)}")

def log_activity(activity_type: str, message: str) -> None:
    """Enhanced logging with corruption protection"""
    try:
        from config.config import Config
        
        # Create log entry
        log_entry = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "message": message
        }
        
        # Load existing logs with corruption handling
        logs = safe_load_json(Config.LOGS_FILE, [])
        
        # Ensure logs is a list
        if not isinstance(logs, list):
            logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 1000 logs to prevent file bloat
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Save logs
        success = safe_save_json(Config.LOGS_FILE, logs)
        
        if success:
            logger.info(f"[{activity_type}] {message}")
        else:
            logger.error(f"Failed to save log: [{activity_type}] {message}")
            
    except Exception as e:
        logger.error(f"Logging failed: {str(e)} - Original message: [{activity_type}] {message}")

def initialize_data_files() -> None:
    """Initialize all data files with proper structure"""
    try:
        from config.config import Config
        
        # Define required files and their default structures
        required_files = {
            Config.LOGS_FILE: [],
            Config.CHAT_HISTORY_FILE: [],
            Config.FEEDBACK_DATA_FILE: [],
            os.path.join(Config.DATA_DIR, "processed_reviews.json"): [],
            os.path.join(Config.DATA_DIR, "rejected.json"): [],
            os.path.join(Config.DATA_DIR, "settings.json"): {"feedback_threshold": 5}
        }
        
        # Ensure data directory exists
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # Initialize each file
        for file_path, default_structure in required_files.items():
            try:
                # Use safe_load_json which will create/repair the file if needed
                data = safe_load_json(file_path, default_structure)
                
                # Validate structure and fix if needed
                if file_path.endswith('settings.json'):
                    if not isinstance(data, dict):
                        safe_save_json(file_path, default_structure)
                else:
                    if not isinstance(data, list):
                        safe_save_json(file_path, default_structure)
                
                logger.info(f"Initialized {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {file_path}: {str(e)}")
                # Force create with default structure
                safe_save_json(file_path, default_structure)
        
        log_activity("System", "Data files initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize data files: {str(e)}")

def cleanup_data_files() -> None:
    """Clean up and repair all data files"""
    try:
        from config.config import Config
        
        files_to_clean = [
            Config.LOGS_FILE,
            Config.CHAT_HISTORY_FILE,
            Config.FEEDBACK_DATA_FILE,
            os.path.join(Config.DATA_DIR, "processed_reviews.json"),
            os.path.join(Config.DATA_DIR, "rejected.json"),
            os.path.join(Config.DATA_DIR, "settings.json")
        ]
        
        for file_path in files_to_clean:
            if os.path.exists(file_path):
                try:
                    # Try to load and resave to clean up format
                    data = safe_load_json(file_path, [])
                    safe_save_json(file_path, data)
                    logger.info(f"Cleaned up {file_path}")
                except Exception as e:
                    logger.error(f"Failed to clean up {file_path}: {str(e)}")
        
        log_activity("System", "Data files cleanup completed")
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {str(e)}")

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def validate_json_file(file_path: str) -> bool:
    """Validate if a JSON file is properly formatted"""
    try:
        data = safe_load_json(file_path)
        return data is not None
    except:
        return False
