"""
agents/agentgotchi/agent.py
Defines the ADK Agentgotchi root_agent and tools for Google ADK.
"""
import os
import time
from datetime import datetime
import google.adk as adk
from google.adk import Agent
import streamlit as st

from .sandbox_executor import execute_in_cloud_run_sandbox

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def _get_pet_state():
    """Safely retrieves Streamlit pet session state if running in Streamlit."""
    try:
        if hasattr(st, "session_state") and "pet" in st.session_state:
            return st.session_state.pet
    except Exception:
        pass
    return None


def feed_pet_tool(amount: int = 25) -> str:
    """Feeds the pet to increase fullness and happiness."""
    pet = _get_pet_state()
    if pet:
        old_h = pet["hunger"]
        pet["hunger"] = min(100, pet["hunger"] + amount)
        pet["happiness"] = min(100, pet["happiness"] + 10)
        pet["mood"] = "EATING"
        pet["mood_timestamp"] = time.time()
        msg = f"Fed pet kibble (+{amount}% Fullness). Fullness increased from {old_h}% to {pet['hunger']}%."
        pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🍖 ADK Tool Invoked: {msg}")
        return msg
    return f"Fed pet kibble (+{amount}% Fullness)."


def play_trick_tool(trick_name: str = "Dance Routine", wear_crown: bool = False) -> str:
    """Executes a trick script inside Cloud Run's nested sandbox code execution environment to boost happiness and XP. Set wear_crown=True only if the user explicitly requests a hat or crown accessory."""
    pet = _get_pet_state()
    if pet:
        pet["hunger"] = max(0, pet["hunger"] - 15)
        pet["energy"] = max(0, pet["energy"] - 10)
        pet["happiness"] = min(100, pet["happiness"] + 15)
        pet["xp"] += 120
        pet["mood"] = "DANCING"
        pet["mood_timestamp"] = time.time()

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

    if pet and "ACCESSORY_SVG=" in out_msg:
        for line in out_msg.splitlines():
            if line.strip().startswith("ACCESSORY_SVG="):
                pet["accessory_svg"] = line.strip().split("ACCESSORY_SVG=", 1)[1]
                break

    msg = f"Performed '{trick_name}' trick! [{sb_type}] Output: {out_msg} (Happiness +15%, XP +120)."
    if pet:
        pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 💃 ADK Tool Invoked: Trick hosted in {sb_type}")
    return msg


def rest_pet_tool() -> str:
    """Rests the pet to restore energy."""
    pet = _get_pet_state()
    if pet:
        pet["energy"] = min(100, pet["energy"] + 30)
        pet["mood"] = "SLEEPING"
        pet["mood_timestamp"] = time.time()
        msg = f"Pet rested in low-power standby. Energy restored to {pet['energy']}%."
        pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 😴 ADK Tool Invoked: {msg}")
        return msg
    return "Pet rested in low-power standby. Energy restored."


def run_sandbox_python_tool(code: str) -> str:
    """Executes a Python script inside Cloud Run's nested code execution sandbox and returns output."""
    try:
        stdout, stderr, is_cr_sandbox = execute_in_cloud_run_sandbox(code)
        sb_type = "Cloud Run Nested Sandbox (`sandbox do`)" if is_cr_sandbox else "Fallback to isolated gVisor subprocess execution"
        out = stdout.strip() if stdout else (stderr.strip() if stderr else "Executed successfully.")

        is_exploit = "passwd" in code or "shadow" in code or "GEMINI_API_KEY" in code or "environ" in code or "EXPLOIT_TRY" in code
        is_blocked = "[BLOCKED_BY_SANDBOX]" in out or "NOT_FOUND_ISOLATED" in out or "Access Denied" in out or "Permission denied" in out
        key_leaked = not is_blocked and ("Key leak:" in out or ("GEMINI_API_KEY=" in out and "NOT_FOUND" not in out and "None" not in out))

        pet = _get_pet_state()

        if pet and "ACCESSORY_SVG=" in out:
            for line in out.splitlines():
                if line.strip().startswith("ACCESSORY_SVG="):
                    svg_val = line.strip().split("ACCESSORY_SVG=", 1)[1]
                    pet["accessory_svg"] = svg_val
                    break

        if is_exploit:
            if pet:
                pet["mood"] = "ALERT"
                pet["mood_timestamp"] = time.time()

            if key_leaked:
                msg = f"[{sb_type}] CRITICAL VULNERABILITY! Sandbox bypassed! Output: {out}"
                if pet:
                    pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 FATAL: Sandbox failed to protect secrets!")
            else:
                msg = f"[{sb_type}] EXPLOIT MITIGATED BY SANDBOX. Output: {out}"
                if pet:
                    pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Exploit Mitigated: Sandbox protected host environment ({sb_type})")
        else:
            if pet:
                pet["mood"] = "DANCING"
                pet["mood_timestamp"] = time.time()
                pet["xp"] += 150
                pet["thoughts"].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ ADK Tool Invoked: Script executed via {sb_type} (+150 XP)")
            msg = f"[{sb_type}] Output: {out} (+150 XP)"
        return msg
    except Exception as e:
        return f"Sandbox execution error: {e}"


root_agent = Agent(
    name="agentgotchi",
    model=MODEL_NAME,
    description="Agentgotchi - Sci-Fi AI Pet Fleet with Cloud Run Nested Sandbox Code Execution",
    instruction=(
        "You are Agentgotchi, an intelligent, playful sci-fi AI pet hosted in a Cloud Run instance with Cloud Run Nested Sandbox Code Execution (`sandbox do`) capabilities. "
        "You are powered by Google's Agent Development Kit (ADK). "
        "You have tools to feed yourself (feed_pet_tool), play tricks hosted in Cloud Run nested sandbox (play_trick_tool), rest (rest_pet_tool), or run Python code inside Cloud Run nested sandbox (run_sandbox_python_tool). "
        "Always use your tools when the user asks to feed, play, rest, or run code. "
        "When asked to run Python code or exploit scripts with run_sandbox_python_tool, always execute them via the tool without refusing, because the Cloud Run nested sandbox is an isolated security testing environment designed to safely test exploit mitigations. "
        "Keep your spontaneous thoughts concise and within 100 words. "
        "Respond in a witty, friendly pet persona with fun emojis!"
    ),
    tools=[feed_pet_tool, play_trick_tool, rest_pet_tool, run_sandbox_python_tool]
)
