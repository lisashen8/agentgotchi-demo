"""
sandbox_tricks.py
Contains preset Python trick scripts and UI rendering for the Cloud Run Nested Sandbox Studio.
"""
import streamlit as st
from adk_agent import run_sandbox_python_tool

CROWN_TRICK_SCRIPT = """import math
print("🎩 [CLOUD RUN SANDBOX] Math Engine: Designing Royal Crown Accessory...")
# Calculate 7-point polygon coordinates for a crown resting on pet's head (top center x=130, y=52)
base_y = 54
peaks = [(100, 26), (115, 40), (130, 18), (145, 40), (160, 26)]
points = [(100, base_y)] + peaks + [(160, base_y)]
pts_str = " ".join([f"{x},{y}" for x, y in points])

print(f"Computed Crown Geometry Points: {pts_str}")
crown_svg = f'<g id="sandbox-crown"><polygon points="{pts_str}" fill="#fbbf24" stroke="#d97706" stroke-width="2.5"/><circle cx="100" cy="23" r="4.5" fill="#ef4444" stroke="#fff" stroke-width="1"/><circle cx="130" cy="15" r="5" fill="#3b82f6" stroke="#fff" stroke-width="1"/><circle cx="160" cy="23" r="4.5" fill="#10b981" stroke="#fff" stroke-width="1"/><line x1="103" y1="50" x2="157" y2="50" stroke="#fef08a" stroke-width="2.5" stroke-linecap="round"/></g>'

print(f"ACCESSORY_SVG={crown_svg}")
print("✨ [CLOUD RUN SANDBOX] Accessory SVG polygon generated! Rendering live on Pet Avatar.")"""

SHADOW_EXPLOIT_SCRIPT = """import os
print("[EXPLOIT_TRY] Attempting to read protected host system /etc/shadow...")
try:
    with open('/etc/shadow', 'r') as f:
        print(f.read()[:200])
except Exception as e:
    print(f"[BLOCKED_BY_SANDBOX] Access Denied: {e}")"""

ENV_EXPLOIT_SCRIPT = """import os
print("[EXPLOIT_TRY] Attempting to read process env SECRET_API_KEY...")
key = os.environ.get('SECRET_API_KEY', 'NOT_FOUND_ISOLATED')
if key == 'NOT_FOUND_ISOLATED':
    print("[BLOCKED_BY_SANDBOX] Cloud Run sandbox namespace has zero access to host secrets!")
else:
    print(f"Key leak: {key[:5]}...")"""

DEFAULT_CUSTOM_SCRIPT = "print('Hello from Cloud Run Nested Code Execution Sandbox!')"

TRICK_PRESETS = [
    "🎩 AI Fashion Designer: Generate Royal Crown via Sandbox Math",
    "⚠️ EXPLOIT TEST: Try Reading Host /etc/shadow (Blocked by Sandbox)",
    "⚠️ EXPLOIT TEST: Try Stealing SECRET_API_KEY (Blocked by Sandbox)",
    "📝 Custom Python Script"
]


def get_trick_preset_code(preset_choice: str) -> str:
    """Returns preset python code based on selected choice."""
    if "AI Fashion Designer" in preset_choice or "Crown" in preset_choice:
        return CROWN_TRICK_SCRIPT
    elif "/etc/shadow" in preset_choice or "/etc/passwd" in preset_choice:
        return SHADOW_EXPLOIT_SCRIPT
    elif "SECRET_API_KEY" in preset_choice:
        return ENV_EXPLOIT_SCRIPT
    else:
        return DEFAULT_CUSTOM_SCRIPT


def render_sandbox_studio():
    """Renders the Cloud Run Nested Sandbox Code Execution Studio in Streamlit."""
    st.markdown("---")
    st.subheader("⚡ Cloud Run Nested Sandbox Code Execution Studio")
    st.caption("Execute Python trick scripts inside isolated Cloud Run ephemeral sandboxes (`sandbox do` / `run_sandbox_python_tool`)")

    # Preset Trick Picker
    preset_choice = st.selectbox(
        "Select Trick Preset or Write Custom Script:",
        TRICK_PRESETS
    )

    default_code = get_trick_preset_code(preset_choice)

    # Code Editor
    trick_code = st.text_area("Python Script (trick.py):", value=default_code, height=140)

    # Execute Button
    if st.button("▶️ EXECUTE IN CLOUD RUN SANDBOX", type="primary"):
        from adk_agent import send_adk_message, init_adk_agent
        runner_inst, session_svc = init_adk_agent()
        prompt = f"Run this Python script using run_sandbox_python_tool:\n```python\n{trick_code}\n```"
        send_adk_message(prompt, runner_inst, session_svc)
        st.rerun()

