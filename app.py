"""
app.py
The main frontend entry point for the application. Uses Streamlit to render the dashboard, manage button clicks, and synchronize the UI with the pet's underlying state.
"""
import time
import streamlit as st

from pet_model import init_pet_state
from adk_agent import init_adk_agent, send_adk_message, get_model_display_name, ensure_adk_session
from ui_components import render_styles, render_pet_visualizer, render_sidebar
from sandbox_tricks import render_sandbox_studio

# Configure Streamlit Page
st.set_page_config(
    page_title="Agentgotchi - Google ADK Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Global Custom CSS
render_styles()

# Initialize Session State
init_pet_state()

# Initialize ADK Agent Runner and Session Service
runner_inst, session_svc = init_adk_agent()
ensure_adk_session(session_svc)


# Header Banner
st.title("🤖 AGENTGOTCHI")
st.markdown(f"""
<div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
    <span class="adk-badge">⚡ Powered by {get_model_display_name()}</span>
    <span class="status-badge">🟢 Cost Effective Long-lived Cloud Run Instance</span>
    <span class="status-badge">🔒 Cloud Run Nested Sandbox (`sandbox do`)</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Render Sidebar Architecture
render_sidebar()

# Main Layout Columns
col_pet, col_studio = st.columns([1, 1.2])

with col_pet:
    st.subheader("🟢 Live Agentgotchi Pet Status")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Level", f"Lv. {st.session_state.pet['level']}")
    m2.metric(
        "Fullness",
        f"{st.session_state.pet['hunger']}%",
        delta=st.session_state.get("hunger_delta", None)
    )
    m3.metric(
        "Happiness",
        f"{st.session_state.pet['happiness']}%",
        delta=st.session_state.get("happiness_delta", None)
    )
    m4.metric(
        "Energy",
        f"{st.session_state.pet['energy']}%",
        delta=st.session_state.get("energy_delta", None)
    )

    # Progress Bars
    st.progress(st.session_state.pet["hunger"] / 100, text=f"🍖 Fullness Level: {st.session_state.pet['hunger']}%")
    st.progress(st.session_state.pet["happiness"] / 100, text=f"💖 Happiness Level: {st.session_state.pet['happiness']}%")
    st.progress(st.session_state.pet["energy"] / 100, text=f"⚡ Energy Level: {st.session_state.pet['energy']}%")

    st.markdown("**Pet Visualizer:**")

    # Auto-reset temporary action moods in session state if older than 3 seconds
    now_time = time.time()
    if st.session_state.pet["mood"] in ["EATING", "DANCING", "ALERT", "THINKING", "SLEEPING"]:
        if now_time - st.session_state.pet.get("mood_timestamp", now_time) > 3.0:
            st.session_state.pet["mood"] = "HAPPY"

    # Auto-reset temporary wearable accessory (hat/crown) after 4.5 seconds
    if st.session_state.pet.get("accessory_svg") and now_time - st.session_state.pet.get("mood_timestamp", now_time) > 4.5:
        st.session_state.pet["accessory_svg"] = ""

    # Pet Display Container
    pet_display = st.empty()
    current_mood = st.session_state.pet["mood"]

    render_pet_visualizer(
        pet_display,
        mood=current_mood,
        frame_idx=st.session_state.anim_state,
        timestamp=st.session_state.pet.get("mood_timestamp", 0)
    )

    # Pet Action Controls
    st.markdown("**Pet Direct Interactions:**")
    b1, b2, b3, b4 = st.columns(4)

    is_waiting = "pending_prompt" in st.session_state

    if b1.button("🍖 Feed Treat", disabled=is_waiting):
        prompt = "Feed the pet with a delicious treat"
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state["pending_prompt"] = prompt
        st.session_state.pet["disable_tools"] = False
        st.session_state.pet["mood"] = "EATING"
        st.session_state.pet["mood_timestamp"] = time.time()
        st.rerun()

    if b2.button("💃 Play Trick", disabled=is_waiting):
        prompt = "Perform a dance trick"
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state["pending_prompt"] = prompt
        st.session_state.pet["disable_tools"] = False
        st.session_state.pet["mood"] = "DANCING"
        st.session_state.pet["mood_timestamp"] = time.time()
        st.rerun()

    if b3.button("😴 Rest", disabled=is_waiting):
        prompt = "Rest and recharge your energy"
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state["pending_prompt"] = prompt
        st.session_state.pet["disable_tools"] = False
        st.session_state.pet["mood"] = "SLEEPING"
        st.session_state.pet["mood_timestamp"] = time.time()
        st.rerun()

    if b4.button("🧠 AI Thought", disabled=is_waiting):
        prompt = "Share a spontaneous thought within 100 words about living inside a Cloud Run nested code execution sandbox. DO NOT invoke any tools."
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state["pending_prompt"] = prompt
        st.session_state.pet["disable_tools"] = True
        st.session_state.pet["energy"] = max(0, st.session_state.pet["energy"] - 10)
        
        # Penalize happiness if energy drops below 50%
        if st.session_state.pet["energy"] < 50:
            st.session_state.pet["happiness"] = max(0, st.session_state.pet["happiness"] - 10)
            
        st.session_state.pet["mood"] = "THINKING"
        st.session_state.pet["mood_timestamp"] = time.time()
        st.rerun()

    # Autonomic Thoughts & Tool Logs Expander
    with st.expander("🛠️ View ADK Debug & Tool Logs", expanded=False):
        st.caption("System telemetry and timestamped audit logs of underlying ADK tool executions:")
        for t in st.session_state.pet["thoughts"][:6]:
            st.caption(f"💭 {t}")

with col_studio:
    st.subheader("💬 Chat with Agentgotchi")
    st.caption("Ask Agentgotchi questions or issue commands. ADK automatically calls tools to update pet state or run trick scripts in the sandbox!")

    # Chat display container
    chat_box = st.container(height=260)
    with chat_box:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant", avatar="🤖").write(msg["content"])

    # Chat Input Box
    user_input = st.chat_input(
        "Ask Agentgotchi or tell it to do something (e.g. 'Feed yourself', 'Play a trick in Cloud Run sandbox')...",
        disabled=is_waiting
    )
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state["pending_prompt"] = user_input
        st.session_state.pet["disable_tools"] = False
        st.rerun()

    if is_waiting:
        prompt_to_process = st.session_state.pop("pending_prompt")
        with chat_box:
            with st.spinner("Agentgotchi is thinking..."):
                send_adk_message(prompt_to_process, runner_inst, session_svc, skip_user_append=True)
        st.session_state.pet["disable_tools"] = False
        st.rerun()

    # Render Sandbox Code Execution Studio
    render_sandbox_studio()

