# agora-code

> Scan any codebase. Turn it into an AI agent.

Point `agora-code` at your repo and it automatically discovers all API endpoints, exposes them as MCP tools, and plugs into Claude Desktop or Cursor — with memory that learns from past calls.

---

## Quick Start

```bash
pip install agora-code

# Scan your API (auto-detects OpenAPI → Python AST → Regex)
agora-code scan ./my-api

# Start MCP server (plug into Claude Desktop)
agora-code serve ./my-api --url http://localhost:8000
```

Then in Claude Desktop, you can ask things like:
> *"Show me all users"* → Claude calls `GET /users`
> *"Add item to cart"* → Claude calls `POST /cart/add`

---

## How It Works

```
Your API code
    ↓ agora-code scan
Route catalog (method, path, params, docs)
    ↓ agora-code serve  
MCP server (one tool per route)
    ↓ Claude calls tools
agora-code executes HTTP calls + stores in agora-mem
    ↓ Next call
Uses past context (stats, errors, patterns)
```

**Claude is the chatbot. agora-code provides the memory-aware tools.**

---

## Extraction Strategy (auto-detected)

| Tier | Method | Works on | Cost |
|------|--------|----------|------|
| 1 | OpenAPI spec | Any language with `/openapi.json` | Free |
| 2 | Python AST | FastAPI, Flask, Django | Free |
| 3 | LLM | Any language (opt-in) | ~$0.01/repo |
| 4 | Regex | Any language (fallback) | Free |

---

## Commands

```bash
# Discover routes
agora-code scan ./my-api
agora-code scan ./my-api --output routes.json
agora-code scan ./my-app --use-llm          # for non-Python repos

# Start MCP server
agora-code serve ./my-api --url http://localhost:8000
agora-code serve ./my-api --url http://localhost:8000 --auth-token mytoken123

# Stats from memory
agora-code stats ./my-api

# Configure auth
agora-code auth ./my-api
```

---

## Claude Desktop Setup

Add to `~/.config/claude/config.json`:

```json
{
  "mcpServers": {
    "my-api": {
      "command": "agora-code",
      "args": ["serve", "./my-api", "--url", "http://localhost:8000"]
    }
  }
}
```

---

## Installation Options

```bash
pip install agora-code                    # Core (OpenAPI + AST + Regex)
pip install agora-code[openai]            # LLM tier with OpenAI
pip install agora-code[gemini]            # LLM tier with Gemini
pip install agora-code[memory]            # agora-mem integration
pip install agora-code[enterprise]        # Supabase cloud backend
pip install agora-code[all]              # Everything
```

---

## Memory Layer

With `pip install agora-code[memory]`, the agent remembers every API call:

- **Before calling:** *"This endpoint failed 3x last week"*
- **After calling:** Stores result, latency, errors in SQLite
- **Pattern detection:** *"POST /orders fails 30% of the time on Fridays"*

---

## Editions

| | Community | Enterprise |
|---|---|---|
| Storage | Local SQLite | Supabase cloud |
| Multi-user | ❌ | ✅ |
| Shared catalogs | ❌ | ✅ |
| Auth (coming soon) | — | Supabase Auth / WorkOS |

---

## Supported Frameworks

| Framework | Language | Tier |
|-----------|----------|------|
| FastAPI | Python | AST |
| Flask | Python | AST |
| Django | Python | AST |
| Express, NestJS | JS/TS | LLM or Regex |
| Rails | Ruby | Regex |
| Spring Boot | Java | Regex |
| Any with `/openapi.json` | Any | OpenAPI |
