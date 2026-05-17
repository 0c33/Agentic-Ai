# 🤖 Agentic AI Architect (v0.0.1)

A closed-loop AI system that takes a raw idea, interviews the user until it fully understands it, iteratively designs and prompt-tests an agent, generates standalone Python code, evaluates it via real subprocess execution, and ships an approved, runnable agent file.

> **Status:** Developer alpha. Requires manual setup. Not consumer-ready.

---

## 🧠 Core Philosophy

Most AI tools generate code in one pass. This system thinks in loops:

1. **It asks before it builds.** A clarification loop runs until intent is fully captured.
2. **It tests before it trusts.** Generated prompts are LLM-tested in Phase 3, then the final code is executed in a real subprocess in Phase 5.
3. **It refines until approved.** A structured rating schema drives iteration. A human gate controls every exit point.

---

## 🔄 System Flow

```
User Raw Idea
     ↓
Clarification Loop  →  Structured Idea Payload
                               ↓
              ┌────────────────────────────────────────┐
              │  Design Loop                            │
              │  Generate: Name, Scope, Prompt, Args   │
              │       ↓                                 │
              │  Prompt Test (LLM invoke, not subprocess│
              │       ↓                                 │
              │  Finish? ──no──→ refine + retry         │
              │       ↓ yes                             │
              │  Human Approval Gate                    │
              │       ↓ approved                        │
              └────────────────────────────────────────┘
                               ↓
              Code Generation Loop
                               ↓
              ┌────────────────────────────────────────┐
              │  Evaluation Loop                        │
              │  TestAgent: real subprocess execution   │
              │       ↓                                 │
              │  LLM Rating Schema                      │
              │       ↓                                 │
              │  Remake? ──yes──→ back to CodeGen       │
              │       ↓ no                              │
              │  Human Approval Gate                    │
              │       ↓ approved                        │
              └────────────────────────────────────────┘
                               ↓
              SaveAgent → {Agent_Name}.py
```

---

## 🔹 Phase Breakdown

### Phase 1 — Initialization
**`Agentic.__init__()`**
- Loads LLM via LangChain `init_chat_model` using an OpenAI-compatible endpoint (`localhost:8080/v1`).
- Configured with `enable_thinking: False` for structured, non-verbose output.
- Accepts raw unstructured user input, passes it to the clarification loop.

---

### Phase 2 — Clarification Loop
**`define_user_request()`**

Runs an interview loop. Does not proceed until the LLM signals it has fully understood the request.

LLM response schema per turn:
```json
{
  "done_understanding": bool,
  "question": str,
  "idea": str | null,
  "user_inputs_summary": str
}
```

- `done_understanding: false` → prints question, appends Q&A pair to `chat_history` string, retries.
- `done_understanding: true` → extracts `idea` payload, calls `Agentic_Ai()`.
- Full `chat_history` is appended as a string on every turn — no context is dropped between iterations.

---

### Phase 3 — Design Loop
**`Agentic_Ai()` + `Sandbox()`**

Takes the structured `idea` and enters a prompt refinement loop.

Each iteration generates:
```json
{
  "Agent_Name": str,
  "Agent_Scope": str,
  "Agent_Prompt": str,
  "Agent_Args": obj,
  "Finish": bool
}
```

**Important:** `Finish` is always `false` on iteration 0 — enforced via the counter value injected into the prompt. This prevents premature exit before any result exists.

`Sandbox()` at this stage is a **direct LLM invoke** — the generated prompt is tested against the LLM with the provided args. This is prompt validation, not code execution. Subprocess sandboxing happens later in Phase 5.

Loop tracking:
- Each attempt appends `{prompt_used, result}` to `agent_history`.
- `agent_history` is passed on every subsequent iteration — the LLM has full visibility into what was tried and what failed.
- `tries_count` increments each iteration and is injected into the prompt.

Exit:
- `Finish: true` + human approves → proceeds to `BuildAgent()`.
- `Finish: true` + human rejects → captures notes, adds to `user_notes`, continues loop.

---

### Phase 4 — Code Generation Loop
**`BuildAgent()`**

Switches from prompt design to Python code generation.

Sends to LLM:
- A method-level template showing expected code structure
- Full `main.py` source injected as a reference (self-referential generation)
- `agent_name`, `agent_scope`, `agent_prompt`, `example_result`, `user_request`
- Any notes and results from failed previous builds

Expected output schema:
```json
{
  "python_code": str,
  "response": str,
  "input_for_test": str,
  "input_text": str
}
```

Generated agents inherit the same structural patterns — error handling, JSON parsing, LLM initialization — from the injected source reference without hardcoding them per agent.

Immediately passes generated code to `RateAgentResult()` for evaluation.

---

### Phase 5 — Evaluation Loop
**`RateAgentResult()` + `TestAgent()`**

`TestAgent()` executes the generated code in a **real subprocess**:
- Writes code to `tempfile.NamedTemporaryFile`
- Executes via a dedicated venv Python interpreter
- Injects `PYTHONPATH` to make dependencies available inside the subprocess
- Pipes `input_for_test` to stdin
- Captures `stdout`, `stderr`, and `exit_code`
- Deletes the temp file in a `finally` block

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

- `Remake: true` → returns notes + agent result back to `BuildAgent()` for a new generation attempt.
- `Remake: false` → human approval gate: `Are you good with this? (Y/n)`.
  - Approved → `SaveAgent()`.
  - Rejected → captures human notes, loops back to `BuildAgent()`.

---

### Phase 6 — Output
**`SaveAgent()`**

Writes approved code to `{Agent_Name}.py`. The output is a standalone, runnable Python class.

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

```bash
python SuperIdeaToAtomicTasks.py
```

---

## 🔧 Component Reference

| Component | Method | Purpose |
|-----------|--------|---------|
| Initialization | `Agentic.__init__()` | LLM setup, raw input intake |
| Clarification | `define_user_request()` | Stateful interview loop, idea extraction |
| Design Loop | `Agentic_Ai()` | Iterative prompt generation and LLM-based prompt testing |
| Prompt Test | `Sandbox()` | LLM invoke of generated prompt against test args |
| Code Generation | `BuildAgent()` | Self-referential Python class generation |
| Subprocess Test | `TestAgent()` | Real execution via venv subprocess, captures stdout/stderr/exit |
| Evaluation | `RateAgentResult()` | Structured LLM rating + human approval gate |
| Output | `SaveAgent()` | Writes approved agent to `{Agent_Name}.py` |

---

## ⚙️ Engineering Notes

- **Two distinct testing stages:** Phase 3 tests prompts via LLM invoke. Phase 5 tests generated Python code via real subprocess execution. These are separate concerns.
- **Self-referential generation:** `BuildAgent()` injects the full `main.py` source as a reference, ensuring generated agents follow consistent structure without hardcoding patterns per output.
- **State tracking:** `chat_history` (clarification turns) and `agent_history` (design iterations) are passed in full on every call — no context is lost mid-loop.
- **Counter guard:** `tries_count` is injected into the Phase 3 prompt to enforce `Finish: false` on iteration 0, preventing exit before any result exists.
- **JSON parsing:** Raw `json.loads()` on LLM output. If the model wraps output in markdown fences, parsing will fail and the loop retries via the `except` block.

---

## 📦 Prerequisites

- Python 3.10+
- A Python venv with LangChain installed
- Local LLM endpoint at `http://localhost:8080/v1` (tested with Qwen3.6-35B via llama.cpp/vLLM)

```bash
pip install langchain langchain-openai
```

---

## ⚙️ Setup

Before running, edit these hardcoded values in `main.py`:

```python
# In Agentic.__init__() — set your model name
model="your-model-name-here"

# In TestAgent() — set your venv Python path
venv_py = "/path/to/your/.venv/bin/python3.12"
site_packages = "/path/to/your/.venv/lib/python3.12/site-packages"

# In BuildAgent() → ReadFile() — set your main.py path
self.ReadFile('/path/to/your/main.py')
```

---

## 🚀 Usage

```bash
python main.py
```

1. Enter your raw idea or project description
2. Answer clarification questions until `done_understanding: true`
3. Review prompt test output per design iteration — approve or provide notes
4. Generated Python code is executed in subprocess and rated
5. Approve the final result → saved as `{Agent_Name}.py`

---

## 📈 Roadmap

- [ ] `.env` / `config.yaml` for model name, paths, and endpoint
- [ ] Markdown fence stripping before JSON parsing
- [ ] Subprocess timeout and resource limits
- [ ] Persistent session state
- [ ] Multi-agent composition

---

## 🏷️ License

MIT © 2026
