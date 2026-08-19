"""
adk_agent.py
The communication bridge between the Streamlit UI and Google's AI Agent engine. Manages agent sessions, streams chat responses, and includes fallback logic.
"""
import os
import time
import asyncio
from datetime import datetime
import streamlit as st

import google.adk as adk
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.agentgotchi.agent import (
    root_agent,
    MODEL_NAME,
    run_sandbox_python_tool,
    feed_pet_tool,
    play_trick_tool,
    rest_pet_tool
)

def get_adk_version() -> str:
    """Returns the installed version of google-adk dynamically."""
    if hasattr(adk, "__version__") and adk.__version__:
        return adk.__version__
    try:
        import importlib.metadata
        return importlib.metadata.version("google-adk")
    except Exception:
        return "unknown"

ADK_VERSION = get_adk_version()

def get_model_display_name(model_id: str = MODEL_NAME) -> str:
    """Converts a model ID into a user-friendly display name (e.g. 'gemini-3.5-flash' -> 'Gemini 3.5 Flash')."""
    clean_id = model_id.split("/")[-1]
    parts = clean_id.replace("_", "-").split("-")
    capitalized = [p.capitalize() if not p.isdigit() else p for p in parts]
    return " ".join(capitalized)

@st.cache_resource
def init_adk_agent():
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service, app_name="agentgotchi_adk_app")
    return runner, session_service

async def run_adk_turn_async(runner, session_id, user_text):
    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=user_text)])
    response_texts = []
    tools_called = []

    async for event in runner.run_async(user_id="user1", session_id=session_id, new_message=user_text if isinstance(user_text, types.Content) else user_msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    tools_called.append(part.function_call.name)
                if part.text:
                    response_texts.append(part.text)

    reply = " ".join(response_texts) if response_texts else "ADK Agent processed request."
    return reply, tools_called

def ensure_adk_session(session_svc):
    """Ensures an ADK session is created with initial state if not already initialized."""
    if "adk_session_id" not in st.session_state:
        session = asyncio.run(session_svc.create_session(
            app_name="agentgotchi_adk_app",
            user_id="user1",
            state=dict(st.session_state.pet)
        ))
        st.session_state.adk_session_id = session.id
        return session
    else:
        session = asyncio.run(session_svc.get_session(
            app_name="agentgotchi_adk_app",
            user_id="user1",
            session_id=st.session_state.adk_session_id
        ))
        if not session:
            session = asyncio.run(session_svc.create_session(
                app_name="agentgotchi_adk_app",
                user_id="user1",
                session_id=st.session_state.adk_session_id,
                state=dict(st.session_state.pet)
            ))
        else:
            for k, v in st.session_state.pet.items():
                session.state[k] = v
        return session

def send_adk_message(prompt: str, runner_inst, session_svc, skip_user_append: bool = False):
    if not prompt.strip():
        return

    if not skip_user_append:
        st.session_state.chat_history.append({"role": "user", "content": prompt})

    try:
        ensure_adk_session(session_svc)

        reply, tools = asyncio.run(run_adk_turn_async(runner_inst, st.session_state.adk_session_id, prompt))
        
        # Read back updated ADK session state into Streamlit session_state for rendering
        session = asyncio.run(session_svc.get_session(
            app_name="agentgotchi_adk_app",
            user_id="user1",
            session_id=st.session_state.adk_session_id
        ))
        if session and session.state:
            for k, v in session.state.items():
                st.session_state.pet[k] = v
            # Refresh timestamp after ADK turn completes so animations display for a full 3 seconds
            st.session_state.pet["mood_timestamp"] = time.time()

        if tools:
            tool_str = ", ".join(tools)
            st.toast(f"🛠️ ADK Agent dispatched tool(s): {tool_str}")

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 ADK Agent: {reply}")
    except Exception as ex:
        pet = st.session_state.pet
        p_lower = prompt.lower()
        if "feed" in p_lower or "eat" in p_lower or "treat" in p_lower:
            pet["hunger"] = min(100, pet["hunger"] + 25)
            pet["mood"] = "EATING"
            pet["mood_timestamp"] = __import__("time").time()
            reply = "Yum! Ate quantum kibble (+25% Fullness)."
        elif "dance" in p_lower or "play" in p_lower or "trick" in p_lower:
            pet["happiness"] = min(100, pet["happiness"] + 15)
            pet["energy"] = max(0, pet["energy"] - 10)
            pet["hunger"] = max(0, pet["hunger"] - 15)
            if pet["energy"] < 50:
                pet["happiness"] = max(0, pet["happiness"] - 10)
            pet["mood"] = "DANCING"
            pet["mood_timestamp"] = __import__("time").time()
            reply = "Wheee! Danced for you in matrix (+15% Happiness, -10 Energy)."
        elif "rest" in p_lower or "sleep" in p_lower:
            pet["energy"] = min(100, pet["energy"] + 30)
            pet["mood"] = "SLEEPING"
            pet["mood_timestamp"] = __import__("time").time()
            reply = "Zzz... Recharging MicroVM energy cells."
        elif "thought" in p_lower:
            pet["energy"] = max(0, pet["energy"] - 10)
            if pet["energy"] < 50:
                pet["happiness"] = max(0, pet["happiness"] - 10)
            pet["mood"] = "THINKING"
            pet["mood_timestamp"] = __import__("time").time()
            reply = "I'm thinking about how cool it is to run in a Cloud Run nested sandbox!"
        else:
            reply = f"Beep boop! I am {pet['name']}, powered by Google Agent Development Kit (ADK)!"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 ADK Agent: {reply}")


