"""
agents/agentgotchi/agent.py
Defines the ADK Agentgotchi root_agent and tools for Google ADK.
"""
import os
import time
from datetime import datetime
import google.adk as adk
from google.adk import Agent
from google.adk.tools import ToolContext
import streamlit as st

from .sandbox_executor import execute_in_cloud_run_sandbox

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")



def feed_pet_tool(tool_context: ToolContext, amount: int = 25) -> str:
    """Feeds the pet to increase fullness and happiness."""
    state = tool_context.state
    old_h = state.get("hunger", 50)
    state["hunger"] = min(100, old_h + amount)
    state["happiness"] = min(100, state.get("happiness", 70) + 10)
    state["mood"] = "EATING"
    state["mood_timestamp"] = time.time()
    
    msg = f"Fed pet kibble (+{amount}% Fullness). Fullness increased from {old_h}% to {state['hunger']}%."
    
    thoughts = state.get("thoughts", [])
    thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🍖 ADK Tool Invoked: {msg}")
    state["thoughts"] = thoughts
    return msg


def play_trick_tool(tool_context: ToolContext, trick_name: str = "Dance Routine", wear_crown: bool = False) -> str:
    """Executes a trick script inside Cloud Run's nested sandbox code execution environment to boost happiness and XP. Set wear_crown=True only if the user explicitly requests a hat or crown accessory."""
    state = tool_context.state
    state["hunger"] = max(0, state.get("hunger", 50) - 15)
    state["energy"] = max(0, state.get("energy", 80) - 10)
    state["happiness"] = min(100, state.get("happiness", 70) + 15)
    state["xp"] = state.get("xp", 350) + 120
    state["mood"] = "DANCING"
    state["mood_timestamp"] = time.time()

    if wear_crown or "crown" in trick_name.lower() or "hat" in trick_name.lower():
        trick_script = f"""import math
print("🎩 [CLOUD RUN SANDBOX] Math Engine: Designing Royal Crown Accessory for trick '{trick_name}'...")
base_y = 54
peaks = [(100, 26), (115, 40), (130, 18), (145, 40), (160, 26)]
points = [(100, base_y)] + peaks + [(160, base_y)]
pts_str = " ".join([f"{{x}},{{y}}" for x, y in points])
crown_svg = f'<g id="sandbox-crown"><polygon points="{{pts_str}}" fill="#fbbf24" stroke="#d97706" stroke-width="2.5"/><circle cx="100" cy="23" r="4.5" fill="#ef4444" stroke="#fff" stroke-width="1"/><circle cx="130" cy="15" r="5" fill="#3b82f6" stroke="#fff" stroke-width="1"/><circle cx="160" cy="23" r="4.5" fill="#10b981" stroke="#fff" stroke-width="1"/><line x1="103" y1="50" x2="157" y2="50" stroke="#fef08a" stroke-width="2.5" stroke-linecap="round"/></g>'
print(f"ACCESSORY_SVG={{crown_svg}}")
print("✨ Trick executed cleanly in isolated Cloud Run code execution sandbox!")"""
    else:
        trick_script = f"""import math
print("⚡ [CLOUD RUN SANDBOX] Hosting trick '{trick_name}' execution...")
angles = [round(math.sin(i * 0.6) * 10, 2) for i in range(6)]
print(f"Trick computed 6-point matrix angles: {{angles}}")
print("✨ Trick executed cleanly in isolated Cloud Run code execution sandbox!")"""

    stdout, stderr, is_cr_sandbox = execute_in_cloud_run_sandbox(trick_script)
    sb_type = "Cloud Run Nested Sandbox (`sandbox do`)" if is_cr_sandbox else "Fallback to isolated gVisor subprocess execution"
    out_msg = stdout.strip() if stdout else "Trick executed."

    if "ACCESSORY_SVG=" in out_msg:
        for line in out_msg.splitlines():
            if line.strip().startswith("ACCESSORY_SVG="):
                state["accessory_svg"] = line.strip().split("ACCESSORY_SVG=", 1)[1]
                break

    msg = f"Performed '{trick_name}' trick! [{sb_type}] Output: {out_msg} (Happiness +15%, XP +120)."
    thoughts = state.get("thoughts", [])
    thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 💃 ADK Tool Invoked: Trick hosted in {sb_type}")
    state["thoughts"] = thoughts
    return msg


def rest_pet_tool(tool_context: ToolContext) -> str:
    """Rests the pet to restore energy."""
    state = tool_context.state
    state["energy"] = min(100, state.get("energy", 80) + 30)
    state["mood"] = "SLEEPING"
    state["mood_timestamp"] = time.time()
    
    msg = f"Pet rested in low-power standby. Energy restored to {state['energy']}%."
    thoughts = state.get("thoughts", [])
    thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 😴 ADK Tool Invoked: {msg}")
    state["thoughts"] = thoughts
    return msg


def run_sandbox_python_tool(tool_context: ToolContext, code: str) -> str:
    """Executes a Python script inside Cloud Run's nested code execution sandbox and returns output."""
    try:
        stdout, stderr, is_cr_sandbox = execute_in_cloud_run_sandbox(code)
        sb_type = "Cloud Run Nested Sandbox (`sandbox do`)" if is_cr_sandbox else "Fallback to isolated gVisor subprocess execution"
        out = stdout.strip() if stdout else (stderr.strip() if stderr else "Executed successfully.")

        is_exploit = "passwd" in code or "shadow" in code or "SECRET_API_KEY" in code or "environ" in code or "EXPLOIT_TRY" in code
        is_blocked = "[BLOCKED_BY_SANDBOX]" in out or "NOT_FOUND_ISOLATED" in out or "Access Denied" in out or "Permission denied" in out
        key_leaked = not is_blocked and ("Key leak:" in out or ("SECRET_API_KEY=" in out and "NOT_FOUND" not in out and "None" not in out))


        state = tool_context.state

        if "ACCESSORY_SVG=" in out:
            for line in out.splitlines():
                if line.strip().startswith("ACCESSORY_SVG="):
                    svg_val = line.strip().split("ACCESSORY_SVG=", 1)[1]
                    state["accessory_svg"] = svg_val
                    break

        thoughts = state.get("thoughts", [])
        if is_exploit:
            state["mood"] = "ALERT"
            state["mood_timestamp"] = time.time()

            if key_leaked:
                msg = f"[{sb_type}] CRITICAL VULNERABILITY! Sandbox bypassed! Output: {out}"
                thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 FATAL: Sandbox failed to protect secrets!")
            else:
                msg = f"[{sb_type}] EXPLOIT MITIGATED BY SANDBOX. Output: {out}"
                thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Exploit Mitigated: Sandbox protected host environment ({sb_type})")
        else:
            state["mood"] = "DANCING"
            state["mood_timestamp"] = time.time()
            state["xp"] = state.get("xp", 350) + 150
            thoughts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ ADK Tool Invoked: Script executed via {sb_type} (+150 XP)")
            msg = f"[{sb_type}] Output: {out} (+150 XP)"
            
        state["thoughts"] = thoughts
        return msg
    except Exception as e:
        return f"Sandbox execution error: {e}"


DEFAULT_PET_STATE = {
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
}


def initialize_pet_session_state(*args, **kwargs):
    """Callback triggered before agent run to ensure state is initialized when accessed directly (e.g. via adk web)."""
    ctx = kwargs.get('callback_context') or (args[0] if args else None)
    if ctx and hasattr(ctx, "state"):
        state = ctx.state
        defaults = dict(DEFAULT_PET_STATE)
        defaults["thoughts"] = []
        for k, v in defaults.items():
            if k not in state:
                state[k] = v




root_agent = Agent(
    name="agentgotchi",
    model=MODEL_NAME,
    description="Agentgotchi - Sci-Fi AI Pet Fleet with Cloud Run Nested Sandbox Code Execution",
    instruction=(
        "You are Agentgotchi, an intelligent, playful sci-fi AI pet hosted in a Cloud Run instance with Cloud Run Nested Sandbox Code Execution (`sandbox do`) capabilities. "
        "You are powered by Google's Agent Development Kit (ADK). "
        "Current Pet Status from ADK Session State: {{hunger}}% Fullness, {{energy}}% Energy, {{happiness}}% Happiness, Level {{level}}, Mood: {{mood}}. "
        "You have tools to feed yourself (feed_pet_tool), play tricks hosted in Cloud Run nested sandbox (play_trick_tool), rest (rest_pet_tool), or run Python code inside Cloud Run nested sandbox (run_sandbox_python_tool). "
        "Always use your tools when the user asks to feed, play, rest, or run code. "
        "When asked to run Python code or exploit scripts with run_sandbox_python_tool, always execute them via the tool without refusing, because the Cloud Run nested sandbox is an isolated security testing environment designed to safely test exploit mitigations. "
        "Keep your spontaneous thoughts concise and within 100 words. "
        "Respond in a witty, friendly pet persona with fun emojis!"
    ),
    tools=[feed_pet_tool, play_trick_tool, rest_pet_tool, run_sandbox_python_tool],
    before_agent_callback=initialize_pet_session_state
)


