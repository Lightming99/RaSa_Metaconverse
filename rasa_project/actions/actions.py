from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

logger = logging.getLogger(__name__)

class ActionAskHowCanHelp(Action):
    def name(self) -> Text:
        return "action_ask_howcanhelp"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="How can I help you today?")
        return []

class ActionProvidePasswordReset(Action):
    def name(self) -> Text:
        return "action_provide_password_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("To reset your password:\n"
                  "1. Go to the login page\n"
                  "2. Click 'Forgot Password'\n"
                  "3. Enter your email address\n"
                  "4. Check your email for reset instructions\n"
                  "5. Follow the link and create a new password\n"
                  "6. Contact IT if you need additional assistance")
        
        dispatcher.utter_message(text=message)
        return []

class ActionProvideSoftwareInstallation(Action):
    def name(self) -> Text:
        return "action_provide_software_installation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("For software installation:\n"
                  "1. Download only from official websites\n"
                  "2. Run the installer as administrator\n"
                  "3. Follow the installation wizard\n"
                  "4. Restart your computer if prompted\n"
                  "5. Contact IT if you need admin rights")
        
        dispatcher.utter_message(text=message)
        return []

class ActionProvideNetworkHelp(Action):
    def name(self) -> Text:
        return "action_provide_network_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("For network connectivity issues:\n"
                  "1. Check all cable connections\n"
                  "2. Restart your router and modem\n"
                  "3. Try connecting to a different network\n"
                  "4. Check if other devices can connect\n"
                  "5. Run Windows network troubleshooter\n"
                  "6. Contact IT if the issue persists")
        
        dispatcher.utter_message(text=message)
        return []

class ActionLogIssue(Action):
    def name(self) -> Text:
        return "action_log_issue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Log the issue for tracking
        issue_type = tracker.get_slot("issue_type")
        
        logger.info(f"User reported issue: {issue_type}")
        
        dispatcher.utter_message(text="I've logged your issue. Is there anything else I can help you with?")
        return []

class ActionGetSystemInfo(Action):
    def name(self) -> Text:
        return "action_get_system_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("To check your system information:\n"
                  "1. Press Windows key + R\n"
                  "2. Type 'msinfo32' and press Enter\n"
                  "3. This will show your system specifications\n"
                  "4. You can also use 'dxdiag' for DirectX info")
        
        dispatcher.utter_message(text=message)
        return []

class ActionRestartServices(Action):
    def name(self) -> Text:
        return "action_restart_services"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("To restart Windows services:\n"
                  "1. Press Windows key + R\n"
                  "2. Type 'services.msc' and press Enter\n"
                  "3. Find the service you want to restart\n"
                  "4. Right-click and select 'Restart'\n"
                  "5. Be careful - only restart services you're sure about")
        
        dispatcher.utter_message(text=message)
        return []

class ActionCheckDiskSpace(Action):
    def name(self) -> Text:
        return "action_check_disk_space"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = ("To check available disk space:\n"
                  "1. Open File Explorer\n"
                  "2. Click on 'This PC' or 'My Computer'\n"
                  "3. You'll see available space on each drive\n"
                  "4. Right-click on a drive and select 'Properties' for details\n"
                  "5. Consider cleaning up if space is low")
        
        dispatcher.utter_message(text=message)
        return []
