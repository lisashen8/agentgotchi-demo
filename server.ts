import express from 'express';
import http from 'http';
import { spawn, execSync } from 'child_process';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
const PORT = process.env.PORT || 8080;
const STREAMLIT_PORT = 8501;

console.log('🔍 Checking Python dependencies (streamlit, google-genai, google-adk)...');
try {
  execSync('python3 -c "import streamlit, google.genai, google.adk"', { stdio: 'inherit' });
  console.log('✅ Streamlit, google-genai, and google-adk are ready.');
} catch (e) {
  console.log('📦 Installing Streamlit, google-genai, and google-adk packages...');
  try {
    execSync('python3 -m pip install streamlit google-genai google-adk || (curl -sS https://bootstrap.pypa.io/get-pip.py | python3 && python3 -m pip install streamlit google-genai google-adk)', { stdio: 'inherit' });
  } catch (err) {
    console.error('Failed to auto-install packages:', err);
  }
}

console.log('🚀 Starting Python Streamlit process on port', STREAMLIT_PORT, '...');

// Spawn Streamlit python process
const streamlitProcess = spawn('python3', [
  '-m', 'streamlit', 'run', 'app.py',
  '--server.port', STREAMLIT_PORT.toString(),
  '--server.address', '127.0.0.1',
  '--server.headless', 'true',
  '--server.enableCORS', 'false',
  '--server.enableXsrfProtection', 'false'
], {
  stdio: 'inherit',
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

streamlitProcess.on('error', (err) => {
  console.error('Failed to start Streamlit process:', err);
});

// Configure Proxy Middleware to forward HTTP and WebSocket traffic to Streamlit
const streamlitProxy = createProxyMiddleware({
  target: `http://127.0.0.1:${STREAMLIT_PORT}`,
  ws: true,
  changeOrigin: true
});

app.use('/', streamlitProxy);

function waitForStreamlit(port: number, timeoutMs = 30000): Promise<void> {
  const startTime = Date.now();
  return new Promise((resolve) => {
    const check = () => {
      const req = http.get(`http://127.0.0.1:${port}/_stcore/health`, (res) => {
        if (res.statusCode === 200) {
          console.log(`✅ Streamlit server is up and responding on port ${port}`);
          resolve();
        } else {
          retry();
        }
      });
      req.on('error', () => {
        retry();
      });
      req.end();
    };

    const retry = () => {
      if (Date.now() - startTime > timeoutMs) {
        console.warn('⚠️ Timed out waiting for Streamlit health endpoint; starting Express server anyway.');
        resolve();
      } else {
        setTimeout(check, 300);
      }
    };

    check();
  });
}

waitForStreamlit(STREAMLIT_PORT).then(() => {
  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🤖 Agentgotchi Express proxy server running on http://0.0.0.0:${PORT} -> Streamlit http://127.0.0.1:${STREAMLIT_PORT}`);
  });

  // Handle WebSocket upgrade for Streamlit live re-runs / st.empty() animations
  server.on('upgrade', (req, socket, head) => {
    streamlitProxy.upgrade(req, socket as any, head);
  });
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  streamlitProcess.kill();
  process.exit(0);
});
process.on('SIGINT', () => {
  streamlitProcess.kill();
  process.exit(0);
});
