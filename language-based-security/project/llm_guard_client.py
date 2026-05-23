import socket
import json
import readline

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

SOCKET_PATH = "/tmp/llm_guard_client.sock"

class LLMGuardClient():
    """The interactive, frontend CLI for LLM Guard"""
    def __init__(self):
        self.console = Console()

    def send_to_daemon(self, raw_input: str) -> dict:
        """Taking raw input from user and sends it to backend daemon"""
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(SOCKET_PATH)
            client.sendall(raw_input.encode('utf-8'))

            # wait for response
            response = client.recv(65536).decode('utf-8')
            return json.loads(response)
        except FileNotFoundError:
            return {"status": "ERROR", "reason": "Daemon socket not found. Is the server running?"}
        except Exception as e:
            return {"status": "ERROR", "reason": f"Socket error: {str(e)}"}
        finally:
            client.close()

    def show_menu(self):
        """Anchor method to start and for better navigation purpose for this client.
        """
        self.console.print("\n[bold cyan]--- System Configuration ---[/bold cyan]")
        
        sandbox_state = Confirm.ask("Enable Sandbox Execution (Agentic Mode)?", default=True)
        embed_state = Confirm.ask("Enable Dense Embedding Defense (Deep Semantic - embedding vectorized for future guarding)?", default=False)

        config_payload = f"/config sandbox={sandbox_state} embed={embed_state}"

        with self.console.status("[bold cyan]Applying configuration...", spinner="dots"):
            result = self.send_to_daemon(config_payload)

        if result.get("status") == "SYSTEM":
            self.console.print("[bold green]✔ Configuration successfully synchronized with Daemon.[/bold green]\n")
        else:
            self.console.print("[bold red]✖ Failed to synchronize configuration.[/bold red]\n")

    def run(self):
        # self.console.clear()
        welcome_text = (
            "[bold green] LLM Guard - Security Proxy Terminal for LLM Model [/bold green]\n"
            "Type [bold cyan]/exit[/bold cyan] to quit.\n"
            "Type [bold cyan]/menu[/bold cyan] to configure system settings.\n"
            "To submit a multi-line prompt, type [bold cyan]/send[/bold cyan] on a new line when finished.\n"
            "\n[bold yellow]Agentic Execution Commands:[/bold yellow]\n"
            "  [bold cyan]/execute <prompt>[/bold cyan] - Run a new command in the sandbox.\n"
            "  [bold cyan]/execute[/bold cyan]          - Run the last generated plan in the sandbox.\n"
            "  [bold cyan]/commit[/bold cyan]           - Apply the pending sandbox changes to your real system.\n"
            "  [bold cyan]/discard[/bold cyan]          - Discard the pending sandbox changes.\n"
        )
        self.console.print(Panel.fit(welcome_text, title="System Ready", border_style="green"))

        while True:
            try:
                self.console.print("\n[bold yellow]LLM-Guard >>> [\bold yellow]", end="")

                user_lines = []
                while True:
                    line = input()
                    if line.strip().lower() == '/exit':
                        self.console.print("\n[bold red]Shutting down client...[/bold red]")
                        return
                    if line.strip().lower() == '/main':
                        self.show_menu()
                        user_lines = []
                        break

                    if line.strip().lower() == '/send':
                        break

                    if line.strip().lower() == '/commit':
                        break

                    if line.strip().lower() == '/execute':
                        break
                        
                    user_lines.append(line)
                    if len(user_lines) == 1 and "```" not in line and not line.endswith(":"):
                        break
            
                raw_input = "\n".join(user_lines).strip()
                if not raw_input:
                    continue
            
                with self.console.status("[bold cyan]Processing via LLM-Guard & LLM...", spinner="bouncingBar"):
                    result = self.send_to_daemon(raw_input)

                status = result.get("status")

                if status == "ERROR":
                    self.console.print(f"\n[bold red]SYSTEM ERROR:[/bold red] {result.get('reason')}")
                elif status in ["APPROVED", "SANITIZED", "EXECUTED"]:
                    
                    if status == "SANITIZED":
                        flags = ", ".join(result.get("threat_flags", []))
                        self.console.print(f"\n[bold yellow]THREAT DETECTED & NEUTRALIZED:[/bold yellow] {flags}")
                        self.console.print("[dim green]The malicious commands were trapped in the data block. Processing utility request...[/dim green]\n")
                    
                    raw_content = result.get("llm_response", "No content found.")
                    self.console.rule("[bold cyan]--- SECURE LLM RESPONSE ---")
                    self.console.print(raw_content)
                    self.console.rule()

            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[bold red]Shutting down client...[/bold red]")
                break