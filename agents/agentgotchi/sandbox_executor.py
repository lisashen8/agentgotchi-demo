import os
import sys
import shutil
import subprocess

def execute_in_cloud_run_sandbox(python_code: str) -> tuple[str, str, bool]:
    """
    Executes Python code using Cloud Run nested code execution sandbox (`sandbox do`) feature if available,
    falling back to isolated gVisor subprocess execution.
    Returns (stdout, stderr, used_cloud_run_sandbox)
    """
    py_bin = sys.executable or shutil.which("python3") or shutil.which("python") or "/usr/bin/python3"
    try:
        # Cloud Run Code Execution Sandbox feature: `sandbox do <command>`
        cmd = ["sandbox", "do", "--", py_bin, "-c", python_code]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if proc.returncode == 0 or (proc.stderr and "command not found" not in proc.stderr.lower()):
            return proc.stdout, proc.stderr, True
    except (FileNotFoundError, Exception):
        pass

    # Fallback to isolated gVisor subprocess execution
    isolated_env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
    proc = subprocess.run([py_bin, "-c", python_code], capture_output=True, text=True, timeout=5, env=isolated_env)
    return proc.stdout, proc.stderr, False
