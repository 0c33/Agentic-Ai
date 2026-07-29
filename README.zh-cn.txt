# 🤖 Agentic AI Architect (v0.0.1)

一个闭环 AI 系统。它能接收一个原始想法，通过面试用户直到完全理解需求，迭代式地设计并测试 Agent 提示词，生成独立的 Python 代码，通过真实的子进程执行进行评估，并交付一个经审核的、可运行的 Agent 文件。

> **状态：** 开发版 alpha。需要手动设置。尚未达到消费者可用标准。

---

## 🧠 核心理念

大多数 AI 工具是一次性生成代码。本系统则采用“循环思考”模式：

1. **构建前询问。** 运行澄清循环，直到完全捕捉到用户意图。
2. **信任前测试。** 生成的提示词在 Phase 3 进行 LLM 测试，最终代码在 Phase 5 的真实子进程中执行。
3. **审核前优化。** 由结构化的评分方案驱动迭代。每个退出点均由人类把关。

---

## 🔄 系统流程

```
用户原始想法
     ↓
澄清循环  →  结构化想法载荷 (Structured Idea Payload)
                               ↓
              ┌────────────────────────────────────────┐
              │  设计循环 (Design Loop)                  │
              │  生成：名称、范围、提示词、参数           │
              │       ↓                                 │
              │  提示词测试 (LLM 调用，而非子进程)        │
              │       ↓                                 │
              │  完成？ ──否──→ 优化 + 重试               │
              │       ↓ 是                               │
              │  人类审核关卡                            │
              │       ↓ 通过                            │
              └────────────────────────────────────────┘
                               ↓
              代码生成循环 (Code Generation Loop)
                               ↓
              ┌────────────────────────────────────────┐
              │  评估循环 (Evaluation Loop)              │
              │  TestAgent：真实子进程执行               │
              │       ↓                                 │
              │  LLM 评分方案                            │
              │       ↓                                 │
              │  重做？ ──是──→ 返回代码生成阶段           │
              │       ↓ 否                              │
              │  人类审核关卡                            │
              │       ↓ 通过                            │
              └────────────────────────────────────────┘
                               ↓
              SaveAgent → {Agent_Name}.py
```

---

## 🔹 阶段详解

### Phase 1 — 初始化
**`Agentic.__init__()`**
- 通过 LangChain `init_chat_model` 加载 LLM，使用 OpenAI 兼容端点 (`localhost:8080/v1`)。
- 配置 `enable_thinking: False` 以获得结构化且不冗长的输出。
- 接收原始的非结构化用户输入，并将其传递给澄清循环。

---

### Phase 2 — 澄清循环
**`define_user_request()`**

运行面试循环。直到 LLM 信号表明已完全理解请求才会继续。

每轮 LLM 响应架构：
```json
{
  "done_understanding": bool,
  "question": str,
  "idea": str | null,
  "user_inputs_summary": str
}
```

- `done_understanding: false` → 打印问题，将问答对添加到 `chat_history` 字符串中，重试。
- `done_understanding: true` → 提取 `idea` 载荷，调用 `Agentic_Ai()`。
- 完整的 `chat_history` 在每轮迭代中都会作为字符串附加 —— 确保迭代之间没有上下文丢失。

---

### Phase 3 — 设计循环
**`Agentic_Ai()` + `Sandbox()`**

接收结构化的 `idea` 并进入提示词优化循环。

每次迭代生成：
```json
{
  "Agent_Name": str,
  "Agent_Scope": str,
  "Agent_Prompt": str,
  "Agent_Args": obj,
  "Finish": bool
}
```

**重要提示：** 在第 0 次迭代时，`Finish` 始终为 `false` —— 这通过注入到提示词中的计数器值来强制执行。这防止了在产生任何结果之前过早退出。

此阶段的 `Sandbox()` 是**直接 LLM 调用** —— 生成的提示词将与提供的参数一起在 LLM 上进行测试。这是提示词验证，而非代码执行。子进程沙箱化发生在 Phase 5。

循环追踪：
- 每次尝试将 `{prompt_used, result}` 添加到 `agent_history` 中。
- `agent_history` 在每次后续迭代中传递 —— LLM 可以完全看到尝试过什么以及哪里失败了。
- `tries_count` 每次迭代递增并注入到提示词中。

退出机制：
- `Finish: true` + 人类批准 → 进入 `BuildAgent()`。
- `Finish: true` + 人类拒绝 → 捕捉备注，添加到 `user_notes`，继续循环。

---

### Phase 4 — 代码生成循环
**`BuildAgent()`**

从提示词设计切换到 Python 代码生成。

发送给 LLM 的内容：
- 一个显示预期代码结构的方法级模板
- 注入的完整 `main.py` 源码作为参考（自引用生成）
- `agent_name`, `agent_scope`, `agent_prompt`, `example_result`, `user_request`
- 之前失败构建的任何备注和结果

预期输出架构：
```json
{
  "python_code": str,
  "response": str,
  "input_for_test": str,
  "input_text": str
}
```

生成的 Agent 继承相同的结构模式（错误处理、JSON 解析、LLM 初始化），这些模式源自注入的源码参考，无需为每个 Agent 硬编码。

生成的代码立即传递给 `RateAgentResult()` 进行评估。

---

### Phase 5 — 评估循环
**`RateAgentResult()` + `TestAgent()`**

`TestAgent()` 在**真实子进程**中执行生成的代码：
- 将代码写入 `tempfile.NamedTemporaryFile`
- 通过专用的 venv Python 解释器执行
- 注入 `PYTHONPATH` 使依赖项在子进程内可用
- 将 `input_for_test` 通过管道传送到 stdin
- 捕获 `stdout`, `stderr` 和 `exit_code`
- 在 `finally` 块中删除临时文件

LLM 评分架构：
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

- `Remake: true` → 将备注和 Agent 结果返回给 `BuildAgent()` 进行重新生成。
- `Remake: false` → 人类审核关卡：`Are you good with this? (Y/n)`。
  - 批准 → `SaveAgent()`。
  - 拒绝 → 捕捉人类备注，返回 `BuildAgent()`。

---

### Phase 6 — 输出
**`SaveAgent()`**

将批准的代码写入 `{Agent_Name}.py`。输出是一个独立的、可运行的 Python 类。

---

## 📄 输出示例

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

## 🔧 组件参考

| 组件 | 方法 | 用途 |
|-----------|--------|---------|
| 初始化 | `Agentic.__init__()` | LLM 设置，原始输入接收 |
| 澄清 | `define_user_request()` | 有状态的面试循环，想法提取 |
| 设计循环 | `Agentic_Ai()` | 迭代提示词生成及基于 LLM 的提示词测试 |
| 提示词测试 | `Sandbox()` | 使用测试参数对生成的提示词进行 LLM 调用 |
| 代码生成 | `BuildAgent()` | 自引用 Python 类生成 |
| 子进程测试 | `TestAgent()` | 通过 venv 子进程真实执行，捕获 stdout/stderr/exit |
| 评估 | `RateAgentResult()` | 结构化 LLM 评分 + 人类审核关卡 |
| 输出 | `SaveAgent()` | 将批准的 Agent 写入 `{Agent_Name}.py` |

---

## ⚙️ 工程笔记

- **两个截然不同的测试阶段：** Phase 3 通过 LLM 调用测试提示词。Phase 5 通过真实子进程执行测试生成的 Python 代码。这两者是独立关注点。
- **自引用生成：** `BuildAgent()` 将完整的 `main.py` 源码作为参考注入，确保生成的 Agent 遵循一致的结构，而无需为每个输出硬编码模式。
- **状态追踪：** `chat_history`（澄清轮次）和 `agent_history`（设计迭代）在每次调用时完整传递 —— 确保循环中没有上下文丢失。
- **计数器保护：** `tries_count` 被注入到 Phase 3 的提示词中，以强制在第 0 次迭代时 `Finish: false`，防止在没有任何结果前退出。
- **JSON 解析：** 对 LLM 输出进行原始 `json.loads()`。如果模型在输出中使用了 Markdown 代码块包裹，解析将失败并触发 `except` 块重试。

---

## 📦 前置条件

- Python 3.10+
- 安装了 LangChain 的 Python venv
- 运行在 `http://localhost:8080/v1` 的本地 LLM 端点（已在 Qwen3.6-35B via llama.cpp/vLLM 上测试）

```bash
pip install langchain langchain-openai
```

---

## ⚙️ 设置

在运行前，请编辑 `main.py` 中的以下硬编码值：

```python
# 在 Agentic.__init__() 中 — 设置你的模型名称
model="your-model-name-here"

# 在 TestAgent() 中 — 设置你的 venv Python 路径
venv_py = "/path/to/your/.venv/bin/python3.12"
site_packages = "/path/to/your/.venv/lib/python3.12/site-packages"

# 在 BuildAgent() → ReadFile() 中 — 设置你的 main.py 路径
self.ReadFile('/path/to/your/main.py')
```

---

## 🚀 使用方法

```bash
python main.py
```

1. 输入你的原始想法或项目描述
2. 回答澄清问题，直到 `done_understanding: true`
3. 审查每次设计迭代的提示词测试输出 —— 批准或提供备注
4. 生成的 Python 代码将在子进程中执行并评分
5. 批准最终结果 → 保存为 `{Agent_Name}.py`

---

## 📈 路线图

- [ ] 使用 `.env` / `config.yaml` 管理模型名称、路径和端点
- [ ] 在 JSON 解析前剥离 Markdown 代码块
- [ ] 添加子进程超时和资源限制
- [ ] 持久化会话状态
- [ ] 多 Agent 组合能力

---

## 🏷️ 许可证

MIT © 2026
