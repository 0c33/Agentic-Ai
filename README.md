


# 🤖 Agentic AI Architect (v0.0.1)

A self-referential, iterative AI system that takes a raw idea, interviews the user until it fully understands it, designs an agent architecture, sandbox-tests it, rates its output, and ships a standalone, production-ready Python agent.

No prompt chaining. No static templates. A closed-loop system that refines itself until the output meets the user's intent.

---

## 🧠 Core Philosophy
Current AI systems generate code or answers in one pass. This system **thinks in loops**:
1. It doesn't assume. It asks until it understands.
2. It doesn't guess. It tests in isolation before it trusts.
3. It doesn't settle. It iterates until `Finish: True`.

Built for engineers who want agents that **structure chaos into execution-ready blueprints**.

---

## 🔄 How It Works
```
User Raw Idea → Clarification Loop → Idea Extraction
                              ↓
                 Design Loop (Prompt → Sandbox → Rating → Refine)
                              ↓
                 Code Generation → Standalone `.py` Agent
```

### 🔍 Phase 1: Clarification Loop
- The system intercepts a high-level request and begins an interactive interview.
- It asks targeted questions about purpose, functionality, constraints, and outcomes.
- Chat history is maintained until `done_understanding: true`.
- Output: A precise, structured `idea` payload ready for architecture.

### 🏗 Phase 2: Design & Refine Loop
- The system generates a candidate agent prompt + scope + test args.
- It runs the prompt in a **sandboxed subprocess** using a venv Python interpreter.
- It evaluates the result via LLM rating + human approval.
- If `Finish: false`, it updates the prompt, appends to `agent_history`, and retries.
- Loop continues until the output is structurally sound and user-approved.

### 📦 Phase 3: Standalone Generation
- Once approved, the system generates a clean, dependency-ready Python class.
- It embeds the final prompt, input handling, JSON parsing, and error fallbacks.
- Saves as `{Agent_Name}.py` → ready to run independently.

---

## ✨ Key Features
- 🧩 **Interactive Clarification Engine**: Asks until it understands, never assumes.
- 🔄 **Self-Correcting Design Loop**: Auto-refines prompts based on sandbox feedback.
- 🛡️ **Subprocess Sandboxing**: Tests generated prompts in isolated temp files + venv isolation.
- ⚖️ **Built-in Rating System**: LLM evaluation + human approval gate before saving.
- 📝 **Strict JSON Control Flow**: Regex-stripped parsing, error fallbacks, structured args.
- 🐍 **Standalone Output**: Ships clean, runnable Python agents with zero external deps.

---

## 📦 Prerequisites
- Python 3.10+
- LangChain + LangChain-OpenAI
- Local LLM endpoint (llama.cpp/vLLM) at `http://localhost:8080/v1`
```bash
pip install langchain langchain-openai
```

## 🚀 Usage
```bash
python main.py
```
1. Enter your raw idea/project
2. Answer clarification questions
3. Review sandbox tests & ratings
4. Approve → Save as standalone `.py`

---

## 📄 Example Output
Generated agents follow a clean, runnable template:
```python
class SuperIdeaToAtomicTasks:
    def __init__(self) -> None:
        self.llm = init_chat_model(...)
        self.define_user_request(self.get_user_input())

    def get_user_input(self):
        user_request = input("Enter your Super Idea/Project: ")
        # ...
```
Run independently: `python SuperIdeaToAtomicTasks.py`

---

## 🔧 Technical Architecture
| Component | Purpose |
|-----------|---------|
| `define_user_request()` | Interactive clarification loop with chat history |
| `Agentic_Ai()` | Iterative design, sandbox testing, prompt refinement |
| `Sandbox()` | Temp file + subprocess execution with venv path isolation |
| `RateAgentResult()` | LLM evaluation + human approval gate |
| `BuildAgent()` | Template-based standalone code generation |
| `SaveAgent()` | Atomic file writing to `{Agent_Name}.py` |

### 📌 Engineering Notes
- JSON parsing strips markdown code blocks automatically with regex fallback
- Sandbox uses `tempfile` + `subprocess` with configurable venv Python path
- LLM context history is appended per iteration to maintain design state
- `Finish: True` is LLM-judged but gated behind human approval

---

## 📈 Roadmap (v0.0.2+)
- [ ] Async execution & streaming responses
- [ ] Multi-agent pipelines & dependency resolution
- [ ] Config-driven LLM routing (temperature, top_p, model switching)
- [ ] Pytest suite for generated agents
- [ ] CLI interface & package distribution (`pip install agentic-architect`)

---

## 🏷️ License
MIT © 2026 SBM Labs

---
