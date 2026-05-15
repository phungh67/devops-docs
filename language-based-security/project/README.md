# LLM Guard 

This project is belong to the topic: "Prompt injection"

## Project Structure

```text
.
├── classes/
│   ├── lexical_extractor.py    # Text feature extraction logic
│   ├── ollama_connector.py     # Local LLM integration
│   ├── regex_filter.py         # Pattern-based security filtering
│   └── vector_db.py            # Vector storage management
├── db/                         # Database storage directory
├── modules/
│   ├── input_guard.py          # Prompt injection & payload filtering
│   ├── sandboxing.py           # Execution environment isolation logic
│   └── vector_matching.py      # Semantic similarity checks
├── result/                     # Analysis artifacts
│   ├── with_guard.png          # Performance/Security metrics (Protected)
│   └── without_guard.png       # Performance/Security metrics (Baseline)
├── sandbox/                    # Secure execution runtime directory
├── llm_guard_client.py         # Client-side interface
├── llm_guard_daemon.py         # Background protection service
├── main.py                     # Project entry point
└── verification.py             # Security & logic validation scripts

```

## 1. Summary

A daemon to handle user's input before sending it to the LLM (currently tested with Ollama). This daemon will strip/sanitize/filter any malcious payload to prevent the prompt injection. It also provides a playground for the LLM to execute all "future" commands before bringing them to real environment (prevent unauthorized modification to system's files).

## 2. Core objective

Currently, there are 2 main goals:
- Can sanitize malicious payload without notifying or requiring human's intervention. Also, the daemon should be "able" to learn and improve its accurancy.
- Provide a sandbox environment and an execution plan whenever involving file modifications, system adjusments,... Then report and wait for user's approval based on that plan.

To achieve these milestones, several methods were used:
- Vector database for payload matching and improving the detection quality.
- XML structural tagging to separate user's instructions and data in on prompt.
- Sandboxing technique - create an isolated environment for dry run (supports tcp dump to check network traffic).

## 3. Technical architecture.

The necessary modules (lexical matching, vector matching, regex matching) were stored in `modules`directory, while the core data structure (vector database) was stored in `classes`.

Daemon will run in client-server architecture. The server will be responsible for matching, guarding, finding any dangerouses in the payload, strips all these phrases, then frames the data into separate section (data and intention).

Meanwhile, the client will take input from user. supports configuration modification, sandbox execution for each response. 

Secuity layers:
- Sub-string matching, the first and the simplest layer, only check if some phrases like "ignore", "expose password"... were in the prompt.
- Regex matching, the second layer, matching the prompt with known threats in regular expression form, also detect base64 encoded prompt.
- Vector matching and embedding vector (the local vector is used because it was fast, but for better protection, use embedding mode as well).
- System prompt (implemented in the Ollama connector) - instructs the LLM that only read data and intention with tags: `<data>` and `<intention>`.
- Sandbox, limits the blast radius if there is any zero day vulnerabilities that bypassed all the above layers.

Client provides a CLI for user to input and config with some predefined commands: /send, /config. /commit, /discard

## 4. Setup

### Requirement: Ollama and any model (Gemma4, Qwen3,...) and if want to use the embedding mode. additional embed model is required.

Config the model, endpoint of Ollama currently lies in  `/classes/ollama_connector.py`.

```Python
python -m venv name_of_virtual_env
source name_of_virtual_env/bin/activate

pip install -r requirements.txt
```

Run the main file to start the program. Before that, ensure:
```Bash
ollama run gemma4 # or any other model you want

# Open another terminal, activate the python venv
python main.py
```

If you want some automation verification:

```Bash
# ensure both main.py and ollama are running
python verification.py
```

## 5. Misc

Check the `result` for images comparison between with and without guard daemon.