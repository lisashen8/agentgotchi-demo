import time
from datetime import datetime
import streamlit as st
from adk_agent import get_model_display_name

def init_pet_state():
    """Initializes session state variables for Pet, animations, and chat history."""
    if "pet" not in st.session_state:
        model_display = get_model_display_name()
        st.session_state.pet = {
            "name": "Quantum Byte",
            "species": "Quantum Slime",
            "level": 5,
            "xp": 350,
            "max_xp": 500,
            "hunger": 50,  # 50% Fullness
            "happiness": 70,
            "energy": 80,
            "mood": "HAPPY",
            "accessory_svg": "",
            "thoughts": [
                f"[{datetime.now().strftime('%H:%M:%S')}] Google ADK Agent Engine active with {model_display}.",
                f"[{datetime.now().strftime('%H:%M:%S')}] Cloud Run Nested Sandbox (`sandbox do`) code execution active."
            ]
        }

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
