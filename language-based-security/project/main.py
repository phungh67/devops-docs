import multiprocessing
import time
import sys

from llm_guard_daemon import LLGuardDaemon
from llm_guard_client import LLMGuardClient

def run_server():
    """Background daemon to handle prompt and sends to Ollama"""
    server = LLGuardDaemon()
    server.toggle_sandbox_execution(True)
    server.toggle_log(True)
    server.start()

def run_client():
    """Foreground process running the UI"""
    time.sleep(1)
    client = LLMGuardClient()
    client.run()

if __name__ == "__main__":
    daemon_process = multiprocessing.Process(target=run_server, daemon=True)
    daemon_process.start()

    try:
        run_client()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\n[SYSTEM] Terminating LLM Guard Daemon...")
        daemon_process.terminate()
        daemon_process.join()
        sys.exit(0)