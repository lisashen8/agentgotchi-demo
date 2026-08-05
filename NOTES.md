# Agentgotchi App Architecture & System Documentation

## 1. Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 USER BROWSER                                      |
+-----------------------------------------------------------------------------------+
                                          |
                                          | HTTP / WebSocket Traffic (Port 3000)
                                          v
+-----------------------------------------------------------------------------------+
|                        EXPRESS PROXY SERVER (server.ts)                           |
|  - Binds to 0.0.0.0:3000                                                          |
|  - Manages background Python Streamlit process                                    |
|  - Forwards HTTP & WebSocket traffic via http-proxy-middleware                    |
+-----------------------------------------------------------------------------------+
                                          |
                                          | Proxy to 127.0.0.1:8501
                                          v
+-----------------------------------------------------------------------------------+
|                      STREAMLIT APP ENGINE (app.py)                                |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | 1. STATE & UI ENGINE (st.session_state)                                     |  |
|  |    - Tracks Hunger, Happiness, Energy, Level, XP, Mood, Log History         |  |
|  |    - Handles layout, action buttons, and dark sci-fi UI styling             |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | 2. GOOGLE AGENT DEVELOPMENT KIT (ADK) ENGINE                                |  |
|  |    - google.adk.Agent & Runner powered by Gemini 2.5 Flash                    |  |
|  |    - Typed Function Tools:                                                  |  |
|  |      * feed_pet_tool                                                        |  |
|  |      * play_trick_tool (Hosted in Cloud Run Nested Sandbox)                 |  |
|  |      * rest_pet_tool                                                        |  |
|  |      * run_sandbox_python_tool                                              |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | 3. CLOUD RUN NESTED SANDBOX CODE EXECUTION (`sandbox do`)                   |  |
|  |    - Executes untrusted trick scripts in isolated ephemeral sandboxes       |  |
|  |    - Zero host credential exposure (gVisor/Sandbox isolation)               |  |
|  |    - Fallback to isolated python subprocess if `sandbox` binary missing     |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | 4. SVG HOLOGRAM ANIMATOR (`generate_pet_svg` & `render_pet_visualizer`)     |  |
|  |    - Generates vector graphics with 60fps CSS keyframe animations            |  |
|  |    - Renders dynamically inside sandboxed Streamlit HTML iframe             |  |
|  |    - Client-side timer auto-reverts mood back to cyan HAPPY state in 3s     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Main Application Logic (`app.py`) Detailed Breakdown

`app.py` is the main file orchestrating the backend logic, AI agent interactions, sandbox code execution, state management, and real-time visual UI.

### Key Sections & Components:

#### A. Cloud Run Code Execution Sandbox Integration (`execute_in_cloud_run_sandbox`)
- **Function**: `execute_in_cloud_run_sandbox(python_code: str)`
- Attempts execution via Cloud Run's nested code execution feature (`sandbox do python3 -c <code>`).
- If the `sandbox` binary launcher is not present in local dev environment, it seamlessly falls back to an isolated Python subprocess with stripped environment variables (`PATH=/usr/bin:/bin`) to ensure zero host secret exposure.

#### B. Session State Engine (`st.session_state`)
- Initializes pet state dictionary containing stats (`hunger`, `happiness`, `energy`, `level`, `xp`, `mood`, `thoughts`).
- Initializes `chat_history` storing conversation logs with the ADK agent.
- Auto-resets temporary action states (`EATING`, `DANCING`, `ALERT`, `THINKING`, `SLEEPING`) back to `HAPPY` after 3 seconds.

#### C. Google Agent Development Kit (ADK) Setup (`google.adk`)
- Configures an autonomous `google.adk.Agent` backed by Gemini 2.5 Flash (`gemini-2.5-flash`).
- Registers typed function tools:
  1. `feed_pet_tool(amount)`: Restores fullness and happiness, updates state to `EATING`.
  2. `play_trick_tool(trick_name)`: Runs trick calculation inside the Cloud Run nested sandbox, boosts happiness & XP, updates state to `DANCING`.
  3. `rest_pet_tool()`: Restores pet energy, updates state to `SLEEPING`.
  4. `run_sandbox_python_tool(code)`: Runs custom Python scripts inside the Cloud Run code execution sandbox, catching and blocking malicious exploit attempts (e.g. attempting to read host secrets).
- `send_adk_message(prompt)`: Asynchronously streams user inputs to the ADK agent via `runner.run_async()` and applies resulting tool updates.

#### D. Vector SVG Hologram Generator (`generate_pet_svg`)
- Produces dynamic vector graphics with fluid 60fps CSS animations (`@keyframes danceBop`, `eatBounce`, `sleepBreathe`, `happySway`, `alertVibrate`, `thinkPulse`).
- Renders customized facial expressions, cheeks, specular highlights, holographic pedestal platform, and floating particle indicators per mood (`HAPPY`, `DANCING`, `ALERT`, `SLEEPING`, `EATING`, `THINKING`).
- **Auto-Revert Mechanism**: Embedded JavaScript sets a timer (3 seconds) that smooth-transitions colors, gradients, facial features, and animations back to the default blue/cyan `HAPPY & HEALTHY` state after an action completes.

#### E. Render Engine (`render_pet_visualizer`)
- Uses `streamlit.components.v1.html` to inject the generated SVG visualizer safely into the Streamlit layout within a sandboxed iframe.

#### F. Streamlit Dashboard Layout & Controls
- **Header Banner**: Displays status badges for Google ADK, Gemini 2.5 Flash Brain, and Cloud Run Nested Sandbox (`sandbox do`).
- **Left Column**: Pet HUD progress bars (Fullness, Happiness, Energy), interactive SVG visualizer, action buttons (Feed Treat, Play Trick, Rest, AI Thought), and autonomic thoughts log.
- **Right Column**: Interactive Chat with Agentgotchi (ADK Engine) and the Cloud Run Nested Sandbox Code Execution Studio with preset scripts and custom Python editor.
