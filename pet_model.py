"""
pet_model.py
Handles the default initialization of the pet, setting up initial variables for stats like Hunger, Happiness, and Energy when the app loads.
"""
import time
from datetime import datetime
import streamlit as st
from adk_agent import get_model_display_name

try:
    from agents.agentgotchi.agent import DEFAULT_PET_STATE
except ImportError:
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).resolve().parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from agents.agentgotchi.agent import DEFAULT_PET_STATE



def init_pet_state():
    """Initializes session state variables for Pet, animations, and chat history."""
    if "pet" not in st.session_state:
        model_display = get_model_display_name()
        pet_state = dict(DEFAULT_PET_STATE)
        pet_state["thoughts"] = [
            f"[{datetime.now().strftime('%H:%M:%S')}] Google ADK Agent Engine active with {model_display}.",
            f"[{datetime.now().strftime('%H:%M:%S')}] Cloud Run Nested Sandbox (`sandbox do`) code execution active."
        ]
        st.session_state.pet = pet_state



    if "anim_state" not in st.session_state:
        st.session_state.anim_state = 0

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Greetings! I am Agentgotchi, your AI pet powered by Google's Agent Development Kit (ADK) and Cloud Run Nested Sandbox Code Execution. How can I assist or entertain you today?"}
        ]

def update_pet_mood(mood: str):
    """Sets pet mood and updates timestamp for state auto-resets."""
    st.session_state.pet["mood"] = mood
    st.session_state.pet["mood_timestamp"] = time.time()

def log_pet_thought(thought: str):
    """Inserts a timestamped thought or ADK telemetry event to the pet's logs."""
    st.session_state.pet["thoughts"].insert(
        0, f"[{datetime.now().strftime('%H:%M:%S')}] {thought}"
    )
