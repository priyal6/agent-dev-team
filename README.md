# 🤖 AI Dev Team  _(LangGraph edition)_

A multi-agent pipeline that takes a plain-English app request and produces a fully working REST API — complete with code, tests, and documentation.

Built on **LangGraph** with typed state, conditional edges, and built-in checkpointing.

## Architecture

```
User Request
     │
     ▼
  [pm] ──▶ [architect] ──▶ [developer] ──▶ [qa]
                                              │
                              ┌───────────────┴───────────────┐
                         approved?                        not approved?
                              │                                │
                         [documenter]                    [debugger]
                              │                                │
                         [write_files]               [documenter] ──▶ [write_files]
                              │                                              │
                             END                                            END
```

The `next_agent` field each node writes into `AgentState` drives LangGraph's
`conditional_edges` — so the LLM controls routing at the QA step.

## Stack

| Layer | Library |
|-------|---------|
| Orchestration | **LangGraph** `StateGraph` |
| LLM | **OpenAI** `gpt-4o` |
| Checkpointing | `MemorySaver` (swap for `SqliteSaver` to persist across restarts) |
| State | `AgentState` TypedDict (`state.py`) |

## Agents

| Node | Role | Output |
|------|------|--------|
| `pm` | Converts request → structured PRD | Project name, features, tech stack |
| `architect` | Designs REST API architecture | Endpoints, data models, file structure |
| `developer` | Writes all source code | Complete working files |
| `qa` | Reviews code + writes tests | Quality score, pytest suite, approve/reject |
| `debugger` | Fixes QA-identified issues | Corrected files _(only runs if QA rejects)_ |
| `documenter` | Writes documentation | README, API reference, setup guide |
| `write_files` | Saves everything to disk | `output/generated_app/` |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY=sk-...

# 3. Run with the default demo task (Todo REST API)
python main.py

# 4. Or pass your own task
python main.py "Build a REST API for a bookstore with inventory management"

# 5. Print the pipeline graph as a Mermaid diagram
python main.py --diagram
```

## Output

All generated files land in `output/generated_app/`:

```
output/generated_app/
├── app.py                    # Main application
├── requirements.txt          # App dependencies
├── test_app.py               # Pytest test suite
├── README.md                 # App README
├── API.md                    # API reference
├── SETUP.md                  # Setup guide
└── _pipeline_context.json    # Full AgentState dump (for debugging)
```


