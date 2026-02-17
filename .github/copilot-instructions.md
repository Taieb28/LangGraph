# LangGraph AI Coding Agent Instructions

## Big Picture Architecture

- The project implements a Telegram bot workflow using FastAPI as the server backend.
- Data flow: Telegram User → Telegram Bot (Webhook) → Render Server (FastAPI) → LangGraph Agent (Gemini + Tool) → Response → Telegram → User.
- The LangGraph Agent is the core logic, integrating Gemini and custom tools for handling requests.

## Key Components

- `main.py`: Entry point, likely sets up FastAPI server and webhook handling.
- `agent.py`: Implements the LangGraph Agent logic, including Gemini integration and tool orchestration.
- `tools.py`: Defines custom tools used by the agent.
- `requirements.txt`: Lists Python dependencies (ensure to install before running).

## Developer Workflows

- **Install dependencies:**
  ```shell
  pip install -r requirements.txt
  ```
- **Run server:**
  (If FastAPI is used)
  ```shell
  uvicorn main:app --reload
  ```
- **Debug agent logic:**
  Focus on `agent.py` and `tools.py` for core agent behaviors.

## Project-Specific Patterns

- Agent logic is modular: tools are defined separately and integrated via the agent.
- Data flows are explicit and linear, matching the architecture diagram in README.
- External integrations: Gemini (AI), Telegram (bot), FastAPI (server).

## Integration Points

- Telegram webhook endpoint handled in `main.py`.
- FastAPI server routes connect to agent logic.
- Gemini and custom tools are orchestrated in `agent.py`.

## Examples

- To add a new tool, define it in `tools.py` and register it in `agent.py`.
- To modify response logic, update the agent's handling in `agent.py`.

## References

- See [README.md](LangGraph/README.md) for architecture overview.
- Key files: [main.py](LangGraph/main.py), [agent.py](LangGraph/agent.py), [tools.py](LangGraph/tools.py).

---

**Feedback Requested:**
Please review and suggest improvements or clarify any unclear/incomplete sections.
