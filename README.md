# 🤖 Agentic AI Architect (v0.0.1)

A closed-loop AI system that takes a raw idea, interviews the user until it fully understands it, iteratively designs and tests an agent prompt, evaluates the output with a structured rating schema, and ships a standalone, runnable Python agent.

> **Status:** Alpha. Core loop is complete and functional. Not production-hardened.

---

## 🧠 Core Philosophy

Most AI tools generate code in one pass. This system thinks in loops:

1. **It asks before it builds.** A clarification loop runs until intent is fully captured — no assumptions.
2. **It tests before it trusts.** Every generated prompt is executed in a sandboxed subprocess before evaluation.
3. **It refines until approved.** A structured rating schema drives iteration. A human gate controls the exit.

---

## 🔄 System Flow

```
User Raw Idea
     ↓
Clarification Loop  →  Structured Idea Payload
                               ↓
              ┌────────────────────────────────────┐
              │  Design Loop                        │
              │  Generate Prompt + Args             │
              │       ↓                             │
              │  Sandbox (subprocess + venv)        │
              │       ↓                             │
              │  LLM Rating Schema                  │
              │       ↓                             │
              │  Remake? ──yes──→ refine + retry    │
              │       ↓ no                          │
              │  Human Approval Gate                │
              │       ↓ approved                    │
              └────────────────────────────────────┘
                               ↓
              Code Generation  →  Standalone .py Agent
```

---

## 🔹 Phase Breakdown

### Phase 1 — Initialization
**`Agentic.__init__()`**
- Loads LLM client (`Qwen3.6-35B` via vLLM at `localhost:8080/v1`)
- Configures inference parameters: no thinking tokens, structured output mode
- Accepts raw, unstructured user input

---

### Phase 2 — Interactive Clarification Loop
**`define_user_request()`**

Runs an interview loop against the raw input. Does not proceed until intent is fully understood.

LLM response schema per turn:
```json
{
  "done_understanding": bool,
  "question": str,
  "idea": str | null,
  "user_inputs_summary": str
}
```

- `done_understanding: false` → prints question, appends user reply to `chat_history`, retries
- `done_understanding: true` → extracts structured `idea` payload, exits loop
- Full `chat_history` is passed on every turn — no context loss across iterations

---

### Phase 3 — Iterative Design & Sandbox Testing
**`Agentic_Ai()` + `Sandbox()`**

Takes the structured `idea` and enters a refinement loop.

Each iteration generates:
```json
{
  "Agent_Name": str,
  "Agent_Scope": str,
  "Agent_Prompt": str,
  "Agent_Args": obj
}
```

`Sandbox()` execution:
- Passes `Agent_Prompt` + `Agent_Args` to the LLM
- Captures raw output as a test result
- Appends to `agent_history` for state tracking across iterations

Loop control:
- `Finish: false` → increments `tries_count`, updates prompt with history, retries
- `Finish: true` → pauses for human approval before exiting

`agent_history` acts as a lightweight state machine — every iteration is informed by all previous attempts.

---

### Phase 4 — Standalone Code Generation
**`BuildAgent()`**

Switches from design mode to code generation mode.

Sends to LLM:
- Reference template (from `main.py` itself)
- Final `agent_name`, `agent_scope`, `agent_prompt`, `example_result`

Expected output schema:
```json
{
  "python_code": str,
  "response": str,
  "input_for_test": str
}
```

The reference template is injected directly — generated agents inherit the same error handling, JSON parsing, and structural patterns without hardcoding them per agent.

---

### Phase 5 — Evaluation & Human Approval
**`RateAgentResult()` + `TestAgent()`**

`TestAgent()` runs the generated code in a real subprocess:
- Writes to `tempfile.NamedTemporaryFile`
- Executes via isolated venv Python path
- Injects `PYTHONPATH` to preserve `langchain` availability
- Captures `stdout`, `stderr`, and `exit_code`

LLM rating schema:
```json
{
  "Rating": int,
  "Response": str,
  "Result_Quality": str,
  "Instruct": bool,
  "Notes": str,
  "Remake": bool
}
```

- `Remake: true` → loops back to `BuildAgent()` with `Notes` as refinement instructions
- `Remake: false` → human approval gate: `Are you happy with these results? (Y/n)`

---

### Phase 6 — Final Output
**`SaveAgent()`**

- Writes approved code to `{Agent_Name}.py`
- Output is a standalone, runnable Python class:
  - LLM initialization
  - Input handling
  - JSON parsing with error fallbacks
  - No framework dependency in the generated agent itself

---

## 📄 Example Output

```python
class SuperIdeaToAtomicTasks:
    def __init__(self) -> None:
        self.llm = init_chat_model(...)
        self.define_user_request(self.get_user_input())

    def get_user_input(self):
        user_request = input("Enter your Super Idea/Project: ")
        ...
```

Run independently:
```bash
python SuperIdeaToAtomicTasks.py
```

---

## 🔧 Component Reference

| Component | Method | Purpose |
|-----------|--------|---------|
| Initialization | `Agentic.__init__()` | LLM setup, raw input intake |
| Clarification | `define_user_request()` | Stateful interview loop, idea extraction |
| Design Loop | `Agentic_Ai()` | Iterative prompt generation and refinement |
| Sandboxing | `Sandbox()` / `TestAgent()` | Subprocess execution, output capture |
| Evaluation | `RateAgentResult()` | Structured LLM rating + human approval gate |
| Code Generation | `BuildAgent()` | Template-injected standalone agent synthesis |
| Output | `SaveAgent()` | Atomic write to `{Agent_Name}.py` |

---

## ⚙️ Engineering Notes

- **JSON parsing:** All LLM responses are regex-stripped of markdown fences before parsing. Structured fallbacks on failure.
- **Sandboxing:** Process-level isolation via `tempfile` + `subprocess` + venv Python path. No resource limits or timeouts yet — known limitation.
- **State tracking:** `chat_history` and `agent_history` are passed in full on every iteration. No context is lost between turns.
- **Self-referential generation:** `BuildAgent()` injects `main.py`'s own template as a reference, ensuring all generated agents follow consistent structure and error handling.
- **Human-in-the-loop:** `Finish: true` is LLM-evaluated, but the loop never exits without explicit human approval.

---

## ⚠️ Known Limitations

- Subprocess sandbox has no timeout or resource cap — a runaway generated script will hang the loop
- LLM rating is schema-structured but not rubric-calibrated — quality judgment depends on the model
- No persistent state between sessions — each run starts from scratch
- Single-agent output only — no multi-agent composition yet

---

## 📦 Prerequisites

- Python 3.10+
- LangChain (LLM invocation only)
- Local LLM endpoint at `http://localhost:8080/v1` (tested with Qwen3.6-35B via vLLM)

```bash
pip install langchain langchain-openai
```

---

## 🚀 Usage

```bash
python main.py
```

1. Enter your raw idea or project description
2. Answer clarification questions until the system signals it understands
3. Review sandbox test output per design iteration
4. Watch LLM rating schema evaluate and refine
5. Approve the final result → agent saved as `{Agent_Name}.py`

---

## 📈 Roadmap

- [ ] Subprocess timeout and resource limits
- [ ] Rubric-calibrated rating criteria
- [ ] Async execution and streaming responses
- [ ] Multi-agent composition and dependency resolution
- [ ] CLI interface and config-driven LLM routing

---

## 🏷️ License

MIT © 2026 SBM Labs
