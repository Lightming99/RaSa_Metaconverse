import streamlit as st

st.set_page_config(
    page_title="MetaConverse - IT Support Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid
import time
import logging
from pathlib import Path
import numpy as np
from collections import defaultdict
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules with comprehensive error handling
try:
    from config.config import Config
    from src.chatbot import ChatBot
    from src.feedback_manager import FeedbackManager
    from src.training_manager import TrainingManager
    from src.analytics import Analytics
    from src.utils import initialize_data_files, log_activity, safe_load_json, safe_save_json
except ImportError as e:
    st.error(f"🚨 Module Import Error: {e}")
    st.error("Please ensure all required modules are properly installed and available.")
    st.stop()

# Initialize components with error handling
@st.cache_resource
def initialize_components():
    """Initialize all components with caching and error handling"""
    try:
        initialize_data_files()
        chatbot = ChatBot()
        feedback_manager = FeedbackManager()
        training_manager = TrainingManager()
        analytics = Analytics()
        return chatbot, feedback_manager, training_manager, analytics
    except Exception as e:
        st.error(f"🚨 Component Initialization Error: {e}")
        st.stop()

# Initialize components
chatbot, feedback_manager, training_manager, analytics = initialize_components()

# Ultra-Enhanced Modern CSS with Sophisticated Light Design
st.markdown("""
<style>
    /* Import elegant fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Sophisticated Color Variables */
    :root {
        /* Primary Gradients - Elegant Blues & Purples */
        --primary-gradient: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 25%, #a5b4fc 50%, #8b5cf6 100%);
        --secondary-gradient: linear-gradient(135deg, #fef3c7 0%, #fde68a 25%, #f59e0b 75%, #d97706 100%);
        --accent-gradient: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 25%, #6ee7b7 75%, #10b981 100%);
        --subtle-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 25%, #e2e8f0 75%, #cbd5e1 100%);
        
        /* Sophisticated Background Gradients */
        --bg-main: linear-gradient(135deg, #fafbff 0%, #f4f6ff 25%, #eff2ff 75%, #e8edff 100%);
        --bg-card: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
        --bg-glass: rgba(255, 255, 255, 0.85);
        --bg-glass-subtle: rgba(255, 255, 255, 0.65);
        
        /* Elegant Color Palette */
        --primary-color: #6366f1;
        --primary-light: #a5b4fc;
        --primary-dark: #4338ca;
        --secondary-color: #f59e0b;
        --accent-color: #10b981;
        --accent-light: #6ee7b7;
        
        /* Sophisticated Text Colors */
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --text-light: #94a3b8;
        --text-white: #ffffff;
        
        /* Premium Background Colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --bg-tertiary: #f1f5f9;
        --bg-quaternary: #e2e8f0;
        
        /* Elegant Border Colors */
        --border-light: rgba(226, 232, 240, 0.6);
        --border-medium: rgba(203, 213, 225, 0.8);
        --border-accent: rgba(99, 102, 241, 0.2);
        --border-glass: rgba(255, 255, 255, 0.3);
        
        /* Sophisticated Shadows */
        --shadow-subtle: 0 1px 2px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.04);
        --shadow-soft: 0 2px 4px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.06);
        --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 20px rgba(0, 0, 0, 0.08);
        --shadow-large: 0 8px 25px rgba(0, 0, 0, 0.1), 0 4px 10px rgba(0, 0, 0, 0.05);
        --shadow-premium: 0 20px 40px rgba(99, 102, 241, 0.1), 0 8px 16px rgba(0, 0, 0, 0.04);
        
        /* Elegant Spacing */
        --space-xs: 0.5rem;
        --space-sm: 0.75rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        
        /* Border Radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --radius-2xl: 24px;
        --radius-full: 50px;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main App Styling */
    .main {
        background: var(--bg-main);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        padding: 0;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Ultra-Enhanced Header */
    .main-header {
        background: var(--bg-glass);
        backdrop-filter: blur(20px) saturate(1.8);
        border: 1px solid var(--border-glass);
        color: var(--text-primary);
        padding: var(--space-2xl);
        border-radius: var(--radius-2xl);
        text-align: center;
        font-family: 'Poppins', sans-serif;
        font-size: 2.75rem;
        font-weight: 700;
        margin-bottom: var(--space-2xl);
        box-shadow: var(--shadow-premium);
        position: relative;
        overflow: hidden;
        background-clip: padding-box;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.03) 0%, transparent 50%);
        animation: headerGlow 6s ease-in-out infinite alternate;
        pointer-events: none;
    }
    
    @keyframes headerGlow {
        0% { opacity: 0.3; transform: rotate(0deg); }
        100% { opacity: 0.8; transform: rotate(180deg); }
    }
    
    /* Premium Logo Container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 450px;
        margin-bottom: var(--space-2xl);
        background: var(--bg-glass);
        backdrop-filter: blur(25px) saturate(1.8);
        border-radius: var(--radius-2xl);
        box-shadow: var(--shadow-premium);
        border: 1px solid var(--border-glass);
        position: relative;
        overflow: hidden;
    }
    
    .logo-container::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: conic-gradient(from 45deg, transparent, rgba(99, 102, 241, 0.1), transparent);
        animation: logoRotate 20s linear infinite;
        pointer-events: none;
    }
    
    .logo-animation {
        animation: logoFloat 4s ease-in-out infinite;
        font-size: 9rem;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 15px 35px rgba(99, 102, 241, 0.3));
        z-index: 2;
        position: relative;
    }
    
    @keyframes logoFloat {
        0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
        25% { transform: translateY(-15px) rotate(1deg) scale(1.02); }
        50% { transform: translateY(-10px) rotate(0deg) scale(1.05); }
        75% { transform: translateY(-20px) rotate(-1deg) scale(1.02); }
    }
    
    @keyframes logoRotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Ultra-Premium Chat Styling */
    .chat-container {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        margin: var(--space-lg) 0;
        box-shadow: var(--shadow-large);
        border: 1px solid var(--border-light);
        position: relative;
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: var(--primary-gradient);
        color: var(--text-white);
        padding: var(--space-lg) var(--space-xl);
        border-radius: var(--radius-xl) var(--radius-xl) var(--radius-sm) var(--radius-xl);
        margin: var(--space-md) 0;
        margin-left: 15%;
        box-shadow: var(--shadow-medium);
        font-weight: 500;
        line-height: 1.7;
        position: relative;
        animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .bot-message {
        background: var(--bg-glass);
        backdrop-filter: blur(15px) saturate(1.8);
        color: var(--text-primary);
        padding: var(--space-lg) var(--space-xl);
        border-radius: var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-sm);
        margin: var(--space-md) 0;
        margin-right: 15%;
        box-shadow: var(--shadow-medium);
        border: 1px solid var(--border-light);
        font-weight: 500;
        line-height: 1.7;
        position: relative;
        animation: slideInLeft 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes slideInRight {
        from { 
            transform: translateX(60px); 
            opacity: 0; 
            scale: 0.95;
        }
        to { 
            transform: translateX(0); 
            opacity: 1; 
            scale: 1;
        }
    }
    
    @keyframes slideInLeft {
        from { 
            transform: translateX(-60px); 
            opacity: 0; 
            scale: 0.95;
        }
        to { 
            transform: translateX(0); 
            opacity: 1; 
            scale: 1;
        }
    }
    
    /* Premium Confidence Score */
    .confidence-score {
        background: var(--bg-glass-subtle);
        backdrop-filter: blur(12px) saturate(1.5);
        padding: var(--space-sm) var(--space-lg);
        border-radius: var(--radius-full);
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: var(--space-sm) 0;
        display: inline-block;
        box-shadow: var(--shadow-soft);
        border: 1px solid var(--border-light);
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .confidence-score:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }
    
    .confidence-high { 
        border-left: 3px solid var(--accent-color);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03));
    }
    .confidence-medium { 
        border-left: 3px solid var(--secondary-color);
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03));
    }
    .confidence-low { 
        border-left: 3px solid #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.03));
    }
    
    /* Ultra-Premium Metric Cards */
    .metric-card {
        background: var(--bg-glass);
        backdrop-filter: blur(20px) saturate(1.8);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        margin: var(--space-md) 0;
        text-align: center;
        box-shadow: var(--shadow-large);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translate(-50%, -50%);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-premium);
    }
    
    .metric-card:hover::after {
        width: 100%;
        height: 100%;
    }
    
    .metric-value {
        font-size: 3.25rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: var(--space-md) 0;
        line-height: 1.1;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: var(--space-sm);
    }
    
    .metric-icon {
        font-size: 2.75rem;
        margin-bottom: var(--space-md);
        filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.2));
        animation: iconFloat 3s ease-in-out infinite;
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* ULTRA-ENHANCED CHAT INPUT - The Star of the Show */
    .stChatInput {
        background: transparent !important;
        padding: 0 !important;
        margin: var(--space-lg) 0 !important;
    }
    
    .stChatInput > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    
    .stChatInput > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        position: relative;
    }
    
    .stChatInput textarea,
    .stChatInput input[type="text"] {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(25px) saturate(1.8) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-full) !important;
        padding: var(--space-lg) var(--space-xl) !important;
        font-size: 1.1rem !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--shadow-large) !important;
        outline: none !important;
        resize: none !important;
        min-height: 60px !important;
        max-height: 180px !important;
        width: 100% !important;
        margin: 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    .stChatInput textarea:focus,
    .stChatInput input[type="text"]:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 
            var(--shadow-premium),
            0 0 0 4px rgba(99, 102, 241, 0.15) !important;
        transform: translateY(-2px) !important;
        background: var(--bg-primary) !important;
    }
    
    .stChatInput textarea::placeholder,
    .stChatInput input[type="text"]::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.7 !important;
        font-style: italic !important;
    }
    
    /* Add magical glow effect around chat input */
    .stChatInput > div > div::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--primary-gradient);
        border-radius: var(--radius-full);
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .stChatInput > div > div:focus-within::before {
        opacity: 0.3;
        animation: inputGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes inputGlow {
        0% { opacity: 0.2; }
        100% { opacity: 0.4; }
    }
    
    /* Enhanced Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-md) var(--space-lg) !important;
        font-size: 1rem !important;
        background: var(--bg-glass) !important;
        backdrop-filter: blur(15px) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--shadow-soft) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 
            var(--shadow-medium),
            0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.7 !important;
        font-style: italic !important;
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-md) var(--space-xl) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--shadow-medium) !important;
        font-size: 1rem !important;
        text-transform: none !important;
        letter-spacing: 0.025em !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        transition: all 0.3s ease;
        transform: translate(-50%, -50%);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-premium) !important;
        filter: brightness(1.1) saturate(1.2) !important;
    }
    
    .stButton > button:hover::before {
        width: 300%;
        height: 300%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Protected Sections */
    .protected-section {
        background: var(--bg-glass);
        backdrop-filter: blur(20px) saturate(1.5);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        margin: var(--space-xl) 0;
        box-shadow: var(--shadow-large);
        border: 1px solid rgba(245, 158, 11, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .protected-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--secondary-gradient);
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    }
    
    .protected-header {
        color: var(--secondary-color);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: var(--space-lg);
        display: flex;
        align-items: center;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Enhanced Messages */
    .success-message {
        background: var(--accent-gradient);
        color: var(--text-white);
        padding: var(--space-lg);
        border-radius: var(--radius-lg);
        margin: var(--space-md) 0;
        box-shadow: var(--shadow-medium);
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 25%, #f87171 75%, #ef4444 100%);
        color: var(--text-white);
        padding: var(--space-lg);
        border-radius: var(--radius-lg);
        margin: var(--space-md) 0;
        box-shadow: var(--shadow-medium);
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Enhanced Sidebar */
    .sidebar .sidebar-content {
        background: var(--bg-glass);
        backdrop-filter: blur(20px) saturate(1.8);
        border-right: 1px solid var(--border-light);
    }
    
    /* Welcome Message */
    .welcome-message {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin-bottom: var(--space-xl);
        padding: var(--space-xl);
        background: var(--bg-glass);
        backdrop-filter: blur(15px) saturate(1.8);
        border-radius: var(--radius-xl);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-large);
        line-height: 1.8;
    }
    
    .welcome-message h2 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Poppins', sans-serif;
        margin-bottom: var(--space-lg);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-sm) var(--space-md);
        border-radius: var(--radius-full);
        font-size: 0.9rem;
        font-weight: 500;
        margin: var(--space-xs);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .status-indicator:hover {
        transform: translateY(-1px);
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.1);
        color: #065f46;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-active {
        background: rgba(99, 102, 241, 0.1);
        color: #3730a3;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Enhanced Metrics */
    .stMetric {
        background: transparent !important;
    }
    
    .stMetric > div {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-lg) !important;
        box-shadow: var(--shadow-soft) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric > div:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-medium) !important;
    }
    
    /* Enhanced Plotly Charts */
    .js-plotly-plot .plotly .modebar {
        background: var(--bg-glass) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-sm) !important;
        border: 1px solid var(--border-light) !important;
        box-shadow: var(--shadow-soft) !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .user-message, .bot-message {
            margin-left: 5%;
            margin-right: 5%;
        }
        
        .main-header {
            font-size: 2.25rem;
            padding: var(--space-xl);
        }
        
        .logo-animation {
            font-size: 6rem;
        }
        
        .metric-card {
            padding: var(--space-lg);
        }
        
        .stChatInput textarea,
        .stChatInput input[type="text"] {
            font-size: 1rem !important;
            padding: var(--space-md) var(--space-lg) !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.875rem;
        }
        
        .logo-animation {
            font-size: 4.5rem;
        }
        
        .welcome-message {
            font-size: 1rem;
        }
    }
    
    /* Loading Animations */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(99, 102, 241, 0.2);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: var(--radius-sm);
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* Accessibility Enhancements */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High Contrast Mode */
    @media (prefers-contrast: high) {
        :root {
            --border-light: rgba(0, 0, 0, 0.3);
            --border-medium: rgba(0, 0, 0, 0.5);
            --text-muted: #374151;
        }
    }
    
    /* Focus Indicators */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    select:focus-visible {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables with enhanced defaults"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_logo" not in st.session_state:
        st.session_state.show_logo = True
    if "feedback_mode" not in st.session_state:
        st.session_state.feedback_mode = False
    if "current_response_id" not in st.session_state:
        st.session_state.current_response_id = None
    if "page_visits" not in st.session_state:
        st.session_state.page_visits = defaultdict(int)
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()

# Helper functions
def get_confidence_class(confidence):
    """Get CSS class based on confidence score"""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.5:
        return "confidence-medium"
    else:
        return "confidence-low"

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return str(timestamp)

def create_metric_card(title, value, icon, color_class=""):
    """Create beautiful metric card"""
    return f"""
    <div class="metric-card {color_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """

# Enhanced sidebar navigation
def render_sidebar():
    """Render enhanced sidebar navigation"""
    with st.sidebar:
        st.markdown("## 🤖 MetaConverse")
        st.markdown("### AI-Powered IT Support")
        
        # Navigation
        page = st.selectbox(
            "🧭 Navigate:",
            ["💬 Chat", "📊 Analytics", "📁 History", "📋 Logs"],
            format_func=lambda x: x
        )
        
        st.markdown("---")
        
        # Enhanced quick stats
        try:
            chat_history = safe_load_json(Config.CHAT_HISTORY_FILE, [])
            feedback_data = safe_load_json(Config.FEEDBACK_DATA_FILE, [])
            
            total_chats = len(chat_history)
            total_feedback = len(feedback_data)
            
            st.markdown("### 📈 Quick Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💬 Chats", total_chats)
                st.metric("📝 Feedback", total_feedback)
            
            with col2:
                if total_feedback > 0:
                    positive_feedback = sum(1 for f in feedback_data if f.get("feedback_type") == "positive")
                    satisfaction_rate = (positive_feedback / total_feedback) * 100
                    st.metric("😊 Satisfaction", f"{satisfaction_rate:.1f}%")
                
                # Session time
                session_duration = datetime.now() - st.session_state.session_start_time
                hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                st.metric("⏱️ Session", f"{hours:02d}:{minutes:02d}")
            
        except Exception as e:
            st.error(f"Stats error: {str(e)}")
        
        st.markdown("---")
        
        # Enhanced system status
        st.markdown("### 🔧 System Status")
        st.markdown('<div class="status-indicator status-online">✅ System Online</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-indicator status-active">🔄 Auto-training Active</div>', unsafe_allow_html=True)
        
        # Training info
        try:
            processed_count = training_manager._get_processed_reviews_count()
            rejected_count = training_manager.get_rejected_reviews_count()
            
            st.markdown("#### 🎓 Training Status")
            st.write(f"✅ Processed: {processed_count}")
            st.write(f"❌ Rejected: {rejected_count}")
            
        except:
            pass
        
        st.markdown("---")
        st.markdown("*Built with ❤️ using Rasa & Streamlit*")
        
        return page.split(" ", 1)[1]

# Enhanced Chat Page
def render_chat_page():
    """Render enhanced chat interface"""
    st.markdown('<div class="main-header">🤖 MetaConverse AI IT Support</div>', unsafe_allow_html=True)
    
    # Show welcome message and logo
    if st.session_state.show_logo and len(st.session_state.messages) == 0:
        # Logo container
        st.markdown('''
        <div class="logo-container">
            <div class="logo-animation">🤖</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Welcome message
        st.markdown('''
        <div class="welcome-message">
            <h2>👋 Welcome to MetaConverse!</h2>
            <p>Your intelligent AI IT Support Assistant is here to help.</p>
            <p>💡 Ask me anything about IT support, troubleshooting, or technical issues.</p>
            <p>🚀 I learn from every interaction to provide better support.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f'''
                <div class="user-message">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="bot-message">
                    <strong>🤖 MetaConverse:</strong><br>
                    {message["content"]}
                </div>
                ''', unsafe_allow_html=True)
                
                # Enhanced confidence score
                confidence = message.get("confidence", 0)
                model_source = message.get("model_source", "Unknown")
                confidence_class = get_confidence_class(confidence)
                
                st.markdown(f'''
                <div class="confidence-score {confidence_class}">
                    📊 Confidence: {confidence:.2f} | 🔧 Source: {model_source}
                </div>
                ''', unsafe_allow_html=True)
                
                # Enhanced feedback buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    feedback_col1, feedback_col2 = st.columns(2)
                    
                    with feedback_col1:
                        if st.button("👍 Helpful", key=f"thumbs_up_{i}", help="This response was helpful"):
                            process_feedback(message, "positive", i)
                            st.success("Thank you for your feedback! 🙏")
                            st.rerun()
                    
                    with feedback_col2:
                        if st.button("👎 Improve", key=f"thumbs_down_{i}", help="This response needs improvement"):
                            st.session_state.feedback_mode = True
                            st.session_state.current_response_id = i
                            st.rerun()
    
    # Enhanced negative feedback form
    if st.session_state.feedback_mode and st.session_state.current_response_id is not None:
        st.markdown("---")
        st.markdown("### 💬 Help us improve our responses")
        st.markdown("Your detailed feedback helps us provide better IT support.")
        
        with st.form("feedback_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                issue_description = st.text_area(
                    "🔍 What was wrong with the response?",
                    height=120,
                    placeholder="e.g., The solution didn't work, information was incorrect, response was unclear..."
                )
            
            with col2:
                expected_answer = st.text_area(
                    "💡 What would have been a better response?",
                    height=120,
                    placeholder="e.g., I expected information about..., The correct solution should be..."
                )
            
            submitted = st.form_submit_button("📝 Submit Feedback", use_container_width=True)
            
            if submitted:
                if issue_description.strip():
                    current_message = st.session_state.messages[st.session_state.current_response_id]
                    process_feedback(current_message, "negative", st.session_state.current_response_id, 
                                   issue_description, expected_answer)
                    st.session_state.feedback_mode = False
                    st.session_state.current_response_id = None
                    st.success("🙏 Thank you for your detailed feedback! We'll use this to improve our responses.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Please provide a description of the issue.")
    
    # Enhanced user input - THE STAR FEATURE
    st.markdown("---")
    user_input = st.chat_input("✨ Ask your IT support question here... (Type your message and press Enter)")
    
    if user_input:
        st.session_state.show_logo = False
        
        # Add user message
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "id": str(uuid.uuid4())
        }
        st.session_state.messages.append(user_message)
        
        # Get bot response with enhanced error handling
        with st.spinner("🤔 Thinking..."):
            try:
                response_data = chatbot.get_response(user_input)
                
                bot_message = {
                    "role": "bot",
                    "content": response_data["response"],
                    "confidence": response_data["confidence"],
                    "model_source": response_data["model_source"],
                    "query": user_input,
                    "timestamp": datetime.now().isoformat(),
                    "id": str(uuid.uuid4())
                }
                st.session_state.messages.append(bot_message)
                
                # Save to history
                feedback_manager.save_chat_history(user_input, response_data)
                
            except Exception as e:
                error_message = {
                    "role": "bot",
                    "content": f"I apologize, but I encountered an error while processing your request. Please try again, and if the issue persists, please contact support.",
                    "confidence": 0.0,
                    "model_source": "Error Handler",
                    "query": user_input,
                    "timestamp": datetime.now().isoformat(),
                    "id": str(uuid.uuid4())
                }
                st.session_state.messages.append(error_message)
                log_activity("Error", f"Chat error: {str(e)}")
        
        st.rerun()

# Enhanced Analytics Page
def render_analytics_page():
    """Render beautiful analytics dashboard"""
    st.markdown('<div class="main-header">📊 Advanced Analytics Dashboard</div>', unsafe_allow_html=True)
    
    try:
        # Get analytics data
        analytics_data = analytics.get_performance_metrics()
        
        # Enhanced performance metrics with beautiful cards
        st.markdown("### 🎯 AI Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("BLEU Score", analytics_data.get('bleu_score', 0.85), "🎯", "Measures response quality"),
            ("F1 Score", analytics_data.get('f1_score', 0.82), "🎪", "Overall model performance"),
            ("Precision", analytics_data.get('precision', 0.88), "🎲", "Accuracy of predictions"),
            ("Recall", analytics_data.get('recall', 0.84), "🎨", "Coverage of correct answers")
        ]
        
        for i, (label, value, icon, description) in enumerate(metrics):
            with [col1, col2, col3, col4][i]:
                st.markdown(create_metric_card(label, f"{value:.3f}", icon), unsafe_allow_html=True)
                st.caption(description)
        
        st.markdown("---")
        
        # Enhanced model performance comparison
        st.markdown("### 🤖 Model Performance Analysis")
        
        model_data = analytics.get_model_comparison()
        
        if model_data and any(model_data.values()):
            col1, col2 = st.columns(2)
            
            with col1:
                # Beautiful bar chart
                fig_bar = px.bar(
                    x=list(model_data.keys()),
                    y=list(model_data.values()),
                    title="Response Count by AI Model",
                    labels={"x": "AI Model", "y": "Response Count"},
                    color=list(model_data.values()),
                    color_continuous_scale="Viridis",
                    template="plotly_white"
                )
                
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font_size=18,
                    title_font_color='#1e293b',
                    font=dict(family="Inter", size=12),
                    showlegend=False,
                    height=400
                )
                
                fig_bar.update_traces(
                    marker_line_color='rgba(0,0,0,0.1)',
                    marker_line_width=1,
                    texttemplate='%{y}',
                    textposition='outside'
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Beautiful pie chart
                fig_pie = px.pie(
                    values=list(model_data.values()),
                    names=list(model_data.keys()),
                    title="Model Usage Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    template="plotly_white"
                )
                
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font_size=18,
                    title_font_color='#1e293b',
                    font=dict(family="Inter", size=12),
                    height=400
                )
                
                fig_pie.update_traces(
                    textinfo='label+percent',
                    textfont_size=12,
                    marker=dict(line=dict(color='#FFFFFF', width=2))
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("📊 No model performance data available yet. Start chatting to see analytics!")
        
        st.markdown("---")
        
        # Enhanced confidence score distribution
        st.markdown("### 📈 AI Confidence Analysis")
        
        confidence_data = analytics.get_confidence_distribution()
        
        if confidence_data:
            col1, col2 = st.columns(2)
            
            with col1:
                # Beautiful histogram
                fig_hist = px.histogram(
                    x=confidence_data,
                    nbins=25,
                    title="Confidence Score Distribution",
                    labels={"x": "Confidence Score", "y": "Frequency"},
                    color_discrete_sequence=['#6366f1'],
                    template="plotly_white"
                )
                
                fig_hist.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font_size=18,
                    title_font_color='#1e293b',
                    font=dict(family="Inter", size=12),
                    height=400
                )
                
                fig_hist.update_traces(
                    marker_line_color='rgba(0,0,0,0.1)',
                    marker_line_width=1,
                    opacity=0.8
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Confidence statistics
                avg_confidence = np.mean(confidence_data)
                median_confidence = np.median(confidence_data)
                high_confidence_count = sum(1 for c in confidence_data if c >= 0.8)
                total_responses = len(confidence_data)
                
                st.markdown("#### 📊 Confidence Statistics")
                
                stats_metrics = [
                    ("Average Confidence", f"{avg_confidence:.3f}", "📊"),
                    ("Median Confidence", f"{median_confidence:.3f}", "📈"),
                    ("High Confidence Rate", f"{high_confidence_count/total_responses*100:.1f}%", "🎯"),
                    ("Total Responses", str(total_responses), "💬")
                ]
                
                for label, value, icon in stats_metrics:
                    st.markdown(f"""
                    <div style="background: var(--bg-glass); backdrop-filter: blur(15px); padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border: 1px solid var(--border-light); box-shadow: var(--shadow-soft);">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="font-size: 1.2rem;">{icon}</span>
                            <span style="font-weight: 600; color: var(--text-primary);">{label}:</span>
                            <span style="color: var(--primary-color); font-weight: 700;">{value}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📈 No confidence data available yet.")
        
        st.markdown("---")
        
        # Enhanced feedback analysis
        st.markdown("### 💬 User Feedback Analysis")
        
        feedback_analysis = analytics.get_feedback_analysis()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if feedback_analysis['positive'] > 0 or feedback_analysis['negative'] > 0:
                # Beautiful feedback pie chart
                fig_feedback = px.pie(
                    values=[feedback_analysis['positive'], feedback_analysis['negative']],
                    names=['👍 Positive', '👎 Negative'],
                    title="User Feedback Distribution",
                    color_discrete_sequence=['#10b981', '#ef4444'],
                    template="plotly_white"
                )
                
                fig_feedback.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font_size=18,
                    title_font_color='#1e293b',
                    font=dict(family="Inter", size=12),
                    height=400
                )
                
                fig_feedback.update_traces(
                    textinfo='label+percent+value',
                    textfont_size=12,
                    marker=dict(line=dict(color='#FFFFFF', width=3))
                )
                
                st.plotly_chart(fig_feedback, use_container_width=True)
            else:
                st.info("💬 No feedback data available yet.")
        
        with col2:
            # Feedback summary card
            st.markdown("#### 📋 Feedback Summary")
            
            feedback_metrics = [
                ("Total Feedback", feedback_analysis['total'], "📝"),
                ("Positive Feedback", feedback_analysis['positive'], "👍"),
                ("Negative Feedback", feedback_analysis['negative'], "👎"),
                ("Feedback Rate", f"{feedback_analysis['feedback_rate']:.1f}%", "📊")
            ]
            
            for label, value, icon in feedback_metrics:
                st.markdown(f"""
                <div style="background: var(--bg-glass); backdrop-filter: blur(15px); padding: 1.25rem; border-radius: 16px; margin: 0.75rem 0; border: 1px solid var(--border-light); box-shadow: var(--shadow-soft);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <span style="font-weight: 600; color: var(--text-primary); font-size: 1.1rem;">{label}</span>
                        </div>
                        <span style="color: var(--primary-color); font-weight: 800; font-size: 1.3rem;">{value}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # User satisfaction gauge
            if feedback_analysis['total'] > 0:
                satisfaction_rate = (feedback_analysis['positive'] / feedback_analysis['total']) * 100
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = satisfaction_rate,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "User Satisfaction Rate"},
                    delta = {'reference': 80},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#6366f1"},
                        'steps': [
                            {'range': [0, 50], 'color': "#fef2f2"},
                            {'range': [50, 80], 'color': "#fef3c7"},
                            {'range': [80, 100], 'color': "#ecfdf5"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    height=300,
                    font=dict(family="Inter", size=12),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Training insights
        st.markdown("---")
        st.markdown("### 🎓 Training Insights")
        
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            processed_count = training_manager._get_processed_reviews_count()
            rejected_count = training_manager.get_rejected_reviews_count()
            threshold = training_manager.load_feedback_threshold()
            
            training_metrics = [
                ("Processed Reviews", processed_count, "✅"),
                ("Rejected Reviews", rejected_count, "❌"),
                ("Training Threshold", threshold, "🎯"),
                ("Success Rate", f"{(processed_count/(processed_count+rejected_count)*100) if (processed_count+rejected_count) > 0 else 100:.1f}%", "📈")
            ]
            
            for i, (label, value, icon) in enumerate(training_metrics):
                with [col1, col2, col3, col4][i]:
                    st.markdown(create_metric_card(label, str(value), icon), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Training insights error: {str(e)}")
    
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")
        log_activity("Error", f"Analytics error: {str(e)}")

# Enhanced History Page
def render_history_page():
    """Render enhanced chat history page"""
    st.markdown('<div class="main-header">📁 Chat History & Data Management</div>', unsafe_allow_html=True)
    
    try:
        chat_history = safe_load_json(Config.CHAT_HISTORY_FILE, [])
        
        if chat_history:
            # Enhanced statistics
            st.markdown("### 📊 Conversation Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate statistics
            total_conversations = len(chat_history)
            avg_confidence = sum(chat.get("confidence", 0) for chat in chat_history) / len(chat_history)
            rasa_count = sum(1 for chat in chat_history if chat.get("model_source") == "Rasa")
            groq_count = sum(1 for chat in chat_history if chat.get("model_source") == "Groq")
            
            stats = [
                ("Total Chats", total_conversations, "💬"),
                ("Avg Confidence", f"{avg_confidence:.2f}", "📊"),
                ("Rasa Responses", rasa_count, "🤖"),
                ("Groq Responses", groq_count, "🧠")
            ]
            
            for i, (label, value, icon) in enumerate(stats):
                with [col1, col2, col3, col4][i]:
                    st.markdown(create_metric_card(label, str(value), icon), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Enhanced search and filter
            st.markdown("### 🔍 Search & Filter Conversations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_query = st.text_input("🔍 Search conversations:", placeholder="Enter keywords...")
            
            with col2:
                model_filter = st.selectbox("🔧 Filter by model:", ["All Models", "Rasa", "Groq", "Error"])
            
            with col3:
                date_filter = st.selectbox("📅 Filter by date:", ["All Time", "Today", "Last 7 days", "Last 30 days"])
            
            # Apply filters
            filtered_history = chat_history.copy()
            
            # Search filter
            if search_query:
                filtered_history = [
                    chat for chat in filtered_history
                    if search_query.lower() in chat.get("user_query", "").lower() or
                       search_query.lower() in chat.get("bot_response", "").lower()
                ]
            
            # Model filter
            if model_filter != "All Models":
                filtered_history = [
                    chat for chat in filtered_history
                    if chat.get("model_source") == model_filter
                ]
            
            # Date filter
            if date_filter != "All Time":
                now = datetime.now()
                if date_filter == "Today":
                    cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif date_filter == "Last 7 days":
                    cutoff = now - timedelta(days=7)
                elif date_filter == "Last 30 days":
                    cutoff = now - timedelta(days=30)
                
                filtered_history = [
                    chat for chat in filtered_history
                    if datetime.fromisoformat(chat.get("timestamp", "").replace('Z', '+00:00')) >= cutoff
                ]
            
            # Display results
            st.markdown(f"### 💬 Conversations ({len(filtered_history)} found)")
            
            if filtered_history:
                # Pagination
                items_per_page = 10
                total_pages = (len(filtered_history) + items_per_page - 1) // items_per_page
                
                if total_pages > 1:
                    page_number = st.selectbox("📄 Page:", range(1, total_pages + 1))
                    start_idx = (page_number - 1) * items_per_page
                    end_idx = start_idx + items_per_page
                    page_data = filtered_history[start_idx:end_idx]
                else:
                    page_data = filtered_history
                
                # Display conversations with enhanced styling
                for i, chat in enumerate(reversed(page_data)):
                    timestamp = format_timestamp(chat.get("timestamp", "Unknown time"))
                    confidence = chat.get("confidence", 0)
                    confidence_class = get_confidence_class(confidence)
                    model_source = chat.get("model_source", "Unknown")
                    
                    # Model icon
                    model_icon = "🤖" if model_source == "Rasa" else "🧠" if model_source == "Groq" else "⚠️"
                    
                    with st.expander(f"{model_icon} Conversation {len(page_data) - i} - {timestamp}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**👤 User:** {chat.get('user_query', 'N/A')}")
                            st.markdown(f"**🤖 Assistant:** {chat.get('bot_response', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"""
                            <div class="confidence-score {confidence_class}">
                                📊 Confidence: {confidence:.2f}
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <strong>Model:</strong> {model_source}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No conversations match your search criteria.")
            
            st.markdown("---")
            
            # Enhanced download options
            st.markdown("### 📥 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # JSON export
                json_data = json.dumps(filtered_history, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Export as JSON",
                    data=json_data,
                    file_name=f"metaconverse_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # CSV export
                if filtered_history:
                    df = pd.DataFrame(filtered_history)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Export as CSV",
                        data=csv,
                        file_name=f"metaconverse_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                # Analytics report
                analytics_report = generate_analytics_report(filtered_history)
                st.download_button(
                    label="📈 Analytics Report",
                    data=analytics_report,
                    file_name=f"metaconverse_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        else:
            st.markdown('''
            <div class="welcome-message">
                <h3>📭 No Chat History Yet</h3>
                <p>Start a conversation to see your chat history here!</p>
                <p>Your conversations will be automatically saved and displayed in this section.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Protected admin section
        render_protected_section()
    
    except Exception as e:
        st.error(f"History page error: {str(e)}")
        log_activity("Error", f"History error: {str(e)}")

# Enhanced Logs Page
def render_logs_page():
    """Render enhanced system logs page"""
    st.markdown('<div class="main-header">📋 System Logs & Training Management</div>', unsafe_allow_html=True)
    
    try:
        logs = safe_load_json(Config.LOGS_FILE, [])
        
        if logs:
            # Enhanced log statistics
            st.markdown("### 📊 Log Overview")
            
            log_types = defaultdict(int)
            for log in logs:
                log_types[log.get("type", "Unknown")] += 1
            
            col1, col2, col3, col4 = st.columns(4)
            
            stats = [
                ("Total Logs", len(logs), "📋"),
                ("Training Logs", log_types.get("Training", 0), "🎓"),
                ("Error Logs", log_types.get("Error", 0), "⚠️"),
                ("System Logs", log_types.get("System", 0), "⚙️")
            ]
            
            for i, (label, value, icon) in enumerate(stats):
                with [col1, col2, col3, col4][i]:
                    st.markdown(create_metric_card(label, str(value), icon), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Enhanced log filtering
            st.markdown("### 🔍 Filter Logs")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                log_type_filter = st.selectbox("Filter by type:", ["All Types"] + list(log_types.keys()))
            
            with col2:
                max_logs = st.slider("Maximum logs to display:", 10, 200, 50)
            
            with col3:
                search_logs = st.text_input("Search in logs:", placeholder="Enter keywords...")
            
            # Apply filters
            filtered_logs = logs
            
            if log_type_filter != "All Types":
                filtered_logs = [log for log in logs if log.get("type") == log_type_filter]
            
            if search_logs:
                filtered_logs = [
                    log for log in filtered_logs
                    if search_logs.lower() in log.get("message", "").lower()
                ]
            
            # Display logs
            st.markdown(f"### 📝 System Activity ({len(filtered_logs)} logs)")
            
            # Recent logs with enhanced styling
            for log in reversed(filtered_logs[-max_logs:]):
                timestamp = format_timestamp(log.get("timestamp", "Unknown"))
                log_type = log.get("type", "Unknown")
                message = log.get("message", "No message")
                
                # Style based on log type
                if log_type.lower() == "error":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 25%, #f87171 75%, #ef4444 100%); color: white; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: var(--shadow-medium); border: 1px solid rgba(255, 255, 255, 0.2);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">⚠️</span>
                            <strong>{timestamp} [ERROR]</strong>
                        </div>
                        <div style="padding-left: 1.7rem;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif log_type.lower() == "training":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0.05)); border: 1px solid rgba(99, 102, 241, 0.3); padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: var(--shadow-soft);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">🎓</span>
                            <strong style="color: var(--primary-color);">{timestamp} [TRAINING]</strong>
                        </div>
                        <div style="padding-left: 1.7rem; color: var(--text-primary);">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif log_type.lower() == "feedback":
                    st.markdown(f"""
                    <div style="background: var(--accent-gradient); color: white; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: var(--shadow-medium); border: 1px solid rgba(255, 255, 255, 0.2);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">💬</span>
                            <strong>{timestamp} [FEEDBACK]</strong>
                        </div>
                        <div style="padding-left: 1.7rem;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: var(--bg-glass); backdrop-filter: blur(15px); border: 1px solid var(--border-light); padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: var(--shadow-soft);">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">ℹ️</span>
                            <strong style="color: var(--text-primary);">{timestamp} [{log_type.upper()}]</strong>
                        </div>
                        <div style="padding-left: 1.7rem; color: var(--text-secondary);">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.markdown('''
            <div class="welcome-message">
                <h3>📭 No System Logs Yet</h3>
                <p>System logs will appear here as the application runs.</p>
                <p>This includes training activities, errors, and system events.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Enhanced protected section for training management
        render_enhanced_protected_logs_section()
    
    except Exception as e:
        st.error(f"Logs page error: {str(e)}")
        log_activity("Error", f"Logs error: {str(e)}")

# Enhanced protected sections
def render_protected_section():
    """Render enhanced protected admin section"""
    st.markdown("---")
    st.markdown('''
    <div class="protected-section">
        <div class="protected-header">
            <span style="margin-right: 0.5rem;">🔒</span>
            Administrator Controls
        </div>
        <p>Enter the administrator password to access data management functions.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    password = st.text_input("🔑 Administrator Password:", type="password", key="admin_password")
    
    if password == Config.ADMIN_PASSWORD:
        st.success("✅ Access granted! Administrator controls are now available.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Chat History", type="primary", use_container_width=True):
                try:
                    safe_save_json(Config.CHAT_HISTORY_FILE, [])
                    st.success("✅ Chat history cleared successfully!")
                    log_activity("Admin", "Chat history cleared")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error clearing history: {str(e)}")
        
        with col2:
            if st.button("📊 Reset Analytics", type="primary", use_container_width=True):
                try:
                    analytics.reset_metrics()
                    st.success("✅ Analytics reset successfully!")
                    log_activity("Admin", "Analytics reset")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error resetting analytics: {str(e)}")
        
        with col3:
            if st.button("🔄 Reset Session", type="secondary", use_container_width=True):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.success("✅ Session reset successfully!")
                st.rerun()
    
    elif password:
        st.error("❌ Invalid password! Please try again.")

def render_enhanced_protected_logs_section():
    """Enhanced protected logs section with training management"""
    st.markdown("---")
    st.markdown('''
    <div class="protected-section">
        <div class="protected-header">
            <span style="margin-right: 0.5rem;">🔒</span>
            Training Management & System Controls
        </div>
        <p>Administrator access required for training operations and system management.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    password = st.text_input("🔑 Administrator Password:", type="password", key="logs_admin_password")
    
    if password == Config.ADMIN_PASSWORD:
        st.success("✅ Access granted! Training management controls are now available.")
        
        # Training settings
        st.markdown("### ⚙️ Training Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_threshold = training_manager.load_feedback_threshold()
            new_threshold = st.slider(
                "Feedback Threshold for Auto Training:",
                min_value=1,
                max_value=20,
                value=current_threshold,
                help="Number of feedback entries needed to trigger automatic training"
            )
            
            if new_threshold != current_threshold:
                if st.button("Update Threshold", use_container_width=True):
                    training_manager.save_feedback_threshold(new_threshold)
                    st.success(f"✅ Threshold updated to {new_threshold}")
                    st.rerun()
        
        with col2:
            # Display current training status
            try:
                debug_info = training_manager.get_debug_info()
                st.markdown("#### 🔍 Training Status")
                st.write(f"**Processed Reviews:** {debug_info.get('processed_reviews_count', 0)}")
                st.write(f"**Rejected Reviews:** {debug_info.get('rejected_reviews_count', 0)}")
                st.write(f"**Quality Threshold:** {debug_info.get('quality_threshold', 0.8)}")
                st.write(f"**Max Retries:** {debug_info.get('max_retries', 3)}")
            except:
                pass
        
        # Training operations
        st.markdown("### 🔧 Training Operations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Process Reviews", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing reviews..."):
                    try:
                        result = training_manager.process_reviews_manual()
                        if "successfully" in result.lower() or "processed" in result.lower():
                            st.success(f"✅ {result}")
                        else:
                            st.warning(f"⚠️ {result}")
                        log_activity("Admin", "Manual review processing initiated")
                    except Exception as e:
                        st.error(f"❌ Review processing failed: {str(e)}")
                        log_activity("Error", f"Manual review processing failed: {str(e)}")
        
        with col2:
            if st.button("🎓 Manual Training", type="primary", use_container_width=True):
                with st.spinner("🔄 Training model..."):
                    try:
                        result = training_manager.manual_training()
                        if "successfully" in result.lower():
                            st.success(f"✅ {result}")
                        else:
                            st.error(f"❌ {result}")
                        log_activity("Admin", "Manual training initiated")
                    except Exception as e:
                        st.error(f"❌ Training failed: {str(e)}")
                        log_activity("Error", f"Manual training failed: {str(e)}")
        
        with col3:
            if st.button("🗑️ Clear Logs", type="secondary", use_container_width=True):
                try:
                    safe_save_json(Config.LOGS_FILE, [])
                    st.success("✅ Logs cleared successfully!")
                    log_activity("Admin", "Logs cleared")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error clearing logs: {str(e)}")
        
        # Enhanced debug section
        st.markdown("### 🔍 Advanced Diagnostics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Check Feedback Status", use_container_width=True):
                try:
                    unprocessed = feedback_manager.get_unprocessed_feedback()
                    stats = feedback_manager.get_feedback_stats()
                    rejected_count = training_manager.get_rejected_reviews_count()
                    
                    st.markdown("#### 📋 Feedback Status Report")
                    st.write(f"**Unprocessed Feedback:** {len(unprocessed)}")
                    st.write(f"**Total Feedback:** {stats['total']}")
                    st.write(f"**Processed:** {stats['processed']}")
                    st.write(f"**Rejected:** {rejected_count}")
                    st.write(f"**Current Threshold:** {training_manager.load_feedback_threshold()}")
                    
                    # Show retry information
                    if unprocessed:
                        st.markdown("**Retry Status:**")
                        for feedback in unprocessed[:5]:  # Show first 5
                            retry_count = feedback.get("retry_count", 0)
                            st.write(f"  - ID {feedback['id']}: {retry_count}/3 retries")
                    
                except Exception as e:
                    st.error(f"Error checking feedback: {str(e)}")
        
        with col2:
            if st.button("📁 Check System Files", use_container_width=True):
                try:
                    files_to_check = [
                        ("domain.yml", os.path.join(Config.RASA_PROJECT_PATH, "domain.yml")),
                        ("nlu.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "nlu.yml")),
                        ("stories.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "stories.yml")),
                        ("rules.yml", os.path.join(Config.RASA_PROJECT_PATH, "data", "rules.yml"))
                    ]
                    
                    st.markdown("#### 📂 System File Status")
                    for file_name, file_path in files_to_check:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            st.write(f"✅ **{file_name}**: {file_size} bytes")
                        else:
                            st.write(f"❌ **{file_name}**: Missing")
                    
                    # Check data files
                    data_files = [
                        ("Chat History", Config.CHAT_HISTORY_FILE),
                        ("Feedback Data", Config.FEEDBACK_DATA_FILE),
                        ("System Logs", Config.LOGS_FILE),
                        ("Rejected Reviews", training_manager.rejected_reviews_file),
                        ("Processed Reviews", training_manager.processed_reviews_file)
                    ]
                    
                    st.markdown("#### 💾 Data File Status")
                    for file_name, file_path in data_files:
                        if os.path.exists(file_path):
                            try:
                                data = safe_load_json(file_path, [])
                                st.write(f"✅ **{file_name}**: {len(data)} entries")
                            except:
                                st.write(f"⚠️ **{file_name}**: Exists but unreadable")
                        else:
                            st.write(f"❌ **{file_name}**: Missing")
                    
                except Exception as e:
                    st.error(f"Error checking files: {str(e)}")
        
        # Rejected reviews management
        st.markdown("### 🚫 Rejected Reviews Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 View Rejected Reviews", use_container_width=True):
                try:
                    rejected_reviews = safe_load_json(training_manager.rejected_reviews_file, [])
                    if rejected_reviews:
                        st.markdown(f"#### 📋 Rejected Reviews ({len(rejected_reviews)})")
                        for i, review in enumerate(rejected_reviews[-5:]):  # Show last 5
                            st.markdown(f"**Review {i+1}:**")
                            st.write(f"  - **Query:** {review.get('user_query', 'N/A')[:100]}...")
                            st.write(f"  - **Reason:** {review.get('rejection_reason', 'N/A')}")
                            st.write(f"  - **Rejected:** {format_timestamp(review.get('rejection_timestamp', 'N/A'))}")
                            st.markdown("---")
                    else:
                        st.info("No rejected reviews found")
                except Exception as e:
                    st.error(f"Error loading rejected reviews: {str(e)}")
        
        with col2:
            if st.button("🔄 Retry Rejected Reviews", use_container_width=True):
                try:
                    rejected_file = training_manager.rejected_reviews_file
                    if os.path.exists(rejected_file):
                        rejected_reviews = safe_load_json(rejected_file, [])
                        if rejected_reviews:
                            # Reset retry counts and move back to feedback
                            for review in rejected_reviews:
                                review["retry_count"] = 0
                                review.pop("rejection_timestamp", None)
                                review.pop("rejection_reason", None)
                            
                            # Add to feedback file
                            feedback_data = safe_load_json(Config.FEEDBACK_DATA_FILE, [])
                            feedback_data.extend(rejected_reviews)
                            safe_save_json(Config.FEEDBACK_DATA_FILE, feedback_data)
                            
                            # Clear rejected file
                            safe_save_json(rejected_file, [])
                            
                            st.success(f"✅ Moved {len(rejected_reviews)} reviews back for reprocessing")
                            log_activity("Admin", f"Retried {len(rejected_reviews)} rejected reviews")
                        else:
                            st.info("No rejected reviews to retry")
                    else:
                        st.info("No rejected reviews file found")
                except Exception as e:
                    st.error(f"Error retrying rejected reviews: {str(e)}")
    
    elif password:
        st.error("❌ Invalid password! Please try again.")

# Helper functions
def process_feedback(message, feedback_type, message_index, issue_description=None, expected_answer=None):
    """Process user feedback with enhanced error handling"""
    try:
        feedback_manager.process_feedback(
            message_index,
            message.get("query", ""),
            message.get("content", ""),
            message.get("model_source", ""),
            feedback_type,
            issue_description,
            expected_answer
        )
        
        log_activity("Feedback", f"User provided {feedback_type} feedback for {message.get('model_source', 'Unknown')} response")
        
    except Exception as e:
        st.error(f"Error processing feedback: {str(e)}")
        log_activity("Error", f"Feedback processing error: {str(e)}")

def generate_analytics_report(chat_data):
    """Generate analytics report for download"""
    try:
        report = f"""MetaConverse Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

OVERVIEW
--------
Total Conversations: {len(chat_data)}
Date Range: {min(chat.get('timestamp', '') for chat in chat_data) if chat_data else 'N/A'} to {max(chat.get('timestamp', '') for chat in chat_data) if chat_data else 'N/A'}

CONFIDENCE ANALYSIS
------------------
Average Confidence: {sum(chat.get('confidence', 0) for chat in chat_data) / len(chat_data):.3f if chat_data else 0}
High Confidence (>0.8): {sum(1 for chat in chat_data if chat.get('confidence', 0) > 0.8)}
Medium Confidence (0.5-0.8): {sum(1 for chat in chat_data if 0.5 <= chat.get('confidence', 0) <= 0.8)}
Low Confidence (<0.5): {sum(1 for chat in chat_data if chat.get('confidence', 0) < 0.5)}

MODEL USAGE
-----------
Rasa Responses: {sum(1 for chat in chat_data if chat.get('model_source') == 'Rasa')}
Groq Responses: {sum(1 for chat in chat_data if chat.get('model_source') == 'Groq')}
Error Responses: {sum(1 for chat in chat_data if chat.get('model_source') == 'Error')}

PERFORMANCE METRICS
------------------
Response Time Analysis: Available in chat logs
User Satisfaction: Calculated from feedback data
System Uptime: Monitor through system logs

RECOMMENDATIONS
--------------
- Monitor confidence scores for quality assurance
- Review low confidence responses for improvement
- Analyze user feedback patterns for training optimization
- Regular model retraining based on feedback threshold

GENERATED BY METACONVERSE ANALYTICS SYSTEM
Contact: support@metaconverse.ai
Report Version: 1.0
"""
        return report
        
    except Exception as e:
        return f"Error generating analytics report: {str(e)}\nPlease contact support if this issue persists."

# Main application
def main():
    """Enhanced main application with comprehensive error handling"""
    try:
        # Initialize session state
        init_session_state()
        
        # Render sidebar and get selected page
        page = render_sidebar()
        
        # Track page visits
        st.session_state.page_visits[page] += 1
        
        # Render selected page with error handling
        try:
            if page == "Chat":
                render_chat_page()
            elif page == "Analytics":
                render_analytics_page()
            elif page == "History":
                render_history_page()
            elif page == "Logs":
                render_logs_page()
        
        except Exception as e:
            st.error(f"Page rendering error: {str(e)}")
            log_activity("Error", f"Page {page} rendering error: {str(e)}")
            st.info("Please try refreshing the page or contact support if the issue persists.")
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error("Please refresh the page or contact support if the error persists.")
        log_activity("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
