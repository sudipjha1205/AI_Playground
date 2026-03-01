# 🚀 AI Playground

A production-ready multi-agent AI platform built with Streamlit, LangChain, and Claude.

## Architecture

```
ai_playground/
├── app.py                          # UI routing ONLY (no business logic)
├── requirements.txt
├── .env.example
│
├── agents/                         # Isolated agent modules
│   ├── base_agent.py               # Abstract base with LangChain + memory
│   ├── orchestrator_agent.py       # LLM-based intent classifier & router
│   ├── escape_room_agent.py        # EREBUS-7 space station game
│   ├── mind_reader_agent.py        # ORACLE psychic number/object guesser
│   └── personality_agent.py       # PSYCHE Big Five profiler
│
├── tools/                          # MCP-style structured tools
│   ├── base_tool.py                # ToolResult schema, JSON helpers
│   ├── escape_room_tools.py        # Game state parser & hint tool
│   ├── mind_reader_tools.py        # Mind state parser & yes/no validator
│   └── personality_tools.py       # Analysis state parser & Big Five formatter
│
├── prompts/                        # All LLM prompts isolated here
│   ├── orchestrator_prompts.py
│   ├── escape_room_prompts.py
│   ├── mind_reader_prompts.py
│   └── personality_prompts.py
│
└── utils/
    ├── config.py                   # Environment config loader
    └── logger.py                   # Centralized logging
```

## Setup

### 1. Clone & Install

```bash
git clone <repo>
cd AI_PLAYGROUND

python -m venv my-env
source my-env/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure API Key

```bash
add .env file in the main directory
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```


### 3. Run

```bash
streamlit run app.py
```

Open: http://localhost:8501

## Key Design Decisions

### True Agent Architecture
- Each agent is an isolated class with its own `InMemoryChatMessageHistory`
- No agent shares state with another
- The orchestrator uses LLM reasoning (not keyword matching) to classify intent

### MCP-Style Tools
- All tools return `ToolResult` (Pydantic model) with structured JSON
- Game state embedded in LLM responses as labeled code blocks
- Tools parse, validate, and normalize all structured data

### Separation of Concerns
- `app.py` → UI & routing only
- `agents/` → business logic & LLM calls
- `tools/` → structured data processing
- `prompts/` → all prompt strings
- `utils/` → config & logging

## 5-Minute Demo Script

### Minute 1 — Dashboard
- Open the app. Show the dark neon-noir theme.
- Explain the 3 agents shown on the dashboard cards.
- Point out the sidebar navigation.

### Minute 2 — Escape Room
- Click "Launch Escape Room" → Click "Initialize Emergency Systems"
- Show the atmospheric ARIA intro, oxygen level, puzzle tracker
- Answer the first riddle (MAP) — watch oxygen change, progress bar update
- Demonstrate wrong answer → oxygen drops, tension builds

### Minute 3 — Mind Reader
- Switch to Mind Reader → Click "Awaken Oracle"
- Think of a number (say 37)
- Answer YES/NO questions — show the step tracker, confidence bar rising
- Let Oracle guess — show the dramatic reveal

### Minute 4 — Personality Analyzer
- Switch to Personality → Click "Begin Analysis"
- Answer all 5 questions naturally
- Show the Big Five bars rendering in real-time
- Highlight the archetype, MBTI type reveal, balloons animation

### Minute 5 — Architecture
- Show the folder structure
- Highlight: each agent has isolated memory
- Show how tools return structured JSON
- Note the orchestrator uses Claude itself to route (not if-else)
- Questions!

## Notes
- The orchestrator is activated automatically when using the sidebar nav
- Each sidebar navigation resets the current session
- API key can be entered in sidebar if not set via .env
