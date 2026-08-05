<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Agentgotchi

## What is this app?
**Agentgotchi** is an AI-powered virtual companion that lives in Google Cloud Run! Powered by the **Google Agent Development Kit (ADK)** and **Gemini 3.5 Flash**, Agentgotchi features an autonomous brain that tracks its internal state (Hunger, Happiness, Energy), reasons over its environment, and interacts with you via natural language chat and responsive action buttons.

It can eat quantum treats, rest in standby mode, share spontaneous concise thoughts, and execute untrusted Python "trick scripts" securely inside **Cloud Run Nested Sandboxes (`sandbox do`)**. The sandbox can even dynamically calculate polygon math to design custom wearable SVG accessories (such as a royal crown) that render live on the pet's hologram!

---

## High-Level Application Architecture
The application seamlessly combines a Node.js web server with a Python-based AI and UI orchestration layer:

1. **Express Proxy Server (`server.ts` - Node.js):** Binds to port `8080` for Cloud Run ingress and proxies traffic to Python Streamlit. It includes a `waitForStreamlit` health-check poller (`http://127.0.0.1:8501/_stcore/health`) that prevents container startup 500 errors by ensuring Express only opens traffic after Streamlit is fully warmed up.
2. **Streamlit UI Engine (`app.py` - Python):** Manages the dark-mode UI layout (`.streamlit/config.toml`), tracks pet state variables, renders the dynamic vector SVG holograms, and includes collapsible telemetry logs (`🛠️ View ADK Debug & Tool Logs`).
3. **Google ADK & Gemini 3.5 Flash:** Equipped with typed function tools (`feed_pet_tool`, `play_trick_tool`, `rest_pet_tool`, and `run_sandbox_python_tool`) that autonomously manipulate the pet's state and converse in real time.
4. **Cloud Run Nested Code Execution Sandbox (`sandbox do`):** Leverages Cloud Run's gVisor sandbox feature to execute untrusted Python scripts in ephemeral microVMs without exposing host credentials or environment variables.
5. **Real-Time Deployment & Cost Detection:** Dynamically detects whether the application is running as a **Cloud Run Service** or a **Cloud Run Instance** by checking `K_SERVICE`, displaying real-time compute specs (`2 vCPU | 2 GB RAM`) and estimating monthly VM costs (`~$11.40/mo`).

---

## Key Features
- **🎩 AI Fashion Designer (Sandbox Crown Generator):** Untrusted Python math scripts calculate 7-point polygon coordinates dynamically in `sandbox do` and render royal crown SVG accessories on the pet's head, complete with an automatic 4.5-second JavaScript fade-out and state reset.
- **🛡️ Sandbox Security Proof-of-Concept:** Built-in exploit testing presets demonstrate gVisor isolation in real time by blocking attempts to read `/etc/shadow` or steal `GEMINI_API_KEY` from `/proc`.
- **💬 Interactive ADK Chat:** Converse bidirectionally with your pet using Gemini 3.5 Flash; the agent automatically invokes tools in response to conversational requests.
- **☁️ Live Cloud Run Telemetry:** Inspect deployment type, region, compute resources, and estimated instance pricing directly from the sidebar.

---

## Run Locally

**Prerequisites:** Node.js 20+, Python 3.10+

1. Install dependencies:
   ```bash
   npm install
   ```
2. Set your Gemini API Key. Create a `.env` file in the root directory and add:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Run the app locally:
   ```bash
   npm run dev
   ```

---

## Deploy to Google Cloud Run

To deploy Agentgotchi to Cloud Run and enable the public preview Code Execution Sandbox feature:

### 1. Prerequisites
- Ensure you have the Google Cloud CLI (`gcloud`) installed and authenticated to your project.
- Verify your `Dockerfile` installs both Node.js and Python 3.
- Ensure your `.dockerignore` file excludes local `node_modules`.

### 2. Deploy as a Cloud Run Service
Deploy the application from source using `gcloud beta` to access preview features, explicitly clearing base images and setting `--sandbox-launcher`:

```bash
gcloud beta run deploy agentgotchi-cloudrun \
  --source . \
  --region us-west1 \
  --project YOUR_PROJECT_ID \
  --allow-unauthenticated \
  --clear-base-image \
  --set-env-vars GEMINI_API_KEY="your_gemini_api_key_here" \
  --sandbox-launcher
```
*(Note: The `--sandbox-launcher` flag mounts the `sandbox` binary inside your Cloud Run container at runtime, enabling untrusted Python code execution in isolated gVisor sandboxes via `sandbox do`.)*

### 3. Alternative: Deploy as a Cloud Run Instance (Private Preview)
If you have access to Cloud Run Instances, you can deploy Agentgotchi as a long-lived VM Instance instead of an autoscaled Service:

1. **Create the Instance:** Explicitly specify `--port=8080` (Cloud Run Instances do not automatically inject `$PORT`):
   ```bash
   gcloud alpha run instances create agentgotchi-instance \
     --image="YOUR_IMAGE_URL_HERE" \
     --region us-west1 \
     --port=8080 \
     --set-env-vars GEMINI_API_KEY="your_gemini_api_key_here" \
     --sandbox-launcher
   ```
2. **Allow Unauthenticated Access:**
   ```bash
   gcloud alpha run instances update agentgotchi-instance \
     --region us-west1 \
     --no-invoker-iam-check
   ```