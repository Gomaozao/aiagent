# aiagent

A minimal command-line **AI coding agent** powered by Google's Gemini models. Give it a prompt in plain English and it will plan and carry out a sequence of file-system actions — listing directories, reading files, writing files, and running Python — until it can answer you.

It's a compact demonstration of the *agentic loop*: the model is handed a set of tools, decides which ones to call, sees the results, and keeps going until the task is done.

---

## How it works

```
            ┌─────────────────────────────────────────────┐
            │                  main.py                     │
            │   (agent loop, up to MAX_ITERS iterations)   │
            └─────────────────────────────────────────────┘
                               │
              user prompt ─────┤
                               ▼
                  ┌────────────────────────┐
                  │   Gemini 2.5 Flash      │
                  │  + system instruction   │
                  │  + tool declarations    │
                  └────────────────────────┘
                               │
              function call(s) │
                               ▼
                  ┌────────────────────────┐
                  │     call_function       │
                  │  dispatches to a tool   │
                  └────────────────────────┘
                               │
              tool result      │  (fed back into the conversation)
                               └──────────────► loop until a final
                                                text answer is returned
```

On each iteration the model may either return a final text answer (the loop ends) or request one or more tool calls. Tool results are appended to the conversation and sent back to the model on the next turn. The loop runs for at most `MAX_ITERS` (default `20`) iterations.

## Tools

The agent has access to four functions, all scoped to a fixed working directory:

| Function | Description |
| --- | --- |
| `get_files_info` | Lists files in a directory with sizes and directory flags |
| `get_file_content` | Reads a file's contents (truncated at `MAX_CHARS`, default 10,000) |
| `write_file` | Writes/overwrites a file with the given content |
| `run_python_file` | Executes a `.py` file (with optional args) and returns stdout/stderr |

Every call has its `working_directory` injected automatically and is checked to ensure the resolved path stays inside that directory.

## Requirements

- Python ≥ 3.10
- [uv](https://github.com/astral-sh/uv) for dependency management
- A Google Gemini API key

## Installation

```bash
git clone <repo-url>
cd aiagent
uv sync
```

## Configuration

Create a `.env` file in the project root with your Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

## Usage

```bash
uv run main.py "your prompt here"
```

Add `--verbose` to see token counts and each function call with its arguments and results:

```bash
uv run main.py "fix the bug in the calculator" --verbose
```

### Examples

```bash
# Ask about the codebase
uv run main.py "what files are in the project?"

# Read and explain code
uv run main.py "explain how the calculator renders its output"

# Run code and report the result
uv run main.py "run main.py with the expression 3 + 5"
```

## Project structure

```
aiagent/
├── main.py                 # Entry point and agent loop
├── call_function.py        # Tool registry and dispatcher
├── config.py               # MAX_CHARS, WORKING_DIR, MAX_ITERS
├── prompts.py              # System instruction
├── functions/              # Tool implementations
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python_file.py
└── calculator/             # Sample app the agent operates on
    ├── main.py
    ├── tests.py
    └── pkg/
```

The `calculator/` directory is a small standalone app included as a target for the agent to read, run, and modify.

## Configuration values

These live in `config.py`:

| Setting | Default | Meaning |
| --- | --- | --- |
| `MAX_CHARS` | `10000` | Max characters returned when reading a file |
| `WORKING_DIR` | `./calculator` | Directory the agent is allowed to operate in |
| `MAX_ITERS` | `20` | Max iterations of the agent loop per prompt |

## ⚠️ Disclaimer

This is an experimental proof-of-concept, provided **as-is and without any warranty**. A few things to be aware of before running it:

- **It executes arbitrary code and writes files.** The agent can run Python and overwrite files on your machine.
- **The safety model is intentionally minimal** — access is restricted to a single working directory via a path-prefix check, and that directory is hardcoded to `./calculator`. This is *not* a hardened sandbox.
- **It is not intended for production use**, nor for pointing at directories whose contents you care about.

Run it only against throwaway directories, and review what it does (use `--verbose`).
