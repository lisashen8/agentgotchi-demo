import os
import urllib.request
import urllib.parse
import streamlit as st
from adk_agent import MODEL_NAME, get_model_display_name, ADK_VERSION


def render_styles():
    """Renders custom CSS styling for dark sci-fi aesthetic."""
    st.markdown("""
    <style>
        .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {
            background-color: #020617 !important;
            color: #f8fafc !important;
            font-family: 'Courier New', Courier, monospace;
        }
        section[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarContent"] {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        .adk-badge {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            color: #818cf8;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
            border: 1px solid #6366f1;
            display: inline-block;
        }
        .status-badge {
            background-color: #064e3b;
            color: #34d399;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
            border: 1px solid #059669;
        }
    </style>
    """, unsafe_allow_html=True)

def generate_pet_svg(mood="HAPPY", frame_idx=0):
    """Generates a rich SVG visualizer for the Quantum Slime Avatar with 60fps CSS animations."""
    configs = {
        "HAPPY": {
            "c1": "#06b6d4", "c2": "#10b981", "glow": "rgba(6,182,212,0.45)",
            "title": "HAPPY & HEALTHY",
            "eyes": '<circle cx="98" cy="86" r="8" fill="#ffffff"/><circle cx="142" cy="86" r="8" fill="#ffffff"/><circle cx="100" cy="84" r="3.5" fill="#020617"/><circle cx="144" cy="84" r="3.5" fill="#020617"/><circle cx="96" cy="83" r="1.5" fill="#fff"/><circle cx="140" cy="83" r="1.5" fill="#fff"/>',
            "mouth": '<path d="M 112 102 Q 120 114 128 102" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/>',
            "particles": "✨ ✨ ✨", "subtitle": "Google ADK State: Nominal"
        },
        "DANCING": {
            "c1": "#ec4899", "c2": "#8b5cf6", "glow": "rgba(236,72,153,0.75)",
            "title": "ADK DANCE TRICK ACTIVE 💃",
            "eyes": '<path d="M 90 84 L 106 90 L 90 96" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/><path d="M 150 84 L 134 90 L 150 96" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/>',
            "mouth": '<ellipse cx="120" cy="106" rx="9" ry="7" fill="#ffffff"/>',
            "particles": "🎵 🎶 💃 ✨ 🕺", "subtitle": "ADK Function Tool Active"
        },
        "ALERT": {
            "c1": "#ef4444", "c2": "#f97316", "glow": "rgba(239,68,68,0.65)",
            "title": "gVisor SECCOMP DEFENSE",
            "eyes": '<circle cx="95" cy="84" r="10" fill="#fff"/><circle cx="145" cy="84" r="10" fill="#fff"/><circle cx="95" cy="84" r="4.5" fill="#ef4444"/><circle cx="145" cy="84" r="4.5" fill="#ef4444"/>',
            "mouth": '<path d="M 108 108 L 132 108" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>',
            "particles": "⚡ 🚨 🔒 🛡️", "subtitle": "Exploit Intercepted by Sandbox"
        },
        "SLEEPING": {
            "c1": "#6366f1", "c2": "#a855f7", "glow": "rgba(99,102,241,0.35)",
            "title": "STANDBY LOW POWER",
            "eyes": '<path d="M 88 88 Q 98 96 108 88" stroke="#ffffff" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M 132 88 Q 142 96 152 88" stroke="#ffffff" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "mouth": '<path d="M 114 105 Q 120 108 126 105" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
            "particles": "💤 z Z Z", "subtitle": "Recharging MicroVM Cells"
        },
        "EATING": {
            "c1": "#f59e0b", "c2": "#84cc16", "glow": "rgba(245,158,11,0.55)",
            "title": "QUANTUM KIBBLE CONSUMPTION",
            "eyes": '<path d="M 90 84 Q 98 74 106 84" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/><path d="M 134 84 Q 142 74 150 84" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/>',
            "mouth": '<ellipse cx="120" cy="106" rx="14" ry="11" fill="#ffffff"/><path d="M 112 106 Q 120 112 128 106" fill="#f43f5e"/>',
            "particles": "🍖 😋 ✨ 🍓", "subtitle": "Energy Restored +25%"
        },
        "THINKING": {
            "c1": "#8b5cf6", "c2": "#ec4899", "glow": "rgba(139,92,246,0.75)",
            "title": "NEURAL THOUGHT & QUANTUM BYTE 🧠",
            "eyes": '<circle cx="98" cy="82" r="8" fill="#ffffff"/><circle cx="142" cy="82" r="8" fill="#ffffff"/><circle cx="102" cy="78" r="3.5" fill="#8b5cf6"/><circle cx="146" cy="78" r="3.5" fill="#8b5cf6"/><circle cx="104" cy="76" r="1.5" fill="#fff"/><circle cx="148" cy="76" r="1.5" fill="#fff"/>',
            "mouth": '<path d="M 114 104 Q 120 100 126 104" stroke="#ffffff" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "particles": "🧠 ⚛️ Quantum Byte ⚡ 💡", "subtitle": "ADK Neural Stream"
        }
    }

    cfg = configs.get(mood, configs["HAPPY"])

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
    body {{
        margin: 0;
        padding: 0;
        background-color: #020617;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
        color: #f8fafc;
        overflow: hidden;
    }}
    .holo-card {{
        background: radial-gradient(circle at 50% 35%, #0f172a 0%, #020617 100%);
        border: 2px solid {cfg['c1']};
        border-radius: 14px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 0 24px {cfg['glow']};
        box-sizing: border-box;
        transition: all 0.5s ease;
    }}

    @keyframes danceBop {{
        0%, 100% {{ transform: translate(130px, 115px) rotate(0deg) scale(1, 1) translate(-130px, -115px); }}
        20% {{ transform: translate(130px, 105px) rotate(-14deg) scale(1.14, 0.86) translate(-130px, -115px); }}
        40% {{ transform: translate(130px, 122px) rotate(0deg) scale(0.86, 1.14) translate(-130px, -115px); }}
        60% {{ transform: translate(130px, 105px) rotate(14deg) scale(1.14, 0.86) translate(-130px, -115px); }}
        80% {{ transform: translate(130px, 118px) rotate(-6deg) scale(0.92, 1.08) translate(-130px, -115px); }}
    }}

    @keyframes eatBounce {{
        0%, 100% {{ transform: translate(130px, 115px) scale(1, 1) translate(-130px, -115px); }}
        50% {{ transform: translate(130px, 108px) scale(1.08, 0.92) translate(-130px, -115px); }}
    }}

    @keyframes sleepBreathe {{
        0%, 100% {{ transform: translate(130px, 115px) scale(1, 0.95) translate(-130px, -115px); }}
        50% {{ transform: translate(130px, 115px) scale(1.04, 1.04) translate(-130px, -115px); }}
    }}

    @keyframes happySway {{
        0%, 100% {{ transform: translate(130px, 115px) rotate(-4deg) translate(-130px, -115px); }}
        50% {{ transform: translate(130px, 115px) rotate(4deg) translate(-130px, -115px); }}
    }}

    @keyframes alertVibrate {{
        0%, 100% {{ transform: translate(130px, 115px) translate(-130px, -115px); }}
        25% {{ transform: translate(134px, 112px) translate(-130px, -115px); }}
        75% {{ transform: translate(126px, 118px) translate(-130px, -115px); }}
    }}

    @keyframes thinkPulse {{
        0%, 100% {{ transform: translate(130px, 115px) scale(1, 1) translate(-130px, -115px); }}
        50% {{ transform: translate(130px, 108px) scale(1.06, 0.94) translate(-130px, -115px); }}
    }}

    .anim-DANCING {{ animation: danceBop 0.6s infinite ease-in-out; transform-origin: 130px 115px; }}
    .anim-EATING {{ animation: eatBounce 0.45s infinite ease-in-out; transform-origin: 130px 115px; }}
    .anim-SLEEPING {{ animation: sleepBreathe 2.5s infinite ease-in-out; transform-origin: 130px 115px; }}
    .anim-HAPPY {{ animation: happySway 2.2s infinite ease-in-out; transform-origin: 130px 115px; }}
    .anim-ALERT {{ animation: alertVibrate 0.15s infinite linear; transform-origin: 130px 115px; }}
    .anim-THINKING {{ animation: thinkPulse 1.2s infinite ease-in-out; transform-origin: 130px 115px; }}
</style>
</head>
<body>
<div id="holo-card" class="holo-card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span id="status-title" style="font-size: 10px; letter-spacing: 1.5px; color: {cfg['c1']}; font-weight: bold; transition: color 0.5s ease;">
            ✦ STATUS: {cfg['title']} ✦
        </span>
        <span id="status-subtitle" style="font-size: 10px; color: #94a3b8; background: #1e293b; padding: 2px 8px; border-radius: 10px;">
            {cfg['subtitle']}
        </span>
    </div>

    <svg width="240" height="150" viewBox="0 0 260 180" style="margin: 0 auto; display: block; filter: drop-shadow(0px 8px 16px {cfg['glow']});">
        <defs>
            <radialGradient id="slimeGrad" cx="40%" cy="30%" r="70%">
                <stop id="grad-stop0" offset="0%" stop-color="{cfg['c2']}" />
                <stop id="grad-stop65" offset="65%" stop-color="{cfg['c1']}" />
                <stop offset="100%" stop-color="#020617" />
            </radialGradient>

            <linearGradient id="pedestalGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="{cfg['c1']}" stop-opacity="0" />
                <stop offset="50%" stop-color="{cfg['c1']}" stop-opacity="0.8" />
                <stop offset="100%" stop-color="{cfg['c1']}" stop-opacity="0" />
            </linearGradient>
        </defs>

        <ellipse cx="130" cy="158" rx="85" ry="14" fill="{cfg['c1']}" opacity="0.12" />
        <ellipse cx="130" cy="158" rx="70" ry="9" fill="none" stroke="{cfg['c1']}" stroke-width="1.5" stroke-dasharray="8,4" />
        <ellipse cx="130" cy="158" rx="45" ry="5" fill="none" stroke="{cfg['c2']}" stroke-width="1" />
        <line x1="130" y1="140" x2="130" y2="158" stroke="{cfg['c1']}" stroke-dasharray="2,2" opacity="0.4"/>

        <circle cx="50" cy="40" r="3" fill="{cfg['c1']}" opacity="0.6"/>
        <circle cx="210" cy="50" r="4" fill="{cfg['c2']}" opacity="0.7"/>
        <circle cx="35" cy="120" r="2" fill="{cfg['c1']}" opacity="0.5"/>
        <circle cx="225" cy="115" r="3" fill="{cfg['c2']}" opacity="0.6"/>

        <g id="slime-body" class="anim-{mood}">
            <path id="slime-path" d="M 65 132
                     C 52 105, 65 60, 130 52
                     C 195 60, 208 105, 195 132
                     C 182 148, 78 148, 65 132 Z"
                  fill="url(#slimeGrad)"
                  stroke="{cfg['c1']}"
                  stroke-width="2.5" />

            <ellipse cx="104" cy="70" rx="20" ry="11" fill="#ffffff" opacity="0.4" transform="rotate(-25 104 70)"/>
            <circle cx="162" cy="66" r="5.5" fill="#ffffff" opacity="0.3" />

            {st.session_state.pet.get('accessory_svg', '')}

            <g id="face-g">
                {cfg['eyes']}
                {cfg['mouth']}
                <circle cx="78" cy="98" r="7.5" fill="#f43f5e" opacity="0.45" />
                <circle cx="162" cy="98" r="7.5" fill="#f43f5e" opacity="0.45" />
            </g>
        </g>

        <g id="thought-bubble" style="display: {'block' if mood == 'THINKING' else 'none'};">
            <circle cx="178" cy="50" r="3" fill="#ec4899" opacity="0.8"/>
            <circle cx="188" cy="38" r="5" fill="#8b5cf6" opacity="0.85"/>
            <g transform="translate(120, 6)">
                <rect x="0" y="0" width="130" height="26" rx="13" fill="#0f172a" stroke="#ec4899" stroke-width="1.8" opacity="0.95" />
                <text x="65" y="17" text-anchor="middle" fill="#38bdf8" font-size="11" font-weight="bold" font-family="monospace">
                    ⚛️ Quantum Byte
                </text>
            </g>
        </g>
    </svg>

    <div id="particles-div" style="margin-top: 2px; font-size: 13px; font-weight: bold; color: #f8fafc; letter-spacing: 1px;">
        {cfg['particles']}
    </div>
</div>
<script>
    if ("{mood}" !== "HAPPY") {{
        setTimeout(function() {{
            var card = document.getElementById("holo-card");
            if (card) {{
                card.style.borderColor = "#06b6d4";
                card.style.boxShadow = "0 0 24px rgba(6,182,212,0.45)";
            }}
            var titleElem = document.getElementById("status-title");
            if (titleElem) {{
                titleElem.innerText = "✦ STATUS: HAPPY & HEALTHY ✦";
                titleElem.style.color = "#06b6d4";
            }}
            var subElem = document.getElementById("status-subtitle");
            if (subElem) subElem.innerText = "Google ADK State: Nominal";

            var stop0 = document.getElementById("grad-stop0");
            var stop65 = document.getElementById("grad-stop65");
            if (stop0) stop0.setAttribute("stop-color", "#10b981");
            if (stop65) stop65.setAttribute("stop-color", "#06b6d4");

            var slimePath = document.getElementById("slime-path");
            if (slimePath) slimePath.setAttribute("stroke", "#06b6d4");

            var slimeElem = document.getElementById("slime-body");
            if (slimeElem) slimeElem.setAttribute("class", "anim-HAPPY");

            var faceElem = document.getElementById("face-g");
            if (faceElem) {{
                faceElem.innerHTML = '<circle cx="98" cy="86" r="8" fill="#ffffff"/><circle cx="142" cy="86" r="8" fill="#ffffff"/><circle cx="100" cy="84" r="3.5" fill="#020617"/><circle cx="144" cy="84" r="3.5" fill="#020617"/><circle cx="96" cy="83" r="1.5" fill="#fff"/><circle cx="140" cy="83" r="1.5" fill="#fff"/><path d="M 112 102 Q 120 114 128 102" stroke="#ffffff" stroke-width="3.5" fill="none" stroke-linecap="round"/><circle cx="78" cy="98" r="7.5" fill="#f43f5e" opacity="0.45" /><circle cx="162" cy="98" r="7.5" fill="#f43f5e" opacity="0.45" />';
            }}

            var bubbleElem = document.getElementById("thought-bubble");
            if (bubbleElem) bubbleElem.style.display = "none";

            var particlesElem = document.getElementById("particles-div");
            if (particlesElem) particlesElem.innerText = "✨ ✨ ✨";
        }}, 3000);
    }}
    setTimeout(function() {{
        var crownElem = document.getElementById("sandbox-crown");
        if (crownElem) {{
            crownElem.style.transition = "opacity 0.8s ease";
            crownElem.style.opacity = "0";
            setTimeout(function() {{ crownElem.style.display = "none"; }}, 800);
        }}
    }}, 4500);
</script>
</body>
</html>"""
    return html

def render_pet_visualizer(container, mood="HAPPY", frame_idx=0):
    """Renders SVG Hologram into the container."""
    with container.container():
        html_code = generate_pet_svg(mood, frame_idx)
        if hasattr(st, "iframe"):
            st.iframe(src="data:text/html;charset=utf-8," + urllib.parse.quote(html_code), height=240)
        else:
            st.html(html_code)

def render_sidebar():
    """Renders System Architecture sidebar metadata."""
    with st.sidebar:
        st.header("⚡ System Architecture")
        st.success("🟢 Agent specs: ACTIVE")
        st.caption("Agent: `AgentgotchiCore`")
        st.caption(f"Model: `{MODEL_NAME}`")
        st.caption(f"Framework: `google-adk` v{ADK_VERSION}")

        st.markdown("---")
        st.header("☁️ Cloud Run Specs")
        
        try:
            req = urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/region", headers={"Metadata-Flavor": "Google"})
            region = urllib.request.urlopen(req, timeout=1).read().decode("utf-8").split("/")[-1]
        except Exception:
            region = "Unknown (Local)"
            
        k_service = os.environ.get("K_SERVICE")
        if k_service:
            deployment_mode = f"Cloud Run Service (`{k_service}`)"
        elif region != "Unknown (Local)":
            deployment_mode = "Cloud Run Instance (Long-lived VM)"
        else:
            deployment_mode = "Local Execution"

        cpu_count = 2
        mem_str = "2 GB"

        st.caption(f"Deployment Type: **{deployment_mode}**")
        st.caption(f"Region: `{region}`")
        st.caption(f"Compute: `{cpu_count} vCPU` | `{mem_str} RAM`")
        if "Instance" in deployment_mode:
            est_cost = round(cpu_count * 5.70, 2)
            st.caption(f"Est. Instance Cost: `~${est_cost:.2f}/mo` ($5.70 per 1 vCPU/1GB)")
        st.caption("Pet Trick Code Execution: `Cloud Run Sandbox (sandbox do)`")

        st.markdown("---")
        st.markdown("### 🏗️ Capabilities")
        st.caption("• **Google ADK**: Autonomous reasoning engine with typed function tools (`feed_pet_tool`, `play_trick_tool`, `rest_pet_tool`, `run_sandbox_python_tool`).")
        st.caption("• **Cloud Run Nested Code Execution Sandbox**: Untrusted Python trick scripts execute safely in isolated ephemeral sandboxes powered by Cloud Run (`sandbox do`).")
        st.caption(f"• **Interactive ADK Chat**: Seamless conversation and automated tool execution powered by {get_model_display_name()}.")
