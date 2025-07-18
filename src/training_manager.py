import json
import os
import yaml
import google.generativeai as genai
from datetime import datetime
from config.config import Config
from src.utils import log_activity, safe_load_json, safe_save_json
import subprocess
import shutil
import re
from collections import defaultdict
import hashlib
import traceback
import copy
from typing import Dict, List, Optional, Tuple, Any
import time

class TrainingManager:
    def __init__(self):
        self.config = Config()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.max_regeneration_attempts = 3
        self.max_processing_retries = 3
        self.feedback_threshold = self.load_feedback_threshold()
        self.debug_mode = True
        self.rejected_reviews_file = os.path.join(Config.DATA_DIR, "rejected.json")
        self.processed_reviews_file = os.path.join(Config.DATA_DIR, "processed_reviews.json")
        self.removable_reviews_file = os.path.join(Config.DATA_DIR, "removable_reviews.json")
        
        # Create directories
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # Analyze existing structure once
        self.existing_structure = self._analyze_existing_structure()
    
    def _analyze_existing_structure(self) -> Dict[str, Any]:
        """Analyze existing YAML structure to ensure perfect matching"""
        try:
            structure = {
                "nlu_format": "pipe_notation",
                "domain_format": "list_responses", 
                "stories_format": "simple_steps",
                "rules_format": "simple_steps",
                "existing_intents": [],
                "existing_responses": [],
                "existing_actions": []
            }
            
            # Analyze NLU structure
            nlu_file = os.path.join(Config.RASA_PROJECT_PATH, "data", "nlu.yml")
            if os.path.exists(nlu_file):
                with open(nlu_file, 'r', encoding='utf-8') as f:
                    nlu_data = yaml.safe_load(f)
                    if nlu_data and "nlu" in nlu_data:
                        for item in nlu_data["nlu"]:
                            if isinstance(item, dict) and "intent" in item:
                                structure["existing_intents"].append(item["intent"])
            
            # Analyze domain structure
            domain_file = os.path.join(Config.RASA_PROJECT_PATH, "domain.yml")
            if os.path.exists(domain_file):
                with open(domain_file, 'r', encoding='utf-8') as f:
                    domain_data = yaml.safe_load(f)
                    if domain_data:
                        if "intents" in domain_data:
                            structure["existing_intents"].extend(domain_data["intents"])
                        if "responses" in domain_data:
                            structure["existing_responses"].extend(list(domain_data["responses"].keys()))
                        if "actions" in domain_data:
                            structure["existing_actions"].extend(domain_data["actions"])
            
            # Remove duplicates
            structure["existing_intents"] = list(set(structure["existing_intents"]))
            structure["existing_responses"] = list(set(structure["existing_responses"]))
            structure["existing_actions"] = list(set(structure["existing_actions"]))
            
            log_activity("Training", f"Analyzed existing structure: {len(structure['existing_intents'])} intents")
            return structure
            
        except Exception as e:
            log_activity("Error", f"Failed to analyze existing structure: {str(e)}")
            return {"existing_intents": [], "existing_responses": [], "existing_actions": []}
    
    def load_feedback_threshold(self) -> int:
        """Load user-adjustable feedback threshold"""
        try:
            settings = safe_load_json(os.path.join(Config.DATA_DIR, "settings.json"), {})
            return settings.get("feedback_threshold", 5)
        except Exception as e:
            log_activity("Error", f"Failed to load feedback threshold: {str(e)}")
            return 5
    
    def save_feedback_threshold(self, threshold: int) -> None:
        """Save user-adjustable feedback threshold"""
        try:
            settings = safe_load_json(os.path.join(Config.DATA_DIR, "settings.json"), {})
            settings["feedback_threshold"] = threshold
            safe_save_json(os.path.join(Config.DATA_DIR, "settings.json"), settings)
            self.feedback_threshold = threshold
            log_activity("Settings", f"Feedback threshold updated to {threshold}")
        except Exception as e:
            log_activity("Error", f"Failed to save feedback threshold: {str(e)}")
    
    def process_feedback_for_training(self) -> str:
        """Process feedback and automatically train if threshold reached"""
        try:
            log_activity("Training", "=== STARTING FEEDBACK PROCESSING WITH AUTO-TRAINING ===")
            
            # Get truly unprocessed feedback
            unprocessed_feedback = self._get_truly_unprocessed_feedback()
            
            if not unprocessed_feedback:
                log_activity("Training", "No truly unprocessed feedback found")
                return "No feedback to process"
            
            log_activity("Training", f"Found {len(unprocessed_feedback)} truly unprocessed feedback entries")
            
            # Process each feedback
            successfully_processed = []
            failed_reviews = []
            
            for feedback in unprocessed_feedback:
                feedback_id = feedback.get("id")
                retry_count = feedback.get("retry_count", 0)
                
                log_activity("Training", f"=== PROCESSING FEEDBACK ID: {feedback_id} ===")
                
                if retry_count >= self.max_processing_retries:
                    log_activity("Training", f"❌ Feedback {feedback_id} exceeded max retries")
                    failed_reviews.append(feedback)
                    continue
                
                # Process with structure-aware method
                success = self._process_single_feedback_structure_aware(feedback)
                
                if success:
                    successfully_processed.append(feedback)
                    log_activity("Training", f"✅ Successfully processed feedback {feedback_id}")
                else:
                    feedback["retry_count"] = retry_count + 1
                    feedback["last_retry_timestamp"] = Config.get_timestamp()
                    
                    if feedback["retry_count"] >= self.max_processing_retries:
                        failed_reviews.append(feedback)
                        log_activity("Training", f"❌ Feedback {feedback_id} failed after {self.max_processing_retries} retries")
                    else:
                        log_activity("Training", f"⚠️ Feedback {feedback_id} will retry (attempt {feedback['retry_count']})")
            
            # Handle results
            if successfully_processed:
                self._mark_reviews_as_processed(successfully_processed)
                log_activity("Training", f"✅ Successfully processed {len(successfully_processed)} reviews")
                
                # Check if we should auto-train
                if len(successfully_processed) >= self.feedback_threshold:
                    log_activity("Training", "🎯 Auto-training threshold reached, starting training")
                    training_result = self._auto_train_model()
                    
                    if "successfully" in training_result:
                        # Move processed reviews to removable after successful training
                        self._move_processed_to_removable(successfully_processed)
                        log_activity("Training", "✅ Moved processed reviews to removable after training")
                        return f"Auto-training completed: {len(successfully_processed)} processed, training successful"
                    else:
                        log_activity("Training", f"⚠️ Auto-training failed: {training_result}")
                        return f"Reviews processed but training failed: {training_result}"
                
            if failed_reviews:
                self._mark_reviews_as_rejected(failed_reviews)
                log_activity("Training", f"❌ Rejected {len(failed_reviews)} reviews after max retries")
            
            # Update retry counts
            self._update_feedback_retry_counts(unprocessed_feedback, successfully_processed, failed_reviews)
            
            result_message = f"Review processing complete: {len(successfully_processed)} processed, {len(failed_reviews)} rejected"
            log_activity("Training", result_message)
            
            return result_message
                
        except Exception as e:
            error_msg = f"Review processing failed: {str(e)}\n{traceback.format_exc()}"
            log_activity("Error", error_msg)
            return f"Review processing failed: {str(e)}"
    
    def _get_truly_unprocessed_feedback(self) -> List[Dict]:
        """Get feedback that hasn't been processed or rejected"""
        try:
            from src.feedback_manager import FeedbackManager
            feedback_manager = FeedbackManager()
            
            # Get all unprocessed feedback
            unprocessed_feedback = feedback_manager.get_unprocessed_feedback()
            
            # Load processed, rejected, and removable reviews
            processed_reviews = safe_load_json(self.processed_reviews_file, [])
            rejected_reviews = safe_load_json(self.rejected_reviews_file, [])
            removable_reviews = safe_load_json(self.removable_reviews_file, [])
            
            # Create sets of processed, rejected, and removable IDs
            processed_ids = {str(review["id"]) for review in processed_reviews}
            rejected_ids = {str(review["id"]) for review in rejected_reviews}
            removable_ids = {str(review["id"]) for review in removable_reviews}
            
            # Filter out already processed, rejected, or removable
            truly_unprocessed = []
            for feedback in unprocessed_feedback:
                feedback_id = str(feedback.get("id", ""))
                if (feedback_id not in processed_ids and 
                    feedback_id not in rejected_ids and 
                    feedback_id not in removable_ids):
                    truly_unprocessed.append(feedback)
                else:
                    log_activity("Training", f"Skipping already handled feedback {feedback_id}")
            
            log_activity("Training", f"Original unprocessed: {len(unprocessed_feedback)}, Truly unprocessed: {len(truly_unprocessed)}")
            
            return truly_unprocessed
            
        except Exception as e:
            log_activity("Error", f"Failed to get truly unprocessed feedback: {str(e)}")
            return []
    
    def _process_single_feedback_structure_aware(self, feedback: Dict) -> bool:
        """Process single feedback with perfect structure awareness"""
        try:
            feedback_id = feedback.get("id")
            log_activity("Training", f"Processing feedback {feedback_id} with structure awareness")
            
            # Generate YAML that perfectly matches existing structure
            for attempt in range(self.max_regeneration_attempts):
                log_activity("Training", f"Structure-aware attempt {attempt + 1} for feedback {feedback_id}")
                
                # Generate YAML using Gemini with structure analysis
                yaml_content = self._generate_structure_matching_yaml(feedback, attempt)
                
                if not yaml_content:
                    log_activity("Training", f"❌ Failed to generate YAML for feedback {feedback_id}, attempt {attempt + 1}")
                    continue
                
                # Validate against existing structure
                validation_result = self._validate_yaml_against_structure(yaml_content, feedback_id)
                
                if not validation_result["valid"]:
                    log_activity("Training", f"❌ Structure validation failed for feedback {feedback_id}, attempt {attempt + 1}: {validation_result['reason']}")
                    continue
                
                # Merge with existing files using structure-aware method
                merge_result = self._merge_yaml_structure_aware(validation_result["parsed_data"], feedback_id)
                
                if merge_result:
                    log_activity("Training", f"✅ Successfully processed feedback {feedback_id} on attempt {attempt + 1}")
                    return True
                else:
                    log_activity("Training", f"❌ Merge failed for feedback {feedback_id}, attempt {attempt + 1}")
                    continue
            
            log_activity("Training", f"❌ All attempts failed for feedback {feedback_id}")
            return False
            
        except Exception as e:
            log_activity("Error", f"Structure-aware processing failed for feedback {feedback.get('id')}: {str(e)}")
            return False
    
    def _generate_structure_matching_yaml(self, feedback: Dict, attempt: int) -> Optional[str]:
        """Generate YAML using Gemini that perfectly matches existing structure"""
        try:
            feedback_id = feedback.get("id")
            log_activity("Training", f"Generating structure-matching YAML for feedback {feedback_id}")
            
            # Create enhanced prompt that includes structure analysis
            prompt = self._create_structure_aware_prompt(feedback, attempt)
            
            # Generate with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    max_output_tokens=2000
                )
            )
            
            if response.text:
                log_activity("Training", f"✅ Generated structure-matching YAML for feedback {feedback_id}")
                return response.text
            else:
                log_activity("Training", f"❌ Empty response from Gemini for feedback {feedback_id}")
                return None
                
        except Exception as e:
            log_activity("Error", f"Structure-matching YAML generation failed for feedback {feedback.get('id')}: {str(e)}")
            return None
    
    def _create_structure_aware_prompt(self, feedback: Dict, attempt: int) -> str:
        """Create prompt that ensures perfect structure matching"""
        try:
            user_query = feedback.get('user_query', 'N/A')
            bot_response = feedback.get('bot_response', 'N/A')
            feedback_type = feedback.get('feedback_type', 'unknown')
            issue_description = feedback.get('issue_description', 'N/A')
            expected_answer = feedback.get('expected_answer', 'N/A')
            
            # Create unique intent name
            intent_name = self._create_structure_aware_intent_name(user_query, feedback.get('id'))
            response_name = f"utter_{intent_name}"
            
            # Analyze feedback to create better response
            if feedback_type == "negative" and expected_answer and expected_answer.strip() != "N/A":
                response_text = f"I can help you with that. {expected_answer.strip()}"
            elif issue_description and issue_description.strip() != "N/A":
                response_text = f"I understand your concern about {issue_description.strip()}. Let me help you resolve this IT issue."
            else:
                response_text = "I can assist you with that IT support request. Let me help you resolve this issue."
            
            # Create query variations
            query_variations = self._create_intelligent_variations(user_query)
            
            prompt = f"""You are an expert Rasa YAML generator. Generate training data that EXACTLY matches the existing structure format.

FEEDBACK ANALYSIS:
- User Query: "{user_query}"
- Bot Response: "{bot_response}"
- Feedback Type: {feedback_type}
- Issue: "{issue_description}"
- Expected Answer: "{expected_answer}"

STRUCTURE REQUIREMENTS:
- NLU: Use pipe notation (|) for examples, EXACTLY like existing format
- Domain: Follow existing response format with "- text:" structure
- Stories: Simple steps format with intent and action
- Rules: Simple steps format with intent and action

EXISTING STRUCTURE ANALYSIS:
- Total existing intents: {len(self.existing_structure['existing_intents'])}
- Intent naming pattern: ask_[topic]_[detail]
- Response naming pattern: utter_[intent_name]

GENERATE EXACTLY THIS STRUCTURE:

=== NLU_DATA ===
version: '3.1'
nlu:
- intent: {intent_name}
  examples: |-
    - {user_query}
    - {query_variations[0]}
    - {query_variations[1]}
    - {query_variations[2]}

=== DOMAIN_DATA ===
version: '3.1'
intents:
- {intent_name}
responses:
  {response_name}:
  - text: "{response_text}"

=== STORIES_DATA ===
version: '3.1'
stories:
- story: {intent_name}_story
  steps:
  - intent: {intent_name}
  - action: {response_name}

=== RULES_DATA ===
version: '3.1'
rules:
- rule: {intent_name}_rule
  steps:
  - intent: {intent_name}
  - action: {response_name}

CRITICAL: 
- Use EXACTLY the format shown above
- Use pipe notation |- for examples
- Use single quotes for version
- Ensure response text addresses the user's actual problem
- Intent name must be unique and descriptive
"""
            
            return prompt
            
        except Exception as e:
            log_activity("Error", f"Structure-aware prompt creation failed: {str(e)}")
            return self._create_fallback_prompt(feedback)
    
    def _create_structure_aware_intent_name(self, user_query: str, feedback_id: str) -> str:
        """Create intent name that follows existing naming pattern"""
        try:
            # Clean user query
            query_lower = user_query.lower().strip()
            
            # Extract meaningful words
            words = [word for word in re.findall(r'\b\w+\b', query_lower) if len(word) > 2]
            
            # Remove common words
            common_words = {'the', 'and', 'are', 'for', 'you', 'can', 'how', 'what', 'why', 'when', 'where', 'with', 'from', 'that', 'this', 'have', 'has', 'will', 'would', 'could', 'should'}
            meaningful_words = [word for word in words if word not in common_words]
            
            # Create base name following existing pattern
            if len(meaningful_words) >= 2:
                base_name = f"ask_{meaningful_words[0]}_{meaningful_words[1]}"
            elif len(meaningful_words) == 1:
                base_name = f"ask_{meaningful_words[0]}_help"
            else:
                base_name = f"ask_support_{feedback_id}"
            
            # Clean the name
            base_name = re.sub(r'[^a-zA-Z0-9_]', '', base_name)
            
            # Ensure uniqueness
            intent_name = base_name
            counter = 1
            while intent_name in self.existing_structure['existing_intents']:
                intent_name = f"{base_name}_{counter}"
                counter += 1
            
            return intent_name
            
        except Exception as e:
            log_activity("Error", f"Intent name creation failed: {str(e)}")
            return f"ask_support_{feedback_id}"
    
    def _create_intelligent_variations(self, user_query: str) -> List[str]:
        """Create intelligent variations of user query"""
        try:
            base_query = user_query.strip()
            
            variations = [
                f"Can you help me with {base_query.lower()}",
                f"I need assistance with {base_query.lower()}",
                f"How do I resolve {base_query.lower()}"
            ]
            
            # Add more specific variations based on query content
            if "password" in base_query.lower():
                variations.append("I'm having trouble with my password")
            elif "install" in base_query.lower():
                variations.append("Help me install this software")
            elif "network" in base_query.lower() or "internet" in base_query.lower():
                variations.append("I'm having connectivity issues")
            elif "slow" in base_query.lower() or "performance" in base_query.lower():
                variations.append("My system is running slowly")
            
            return variations[:4]  # Return first 4 variations
            
        except Exception as e:
            log_activity("Error", f"Variations creation failed: {str(e)}")
            return [
                "Can you help me with this issue",
                "I need assistance with this problem",
                "How do I resolve this",
                "Please help me with this"
            ]
    
    def _validate_yaml_against_structure(self, yaml_content: str, feedback_id: str) -> Dict[str, Any]:
        """Validate YAML against existing structure"""
        try:
            log_activity("Training", f"Validating YAML structure for feedback {feedback_id}")
            
            # Parse sections
            sections = self._parse_yaml_sections_enhanced(yaml_content)
            
            if not sections:
                return {"valid": False, "reason": "Failed to parse sections"}
            
            # Validate each section
            parsed_sections = {}
            
            for section_name, section_content in sections.items():
                try:
                    # Parse YAML
                    parsed_data = yaml.safe_load(section_content)
                    
                    if not parsed_data:
                        return {"valid": False, "reason": f"Empty YAML in {section_name}"}
                    
                    # Structure validation
                    if not self._validate_section_structure_enhanced(section_name, parsed_data):
                        return {"valid": False, "reason": f"Invalid structure in {section_name}"}
                    
                    parsed_sections[section_name] = parsed_data
                    log_activity("Training", f"✅ {section_name} section validated for feedback {feedback_id}")
                    
                except yaml.YAMLError as e:
                    log_activity("Training", f"❌ YAML error in {section_name} for feedback {feedback_id}: {str(e)}")
                    return {"valid": False, "reason": f"YAML syntax error in {section_name}: {str(e)}"}
            
            log_activity("Training", f"✅ All YAML structure validation passed for feedback {feedback_id}")
            return {"valid": True, "parsed_data": parsed_sections}
            
        except Exception as e:
            log_activity("Error", f"YAML structure validation failed for feedback {feedback_id}: {str(e)}")
            return {"valid": False, "reason": f"Validation exception: {str(e)}"}
    
    def _parse_yaml_sections_enhanced(self, yaml_content: str) -> Optional[Dict[str, str]]:
        """Enhanced YAML section parsing"""
        try:
            sections = {"nlu": "", "domain": "", "stories": "", "rules": ""}
            
            lines = yaml_content.split('\n')
            current_section = None
            
            for line in lines:
                line_stripped = line.strip()
                
                if "=== NLU_DATA ===" in line_stripped:
                    current_section = "nlu"
                elif "=== DOMAIN_DATA ===" in line_stripped:
                    current_section = "domain"
                elif "=== STORIES_DATA ===" in line_stripped:
                    current_section = "stories"
                elif "=== RULES_DATA ===" in line_stripped:
                    current_section = "rules"
                elif current_section and line_stripped and not line_stripped.startswith('==='):
                    sections[current_section] += line + "\n"
            
            # Validate all sections have content
            for section_name, content in sections.items():
                if not content.strip():
                    log_activity("Training", f"❌ Empty {section_name} section")
                    return None
            
            return sections
            
        except Exception as e:
            log_activity("Error", f"Enhanced section parsing failed: {str(e)}")
            return None
    
    def _validate_section_structure_enhanced(self, section_name: str, parsed_data: Dict) -> bool:
        """Enhanced section structure validation"""
        try:
            if section_name == "nlu":
                return ("nlu" in parsed_data and 
                       isinstance(parsed_data["nlu"], list) and 
                       len(parsed_data["nlu"]) > 0 and
                       all("intent" in item and "examples" in item for item in parsed_data["nlu"] if isinstance(item, dict)))
            
            elif section_name == "domain":
                has_intents = "intents" in parsed_data and isinstance(parsed_data["intents"], list)
                has_responses = "responses" in parsed_data and isinstance(parsed_data["responses"], dict)
                return has_intents or has_responses
            
            elif section_name == "stories":
                return ("stories" in parsed_data and 
                       isinstance(parsed_data["stories"], list) and 
                       len(parsed_data["stories"]) > 0 and
                       all("story" in item and "steps" in item for item in parsed_data["stories"] if isinstance(item, dict)))
            
            elif section_name == "rules":
                return ("rules" in parsed_data and 
                       isinstance(parsed_data["rules"], list) and 
                       len(parsed_data["rules"]) > 0 and
                       all("rule" in item and "steps" in item for item in parsed_data["rules"] if isinstance(item, dict)))
            
            return False
            
        except Exception as e:
            log_activity("Error", f"Enhanced structure validation failed for {section_name}: {str(e)}")
            return False
    
    def _merge_yaml_structure_aware(self, parsed_sections: Dict[str, Any], feedback_id: str) -> bool:
        """Structure-aware YAML merging"""
        try:
            log_activity("Training", f"Starting structure-aware merge for feedback {feedback_id}")
            
            # Create backup
            self._create_backup()
            
            # Define file paths
            file_paths = {
                "nlu": os.path.join(Config.RASA_PROJECT_PATH, "data", "nlu.yml"),
                "domain": os.path.join(Config.RASA_PROJECT_PATH, "domain.yml"),
                "stories": os.path.join(Config.RASA_PROJECT_PATH, "data", "stories.yml"),
                "rules": os.path.join(Config.RASA_PROJECT_PATH, "data", "rules.yml")
            }
            
            # Merge each section
            for section_name, new_data in parsed_sections.items():
                file_path = file_paths[section_name]
                
                if not self._merge_single_section_structure_aware(section_name, file_path, new_data, feedback_id):
                    log_activity("Training", f"❌ Failed to merge {section_name} for feedback {feedback_id}")
                    self._restore_backup()
                    return False
            
            # Validate all files after merge
            if not self._validate_all_files_final():
                log_activity("Training", f"❌ Post-merge validation failed for feedback {feedback_id}")
                self._restore_backup()
                return False
            
            log_activity("Training", f"✅ Structure-aware merge completed for feedback {feedback_id}")
            return True
            
        except Exception as e:
            log_activity("Error", f"Structure-aware merge failed for feedback {feedback_id}: {str(e)}")
            self._restore_backup()
            return False
    
    def _merge_single_section_structure_aware(self, section_name: str, file_path: str, new_data: Dict, feedback_id: str) -> bool:
        """Structure-aware single section merge"""
        try:
            log_activity("Training", f"Structure-aware merging {section_name} for feedback {feedback_id}")
            
            # Load existing data
            existing_data = self._load_existing_data_safe(file_path)
            
            # Merge based on section type with structure awareness
            if section_name == "nlu":
                merged_data = self._merge_nlu_structure_aware(existing_data, new_data)
            elif section_name == "domain":
                merged_data = self._merge_domain_structure_aware(existing_data, new_data)
            elif section_name == "stories":
                merged_data = self._merge_stories_structure_aware(existing_data, new_data)
            elif section_name == "rules":
                merged_data = self._merge_rules_structure_aware(existing_data, new_data)
            else:
                log_activity("Training", f"❌ Unknown section type: {section_name}")
                return False
            
            if not merged_data:
                log_activity("Training", f"❌ Merge operation returned empty data for {section_name}")
                return False
            
            # Save merged data with preserved formatting
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(merged_data, f, default_flow_style=False, sort_keys=False, 
                             allow_unicode=True, width=1000, indent=2)
                
                log_activity("Training", f"✅ Successfully saved merged {section_name} for feedback {feedback_id}")
                return True
                
            except Exception as e:
                log_activity("Training", f"❌ Failed to save {section_name} for feedback {feedback_id}: {str(e)}")
                return False
            
        except Exception as e:
            log_activity("Error", f"Structure-aware section merge failed for {section_name}, feedback {feedback_id}: {str(e)}")
            return False
    
    def _merge_nlu_structure_aware(self, existing: Dict, new: Dict) -> Optional[Dict]:
        """Structure-aware NLU merging"""
        try:
            merged = copy.deepcopy(existing) if existing else {"version": "3.1"}
            
            if "nlu" not in merged:
                merged["nlu"] = []
            
            if not isinstance(merged["nlu"], list):
                merged["nlu"] = []
            
            # Get existing intents
            existing_intents = set()
            for item in merged["nlu"]:
                if isinstance(item, dict) and "intent" in item:
                    existing_intents.add(item["intent"])
            
            # Add new intents
            if "nlu" in new and isinstance(new["nlu"], list):
                for item in new["nlu"]:
                    if isinstance(item, dict) and "intent" in item:
                        intent_name = item["intent"]
                        if intent_name not in existing_intents:
                            merged["nlu"].append(item)
                            existing_intents.add(intent_name)
                            log_activity("Training", f"✅ Added NLU intent: {intent_name}")
            
            return merged
            
        except Exception as e:
            log_activity("Error", f"Structure-aware NLU merge failed: {str(e)}")
            return None
    
    def _merge_domain_structure_aware(self, existing: Dict, new: Dict) -> Optional[Dict]:
        """Structure-aware domain merging"""
        try:
            merged = copy.deepcopy(existing) if existing else {"version": "3.1"}
            
            # Merge intents
            if "intents" in new and isinstance(new["intents"], list):
                if "intents" not in merged:
                    merged["intents"] = []
                
                if not isinstance(merged["intents"], list):
                    merged["intents"] = []
                
                for intent in new["intents"]:
                    if intent not in merged["intents"]:
                        merged["intents"].append(intent)
                        log_activity("Training", f"✅ Added domain intent: {intent}")
            
            # Merge responses
            if "responses" in new and isinstance(new["responses"], dict):
                if "responses" not in merged:
                    merged["responses"] = {}
                
                if not isinstance(merged["responses"], dict):
                    merged["responses"] = {}
                
                for response_key, response_value in new["responses"].items():
                    if response_key not in merged["responses"]:
                        merged["responses"][response_key] = response_value
                        log_activity("Training", f"✅ Added domain response: {response_key}")
                        
                        # Also add to actions if not present
                        if "actions" not in merged:
                            merged["actions"] = []
                        if response_key not in merged["actions"]:
                            merged["actions"].append(response_key)
            
            return merged
            
        except Exception as e:
            log_activity("Error", f"Structure-aware domain merge failed: {str(e)}")
            return None
    
    def _merge_stories_structure_aware(self, existing: Dict, new: Dict) -> Optional[Dict]:
        """Structure-aware stories merging"""
        try:
            merged = copy.deepcopy(existing) if existing else {"version": "3.1"}
            
            if "stories" not in merged:
                merged["stories"] = []
            
            if not isinstance(merged["stories"], list):
                merged["stories"] = []
            
            # Get existing story names
            existing_story_names = set()
            for story in merged["stories"]:
                if isinstance(story, dict) and "story" in story:
                    existing_story_names.add(story["story"])
            
            # Add new stories
            if "stories" in new and isinstance(new["stories"], list):
                for story in new["stories"]:
                    if isinstance(story, dict) and "story" in story:
                        story_name = story["story"]
                        if story_name not in existing_story_names:
                            merged["stories"].append(story)
                            existing_story_names.add(story_name)
                            log_activity("Training", f"✅ Added story: {story_name}")
            
            return merged
            
        except Exception as e:
            log_activity("Error", f"Structure-aware stories merge failed: {str(e)}")
            return None
    
    def _merge_rules_structure_aware(self, existing: Dict, new: Dict) -> Optional[Dict]:
        """Structure-aware rules merging"""
        try:
            merged = copy.deepcopy(existing) if existing else {"version": "3.1"}
            
            if "rules" not in merged:
                merged["rules"] = []
            
            if not isinstance(merged["rules"], list):
                merged["rules"] = []
            
            # Get existing rule names
            existing_rule_names = set()
            for rule in merged["rules"]:
                if isinstance(rule, dict) and "rule" in rule:
                    existing_rule_names.add(rule["rule"])
            
            # Add new rules
            if "rules" in new and isinstance(new["rules"], list):
                for rule in new["rules"]:
                    if isinstance(rule, dict) and "rule" in rule:
                        rule_name = rule["rule"]
                        if rule_name not in existing_rule_names:
                            merged["rules"].append(rule)
                            existing_rule_names.add(rule_name)
                            log_activity("Training", f"✅ Added rule: {rule_name}")
            
            return merged
            
        except Exception as e:
            log_activity("Error", f"Structure-aware rules merge failed: {str(e)}")
            return None
    
    def _auto_train_model(self) -> str:
        """Automatically train model when threshold reached"""
        try:
            log_activity("Training", "=== AUTO-TRAINING MODEL ===")
            
            # Validate all files before training
            if not self._validate_all_files_final():
                log_activity("Error", "Auto-training failed: File validation failed")
                return "❌ Auto-training failed: Invalid Rasa files"
            
            # Start training
            log_activity("Training", "Starting automatic Rasa model training")
            
            result = subprocess.run([
                "rasa", "train", "--force"
            ], cwd=Config.RASA_PROJECT_PATH, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                log_activity("Training", "✅ Auto-training completed successfully")
                log_activity("Training", f"Training output: {result.stdout}")
                
                # Restart server
                server_restart = self._restart_rasa_server()
                
                if server_restart:
                    return "✅ Auto-training completed successfully"
                else:
                    return "⚠️ Auto-training completed but server restart failed"
            else:
                log_activity("Error", f"❌ Auto-training failed: {result.stderr}")
                return f"❌ Auto-training failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            log_activity("Error", "❌ Auto-training timeout")
            return "❌ Auto-training timeout"
        except Exception as e:
            log_activity("Error", f"Auto-training failed: {str(e)}")
            return f"❌ Auto-training failed: {str(e)}"
    
    def manual_training(self) -> str:
        """Manual training with processed review movement"""
        try:
            log_activity("Training", "=== MANUAL TRAINING INITIATED ===")
            
            # Get processed reviews count
            processed_count = self._get_processed_reviews_count()
            log_activity("Training", f"Found {processed_count} processed reviews for training")
            
            if processed_count == 0:
                log_activity("Training", "⚠️ No processed reviews found, training with existing data only")
            
            # Validate all files before training
            if not self._validate_all_files_final():
                log_activity("Error", "Manual training failed: File validation failed")
                return "❌ Manual training failed: Invalid Rasa files"
            
            # Start training
            log_activity("Training", "Starting manual Rasa model training")
            
            result = subprocess.run([
                "rasa", "train", "--force"
            ], cwd=Config.RASA_PROJECT_PATH, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                log_activity("Training", "✅ Manual training completed successfully")
                log_activity("Training", f"Training output: {result.stdout}")
                
                # Move processed reviews to removable after successful training
                if processed_count > 0:
                    processed_reviews = safe_load_json(self.processed_reviews_file, [])
                    self._move_processed_to_removable(processed_reviews)
                    log_activity("Training", f"✅ Moved {processed_count} processed reviews to removable after manual training")
                
                # Restart server
                server_restart = self._restart_rasa_server()
                
                if server_restart:
                    return "✅ Manual training completed successfully"
                else:
                    return "⚠️ Manual training completed but server restart failed"
            else:
                log_activity("Error", f"❌ Manual training failed: {result.stderr}")
                return f"❌ Manual training failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            log_activity("Error", "❌ Manual training timeout")
            return "❌ Manual training timeout"
        except Exception as e:
            log_activity("Error", f"Manual training failed: {str(e)}")
            return f"❌ Manual training failed: {str(e)}"
    
    def _move_processed_to_removable(self, processed_reviews: List[Dict]) -> None:
        """Move processed reviews to removable after successful training"""
        try:
            # Load existing removable reviews
            removable_reviews = safe_load_json(self.removable_reviews_file, [])
            
            # Add processed reviews to removable with training timestamp
            for review in processed_reviews:
                removable_entry = {
                    "id": str(review["id"]),
                    "original_processed_timestamp": review.get("processed_timestamp"),
                    "moved_to_removable_timestamp": Config.get_timestamp(),
                    "user_query": review.get("user_query", ""),
                    "feedback_type": review.get("feedback_type", ""),
                    "training_completed": True
                }
                removable_reviews.append(removable_entry)
            
            # Save removable reviews
            safe_save_json(self.removable_reviews_file, removable_reviews)
            
            # Clear processed reviews file
            safe_save_json(self.processed_reviews_file, [])
            
            log_activity("Training", f"✅ Moved {len(processed_reviews)} reviews from processed to removable")
            
        except Exception as e:
            log_activity("Error", f"Failed to move processed to removable: {str(e)}")
    
    def _load_existing_data_safe(self, file_path: str) -> Dict:
        """Safely load existing data"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    return data if data else {}
            return {}
        except Exception as e:
            log_activity("Error", f"Failed to load {file_path}: {str(e)}")
            return {}
    
    def _validate_all_files_final(self) -> bool:
        """Final validation of all files"""
        try:
            files_to_validate = [
                ("domain.yml", os.path.join(Config.RASA_PROJECT_PATH, "domain.yml")),
                ("nlu.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "nlu.yml")),
                ("stories.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "stories.yml")),
                ("rules.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "rules.yml"))
            ]
            
            for file_name, file_path in files_to_validate:
                if not os.path.exists(file_path):
                    log_activity("Training", f"❌ File missing: {file_path}")
                    return False
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        yaml_data = yaml.safe_load(f)
                        if not yaml_data:
                            log_activity("Training", f"❌ Empty file: {file_name}")
                            return False
                    
                    log_activity("Training", f"✅ {file_name} validated")
                    
                except yaml.YAMLError as e:
                    log_activity("Training", f"❌ YAML error in {file_name}: {str(e)}")
                    return False
            
            log_activity("Training", "✅ All files validated successfully")
            return True
            
        except Exception as e:
            log_activity("Error", f"Final validation failed: {str(e)}")
            return False
    
    def _create_backup(self) -> None:
        """Create backup of existing files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(Config.RASA_PROJECT_PATH, f"backup_{timestamp}")
            
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup data directory
            data_dir = os.path.join(Config.RASA_PROJECT_PATH, "data")
            if os.path.exists(data_dir):
                shutil.copytree(data_dir, os.path.join(backup_dir, "data"))
            
            # Backup domain file
            domain_file = os.path.join(Config.RASA_PROJECT_PATH, "domain.yml")
            if os.path.exists(domain_file):
                shutil.copy2(domain_file, os.path.join(backup_dir, "domain.yml"))
            
            log_activity("Training", f"✅ Backup created: {backup_dir}")
            
        except Exception as e:
            log_activity("Error", f"Failed to create backup: {str(e)}")
    
    def _restore_backup(self) -> None:
        """Restore from most recent backup"""
        try:
            backup_dirs = [d for d in os.listdir(Config.RASA_PROJECT_PATH) if d.startswith("backup_")]
            if not backup_dirs:
                return
            
            latest_backup = max(backup_dirs)
            backup_dir = os.path.join(Config.RASA_PROJECT_PATH, latest_backup)
            
            # Restore data directory
            data_dir = os.path.join(Config.RASA_PROJECT_PATH, "data")
            backup_data_dir = os.path.join(backup_dir, "data")
            
            if os.path.exists(backup_data_dir):
                if os.path.exists(data_dir):
                    shutil.rmtree(data_dir)
                shutil.copytree(backup_data_dir, data_dir)
            
            # Restore domain file
            domain_file = os.path.join(Config.RASA_PROJECT_PATH, "domain.yml")
            backup_domain_file = os.path.join(backup_dir, "domain.yml")
            
            if os.path.exists(backup_domain_file):
                shutil.copy2(backup_domain_file, domain_file)
            
            log_activity("Training", f"✅ Restored from backup: {latest_backup}")
            
        except Exception as e:
            log_activity("Error", f"Failed to restore backup: {str(e)}")
    
    def _mark_reviews_as_processed(self, processed_reviews: List[Dict]) -> None:
        """Mark reviews as processed"""
        try:
            from src.feedback_manager import FeedbackManager
            feedback_manager = FeedbackManager()
            
            # Mark in feedback manager
            feedback_ids = [str(review["id"]) for review in processed_reviews]
            feedback_manager.mark_feedback_processed(feedback_ids)
            
            # Track in processed reviews file
            existing_processed = safe_load_json(self.processed_reviews_file, [])
            
            for review in processed_reviews:
                processed_entry = {
                    "id": str(review["id"]),
                    "processed_timestamp": Config.get_timestamp(),
                    "user_query": review.get("user_query", ""),
                    "feedback_type": review.get("feedback_type", ""),
                    "processing_success": True
                }
                existing_processed.append(processed_entry)
            
            safe_save_json(self.processed_reviews_file, existing_processed)
            log_activity("Training", f"✅ Marked {len(processed_reviews)} reviews as processed")
            
        except Exception as e:
            log_activity("Error", f"Failed to mark reviews as processed: {str(e)}")
    
    def _mark_reviews_as_rejected(self, rejected_reviews: List[Dict]) -> None:
        """Mark reviews as rejected"""
        try:
            existing_rejected = safe_load_json(self.rejected_reviews_file, [])
            
            for review in rejected_reviews:
                rejected_entry = {
                    "id": str(review["id"]),
                    "rejection_timestamp": Config.get_timestamp(),
                    "rejection_reason": f"Failed after {self.max_processing_retries} attempts",
                    "user_query": review.get("user_query", ""),
                    "feedback_type": review.get("feedback_type", ""),
                    "retry_count": review.get("retry_count", 0)
                }
                existing_rejected.append(rejected_entry)
            
            safe_save_json(self.rejected_reviews_file, existing_rejected)
            log_activity("Training", f"✅ Marked {len(rejected_reviews)} reviews as rejected")
            
        except Exception as e:
            log_activity("Error", f"Failed to mark reviews as rejected: {str(e)}")
    
    def _update_feedback_retry_counts(self, original_feedback: List[Dict], processed: List[Dict], rejected: List[Dict]) -> None:
        """Update feedback retry counts"""
        try:
            current_feedback = safe_load_json(Config.FEEDBACK_DATA_FILE, [])
            
            processed_ids = {str(f["id"]) for f in processed}
            rejected_ids = {str(f["id"]) for f in rejected}
            
            for feedback in current_feedback:
                if str(feedback["id"]) not in processed_ids and str(feedback["id"]) not in rejected_ids:
                    for orig_feedback in original_feedback:
                        if str(orig_feedback["id"]) == str(feedback["id"]):
                            feedback["retry_count"] = orig_feedback.get("retry_count", 0)
                            feedback["last_retry_timestamp"] = orig_feedback.get("last_retry_timestamp", "")
                            break
            
            safe_save_json(Config.FEEDBACK_DATA_FILE, current_feedback)
            log_activity("Training", "✅ Updated feedback retry counts")
            
        except Exception as e:
            log_activity("Error", f"Failed to update feedback retry counts: {str(e)}")
    
    def _get_processed_reviews_count(self) -> int:
        """Get count of processed reviews"""
        try:
            processed_reviews = safe_load_json(self.processed_reviews_file, [])
            return len(processed_reviews)
        except Exception as e:
            log_activity("Error", f"Failed to get processed reviews count: {str(e)}")
            return 0
    
    def _restart_rasa_server(self) -> bool:
        """Restart Rasa server"""
        try:
            log_activity("Training", "Restarting Rasa server")
            
            # Kill existing processes
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(["taskkill", "/f", "/im", "rasa.exe"], capture_output=True)
                else:  # Unix-like
                    subprocess.run(["pkill", "-f", "rasa"], capture_output=True)
            except Exception as e:
                log_activity("Training", f"Process kill attempt: {str(e)}")
            
            time.sleep(5)
            
            # Start new server
            try:
                subprocess.Popen([
                    "rasa", "run", "--enable-api", "--cors", "*", "--port", "5005"
                ], cwd=Config.RASA_PROJECT_PATH)
                
                time.sleep(10)
                
                log_activity("Training", "✅ Rasa server restarted")
                return True
                
            except Exception as e:
                log_activity("Error", f"Failed to start server: {str(e)}")
                return False
            
        except Exception as e:
            log_activity("Error", f"Server restart failed: {str(e)}")
            return False
    
    def _create_fallback_prompt(self, feedback: Dict) -> str:
        """Create fallback prompt"""
        user_query = feedback.get("user_query", "help me")
        
        return f"""Generate valid Rasa YAML training data with this exact structure:

=== NLU_DATA ===
version: '3.1'
nlu:
- intent: ask_it_support
  examples: |-
    - {user_query}
    - help me with this
    - I need assistance
    - can you help me

=== DOMAIN_DATA ===
version: '3.1'
intents:
- ask_it_support
responses:
  utter_it_support:
  - text: "I can help you with that IT support request."

=== STORIES_DATA ===
version: '3.1'
stories:
- story: it_support_story
  steps:
  - intent: ask_it_support
  - action: utter_it_support

=== RULES_DATA ===
version: '3.1'
rules:
- rule: it_support_rule
  steps:
  - intent: ask_it_support
  - action: utter_it_support

Use exactly this format with proper indentation.
"""
    
    # Additional utility methods
    def process_reviews_manual(self) -> str:
        """Manual review processing"""
        try:
            log_activity("Training", "Manual review processing initiated")
            return self.process_feedback_for_training()
            
        except Exception as e:
            log_activity("Error", f"Manual review processing failed: {str(e)}")
            return f"Manual review processing failed: {str(e)}"
    
    def get_rejected_reviews_count(self) -> int:
        """Get count of rejected reviews"""
        try:
            rejected_reviews = safe_load_json(self.rejected_reviews_file, [])
            return len(rejected_reviews)
        except Exception as e:
            log_activity("Error", f"Failed to get rejected reviews count: {str(e)}")
            return 0
    
    def get_processed_reviews(self) -> List[Dict]:
        """Get processed reviews for viewing"""
        try:
            return safe_load_json(self.processed_reviews_file, [])
        except Exception as e:
            log_activity("Error", f"Failed to get processed reviews: {str(e)}")
            return []
    
    def get_removable_reviews(self) -> List[Dict]:
        """Get removable reviews for viewing"""
        try:
            return safe_load_json(self.removable_reviews_file, [])
        except Exception as e:
            log_activity("Error", f"Failed to get removable reviews: {str(e)}")
            return []
    
    def clear_processed_reviews(self) -> str:
        """Clear processed reviews"""
        try:
            safe_save_json(self.processed_reviews_file, [])
            log_activity("Admin", "Processed reviews cleared")
            return "✅ Processed reviews cleared"
        except Exception as e:
            log_activity("Error", f"Failed to clear processed reviews: {str(e)}")
            return f"❌ Failed to clear processed reviews: {str(e)}"
    
    def clear_rejected_reviews(self) -> str:
        """Clear rejected reviews"""
        try:
            safe_save_json(self.rejected_reviews_file, [])
            log_activity("Admin", "Rejected reviews cleared")
            return "✅ Rejected reviews cleared"
        except Exception as e:
            log_activity("Error", f"Failed to clear rejected reviews: {str(e)}")
            return f"❌ Failed to clear rejected reviews: {str(e)}"
    
    def clear_removable_reviews(self) -> str:
        """Clear removable reviews"""
        try:
            safe_save_json(self.removable_reviews_file, [])
            log_activity("Admin", "Removable reviews cleared")
            return "✅ Removable reviews cleared"
        except Exception as e:
            log_activity("Error", f"Failed to clear removable reviews: {str(e)}")
            return f"❌ Failed to clear removable reviews: {str(e)}"
