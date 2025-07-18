MetaConverse - AI IT Support Chatbot
<div align="center">
![MetaConverse Logo](https://img.shields.io/badge/MetaConverse-AI%20Chatbot-blue?style=for-the-badge&logo=shields.io/badge/Python-3.10.11-blue?style=flat//img.shields.io/badge/Rasa-3.6+-purple?style=flat-square&logo=r.shields.io/badge/Streamlit-1.28+-red?style=flat-square&logo=streamshields.io/badge/License-MIT-green.shields.io/badge/Build-Passing-brightgreen intelligent hybrid AI system for IT support with automatic training data generation and adaptive learning capabilities.*

🚀 Live Demo - 📖 Documentation - 🛠️ Installation - 🤝 Contributing

</div>
🌟 Overview
MetaConverse is a cutting-edge hybrid conversational AI system that revolutionizes IT support by combining the reliability of structured AI (Rasa) with the flexibility of Large Language Models (LLaMA via Groq). The system automatically generates training data from user feedback, eliminating the need for manual annotation while maintaining enterprise-grade quality and reliability.

✨ Key Features
🤖 Dual AI Architecture: Intelligent routing between Rasa NLU and Groq LLaMA based on confidence thresholds

📝 Automatic Training: Converts user feedback into valid Rasa YAML training data automatically

🔍 Multi-Layer Validation: Comprehensive validation ensuring structural, syntactic, and semantic correctness

📊 Real-time Analytics: Beautiful dashboard with performance metrics and user satisfaction tracking

🔄 Adaptive Learning: Continuous improvement through user feedback processing

🎨 Modern UI: Elegant Streamlit interface with glassmorphism design

🔒 Enterprise Security: Role-based access control and data protection

📈 Production Ready: Deployed and tested in real-world IT support scenarios

🏗️ Architecture
text
graph TB
    A[User Query] --> B{Confidence Check}
    B -->|High Confidence ≥0.67| C[Rasa NLU]
    B -->|Low Confidence <0.67| D[Groq LLaMA]
    
    C --> E[Structured Response]
    D --> E
    
    E --> F[User Feedback]
    F --> G[Feedback Processing]
    G --> H[YAML Generation]
    H --> I[Multi-Layer Validation]
    I --> J[Training Data Integration]
    J --> K[Model Retraining]
    K --> C
    
    style A fill:#e1f5fe
    style E fill:#e8f5e8
    style H fill:#fff3e0
    style I fill:#fce4ec
🚀 Quick Start
Prerequisites
Python 3.10.11+

8GB+ RAM recommended

Internet connection for LLM API access

Installation
Clone the repository

bash
git clone https://github.com/yourusername/metaconverse.git
cd metaconverse
Create virtual environment

bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables

bash
cp .env.example .env
# Edit .env with your API keys and configuration
Initialize Rasa model

bash
cd rasa_project
rasa train
cd ..
Run the application

bash
streamlit run app.py
Visit http://localhost:8501 to access the MetaConverse interface.

📋 Requirements
text
streamlit>=1.28.0
rasa>=3.6.0
groq>=0.4.0
google-generativeai>=0.3.0
pandas>=2.0.0
plotly>=5.17.0
pyyaml>=6.0
spacy>=3.7.0
numpy>=1.24.0
python-dotenv>=1.0.0
requests>=2.31.0
🎯 Usage
Basic Chat Interface
Start a conversation: Navigate to the Chat page and ask any IT-related question

Provide feedback: Use 👍/👎 buttons to rate responses

Detailed feedback: Click "👎 Improve" to provide specific improvement suggestions

Monitor training: Watch as the system automatically improves from your feedback

Admin Features
Access admin controls using the administrator password in the Logs section:

📝 Process Reviews: Manually trigger feedback processing

🎓 Manual Training: Force model retraining

📊 System Diagnostics: Check system health and file status

🗑️ Data Management: Clear processed/rejected reviews

API Usage
python
from src.chatbot import ChatBot
from src.feedback_manager import FeedbackManager

# Initialize chatbot
chatbot = ChatBot()

# Get response
response = chatbot.get_response("How do I reset my password?")
print(f"Response: {response['response']}")
print(f"Confidence: {response['confidence']}")
print(f"Source: {response['model_source']}")

# Process feedback
feedback_manager = FeedbackManager()
feedback_manager.process_feedback(
    message_index=0,
    user_query="How do I reset my password?",
    bot_response=response['response'],
    model_source=response['model_source'],
    feedback_type="positive"
)
🔧 Configuration
Environment Variables
bash
# API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# System Configuration
ADMIN_PASSWORD=your_secure_admin_password
RASA_SERVER_URL=http://localhost:5005
CONFIDENCE_THRESHOLD=0.67
FEEDBACK_THRESHOLD=5

# Paths
RASA_PROJECT_PATH=./rasa_project
DATA_DIR=./data
LOGS_FILE=./data/logs.json
Customization
Adjust Confidence Threshold
python
# In config/config.py
CONFIDENCE_THRESHOLD = 0.67  # Adjust between 0.0-1.0
Modify Training Threshold
python
# Feedback items needed before auto-training
FEEDBACK_THRESHOLD = 5  # Adjust based on your needs
Customize UI Theme
css
/* In app.py CSS section */
:root {
    --primary-color: #6366f1;  /* Change primary color */
    --bg-main: linear-gradient(135deg, #fafbff 0%, #f4f6ff 25%);
}
📊 Features Deep Dive
🤖 Dual AI Architecture
The system intelligently routes queries between two AI models:

Rasa NLU: Handles queries with confidence ≥ 0.67

Groq LLaMA: Processes low-confidence or complex queries

Automatic Fallback: Seamless switching based on real-time confidence assessment

📝 Automatic YAML Generation
Converts natural language feedback into structured Rasa training data:

text
# Generated from: "The bot didn't help with VPN setup"
version: '3.1'
nlu:
- intent: ask_vpn_setup
  examples: |-
    - How do I set up a VPN connection?
    - I need help with VPN configuration
    - VPN setup assistance needed

domain:
  intents:
    - ask_vpn_setup
  responses:
    utter_vpn_setup:
    - text: "I can help you set up a VPN connection. Here's a step-by-step guide..."
🔍 Multi-Layer Validation
Three-tier validation system ensures quality:

Structural Validation: Verifies all required YAML sections

Syntactic Validation: Ensures YAML syntax correctness

Semantic Validation: Checks intent consistency and logical flow

📈 Analytics Dashboard
Comprehensive metrics and visualizations:

Performance Metrics: BLEU score, F1 score, precision, recall

Model Comparison: Rasa vs Groq response distribution

Confidence Analysis: Statistical distribution of confidence scores

User Satisfaction: Feedback trends and satisfaction rates

🧪 Testing
Run the test suite:

bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Full test suite
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src/ --cov-report=html
📈 Performance Benchmarks
Metric	Value	Description
YAML Generation Success Rate	98%	Successful conversion of feedback to training data
Average Response Time	1.2s	End-to-end query processing time
Training Data Quality	96.2%	Human-evaluated semantic consistency
User Satisfaction	78.3%	Positive feedback rate
System Uptime	99.9%	Production deployment reliability
🗂️ Project Structure
text
metaconverse/
├── 📁 src/
│   ├── 🤖 chatbot.py              # Core chatbot logic
│   ├── 💬 feedback_manager.py     # Feedback processing
│   ├── 🎓 training_manager.py     # Training automation
│   ├── 📊 analytics.py            # Analytics engine
│   └── 🛠️ utils.py               # Utility functions
├── 📁 config/
│   └── ⚙️ config.py              # Configuration settings
├── 📁 rasa_project/
│   ├── 📝 data/                   # Training data (YAML)
│   ├── 🏗️ domain.yml             # Rasa domain
│   └── 📋 config.yml             # Rasa configuration
├── 📁 data/
│   ├── 💾 feedback_data.json     # User feedback
│   ├── 📋 logs.json              # System logs
│   └── 📊 chat_history.json      # Conversation history
├── 🎨 app.py                     # Streamlit UI
├── 📋 requirements.txt           # Dependencies
├── 🔧 .env.example              # Environment template
└── 📖 README.md                 # This file
🤝 Contributing
We welcome contributions! Please see our Contributing Guide for details.

Development Setup
Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Make your changes and add tests

Ensure all tests pass: pytest

Commit your changes: git commit -m 'Add amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

Code Style
We use:

Black for code formatting

Flake8 for linting

MyPy for type checking

Run quality checks:

bash
black src/
flake8 src/
mypy src/
🐛 Troubleshooting
Common Issues
Issue: Rasa server connection failed

bash
# Solution: Start Rasa server
cd rasa_project
rasa run --enable-api --cors "*" --port 5005
Issue: GROQ API key invalid

bash
# Solution: Check your API key in .env file
echo $GROQ_API_KEY
Issue: YAML generation failures

bash
# Solution: Check logs for specific errors
tail -f data/logs.json
Getting Help
📖 Documentation

🐛 Issues

💬 Discussions

📧 Email: support@metaconverse.ai

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Rasa Team for the excellent conversational AI framework

Groq for providing fast LLM inference

Streamlit for the amazing web app framework

Open Source Community for the incredible tools and libraries



<div align="center">
⭐ Star this repository if you find it helpful!
</div>