## Commands

agora-code provides four main commands to discover, serve, monitor, and configure API integrations.

---

### `scan` - Discover API Routes

Automatically discover all API endpoints in your codebase or from a remote URL.

**What it does:**
- Scans Python codebases (FastAPI, Flask, Django) for API routes
- Extracts HTTP methods, paths, parameters, and descriptions
- Can use OpenAPI/Swagger specs if available
- Optionally uses LLM for complex codebases (Node.js, Go, etc.)
- Outputs results as table, JSON, or MCP tool definitions

**Usage:**

```bash
# Basic scan - shows table of all routes
agora-code scan ./my-api

# Scan and save to JSON file
agora-code scan ./my-api --output routes.json

# Scan remote API via URL
agora-code scan https://api.example.com

# Output as MCP tool definitions
agora-code scan ./my-api --format mcp

# Use LLM for advanced extraction (requires OpenAI/Gemini API key)
agora-code scan ./my-api --use-llm --llm-provider openai
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output, -o FILE` | Save discovered routes to JSON file | None |
| `--format FORMAT` | Output format: `table`, `json`, or `mcp` | `table` |
| `--use-llm` | Enable LLM-based extraction for non-Python codebases | `false` |
| `--llm-provider PROVIDER` | LLM provider: `openai` or `gemini` | `openai` |
| `--enterprise` | Enable enterprise edition features | `false` |

**Examples:**

```bash
# Scan FastAPI app and save to file
agora-code scan ./fastapi-app --output api-routes.json

# Scan with pretty table output
agora-code scan ./flask-app --format table

# Scan Node.js API using LLM
agora-code scan ./express-app --use-llm --llm-provider openai

# Scan and get MCP-compatible tool definitions
agora-code scan ./my-api --format mcp
```

---

### `serve` - Start MCP Server

Start a Model Context Protocol (MCP) server that exposes your API as tools for AI assistants like Claude or Cursor.

**What it does:**
- Scans your codebase for API routes
- Creates an MCP server with tools for each endpoint
- Automatically makes HTTP requests to your live API
- Optionally tracks API usage and patterns with memory layer
- Handles authentication (Bearer, API Key, Basic)
- Works with Claude Desktop, Cursor, and other MCP clients

**Usage:**

```bash
# Basic server pointing to local API
agora-code serve ./my-api --url http://localhost:8000

# Server with Bearer token authentication
agora-code serve ./my-api --url https://api.example.com --auth-token sk_live_abc123

# Server without memory layer (faster startup)
agora-code serve ./my-api --url http://localhost:8000 --no-memory

# Server with custom auth type
agora-code serve ./my-api --url https://api.example.com --auth-type api-key --auth-token mykey
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--url, -u URL` | **Required.** Base URL of your live API | None |
| `--auth-token TOKEN` | Authentication token (or set `AGORA_AUTH_TOKEN` env var) | None |
| `--auth-type TYPE` | Auth type: `bearer`, `api-key`, `basic`, or `none` | `bearer` |
| `--memory / --no-memory` | Enable/disable API call tracking and pattern detection | `true` |
| `--db-path PATH` | SQLite database path for memory storage | `./agora_agent_memory.db` |
| `--use-llm` | Use LLM for route extraction | `false` |
| `--llm-provider PROVIDER` | LLM provider: `openai` or `gemini` | `openai` |
| `--enterprise` | Enable enterprise edition features | `false` |

**Environment Variables:**

- `AGORA_AUTH_TOKEN` - Authentication token (alternative to `--auth-token`)
- `OPENAI_API_KEY` - Required if using `--use-llm` with OpenAI
- `GEMINI_API_KEY` - Required if using `--use-llm` with Gemini

**Examples:**

```bash
# Production API with authentication
agora-code serve ./my-api \
  --url https://api.production.com \
  --auth-token sk_prod_xyz789

# Local development without memory
agora-code serve ./my-api \
  --url http://localhost:3000 \
  --no-memory

# Custom database location
agora-code serve ./my-api \
  --url http://localhost:8000 \
  --db-path ~/agora-data/my-api.db

# API Key authentication
agora-code serve ./my-api \
  --url https://api.example.com \
  --auth-type api-key \
  --auth-token my_secret_key

# Using environment variable for token
export AGORA_AUTH_TOKEN=sk_live_abc123
agora-code serve ./my-api --url https://api.example.com
```

**Configuration for MCP Clients:**

Once running, configure your MCP client to connect to agora-code:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "my-api": {
      "command": "agora-code",
      "args": ["serve", "./my-api", "--url", "http://localhost:8000"],
      "env": {
        "AGORA_AUTH_TOKEN": "your-token-here"
      }
    }
  }
}
```

---

### `stats` - View API Usage Statistics

Display API call statistics, success rates, latency, and detected usage patterns from the memory layer.

**What it does:**
- Shows total calls per endpoint
- Calculates success rate (2xx responses)
- Reports average latency
- Detects usage patterns (frequent paths, error spikes, etc.)
- Analyzes historical data within a time window

**Requirements:**
- Memory layer must be enabled (default)
- Requires: `pip install agora-code[memory]`
- Needs prior API usage tracked via `serve` command

**Usage:**

```bash
# Show stats for default time window (24 hours)
agora-code stats ./my-api

# Show stats for last 48 hours
agora-code stats ./my-api --window 48

# Use custom database location
agora-code stats ./my-api --db-path ~/agora-data/my-api.db

# Show stats for last week
agora-code stats ./my-api --window 168
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--db-path PATH` | SQLite database path (must match `serve` command) | `./agora_agent_memory.db` |
| `--window HOURS` | Time window in hours for pattern detection | `24` |

**Example Output:**

```
📊 API Stats — ./my-api

  GET    /users/{user_id}                          142 calls   98% ok  45ms
  POST   /users                                      23 calls  100% ok  78ms
  GET    /products                                  456 calls   95% ok  32ms
  DELETE /users/{user_id}                            8 calls   87% ok  120ms

🔍 Patterns detected:

  • High error rate on DELETE /users/{user_id} (13% failures)
  • GET /products called frequently between 9am-5pm
  • POST /users average latency increased 2x in last 6 hours
  • /api/items endpoints not called in last 24 hours
```

**Examples:**

```bash
# Check today's API usage
agora-code stats ./my-api

# Analyze last 3 days
agora-code stats ./my-api --window 72

# Custom database from different location
agora-code stats ./my-api --db-path /var/lib/agora/production.db
```

---

### `auth` - Configure Authentication

Interactively configure or set authentication for API calls. Saves credentials to `.agora-code/auth.json`.

**What it does:**
- Creates authentication configuration for your API
- Supports multiple auth types (Bearer, API Key, Basic, None)
- Saves encrypted credentials locally
- Used automatically by `serve` command

**Usage:**

```bash
# Interactive setup (prompts for auth type and token)
agora-code auth ./my-api

# Non-interactive with Bearer token
agora-code auth ./my-api --type bearer --token sk_live_abc123

# API Key authentication
agora-code auth ./my-api --type api-key --token my_secret_key

# Basic authentication (will prompt for password)
agora-code auth ./my-api --type basic --token username

# Disable authentication
agora-code auth ./my-api --type none
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--type TYPE` | Auth type: `bearer`, `api-key`, `basic`, or `none` | Interactive prompt |
| `--token TOKEN` | Token or credential value (skips interactive prompt) | Interactive prompt |

**Auth Types:**

| Type | Description | Example |
|------|-------------|---------|
| `bearer` | Bearer token in Authorization header | `Authorization: Bearer sk_live_abc123` |
| `api-key` | API key in custom header or query param | `X-API-Key: my_secret_key` |
| `basic` | HTTP Basic authentication | `Authorization: Basic base64(user:pass)` |
| `none` | No authentication | - |

**Examples:**

```bash
# Interactive setup - prompts for details
agora-code auth ./my-api

# Quick Bearer token setup
agora-code auth ./my-api --type bearer --token sk_live_xyz789

# Remove authentication
agora-code auth ./my-api --type none

# API Key for production API
agora-code auth ./production-api --type api-key --token prod_key_456
```

**Security Notes:**

 **Important:** The auth configuration is saved to `.agora-code/auth.json`

- **Always add to `.gitignore`:**
  ```bash
  echo ".agora-code/auth.json" >> .gitignore
  ```
- Tokens are stored in plaintext - protect this file
- Consider using environment variables for production:
  ```bash
  export AGORA_AUTH_TOKEN=sk_live_abc123
  agora-code serve ./my-api --url https://api.example.com
  ```

---

## Common Workflows

### Workflow 1: Local Development

```bash
# 1. Scan your local API
agora-code scan ./my-fastapi-app

# 2. Start local API server (separate terminal)
uvicorn main:app --reload --port 8000

# 3. Start agora-code MCP server
agora-code serve ./my-fastapi-app --url http://localhost:8000 --no-memory

# 4. Connect from Claude Desktop or Cursor and start using!
```

---

### Workflow 2: Production API with Authentication

```bash
# 1. Configure authentication
agora-code auth ./my-api --type bearer --token sk_prod_xyz

# 2. Scan production API
agora-code scan ./my-api --output prod-routes.json

# 3. Start MCP server with memory enabled
agora-code serve ./my-api --url https://api.production.com

# 4. Monitor usage over time
agora-code stats ./my-api --window 168  # Last 7 days
```

---

### Workflow 3: Exploring Third-Party APIs

```bash
# 1. Create stub definitions for third-party API
mkdir github-api && cd github-api
cat > routes.py << EOF
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{username}")
def get_user(username: str): pass

@app.get("/repos/{owner}/{repo}")
def get_repo(owner: str, repo: str): pass
EOF

# 2. Serve with real GitHub API URL
agora-code serve . --url https://api.github.com

# 3. Use in Claude/Cursor to explore GitHub API
```

---

### Workflow 4: API Documentation Generation

```bash
# 1. Scan API and export as JSON
agora-code scan ./my-api --output routes.json --format mcp

# 2. Use routes.json to generate OpenAPI spec
# 3. Generate client SDKs from OpenAPI spec
# 4. Auto-generate API documentation
```

---

## Advanced Usage

### Memory and Pattern Detection

Enable memory to track API usage patterns:

```bash
# Serve with memory enabled (default)
agora-code serve ./my-api --url http://localhost:8000

# Make API calls through Claude/Cursor...

# View statistics
agora-code stats ./my-api

# View patterns over last 3 days
agora-code stats ./my-api --window 72
```

**Memory tracks:**
- Total API calls per endpoint
- Success/failure rates
- Average response latency
- Usage patterns and anomalies
- Timestamp of each call

---

### LLM-Powered Extraction

For non-Python APIs (Node.js, Go, Ruby, etc.), enable LLM extraction:

```bash
# Requires OPENAI_API_KEY or GEMINI_API_KEY environment variable
export OPENAI_API_KEY=sk-...

# Scan with LLM
agora-code scan ./express-app --use-llm --llm-provider openai

# Serve with LLM
agora-code serve ./rails-app \
  --url http://localhost:3000 \
  --use-llm \
  --llm-provider gemini
```

**When to use LLM:**
- ✅ Node.js/Express APIs
- ✅ Ruby on Rails APIs  
- ✅ Go/Gin APIs
- ✅ Complex Python frameworks (Django with custom routers)
- ❌ Standard FastAPI/Flask (unnecessary, AST extraction works great)

**Cost:** Typically $0.01-0.10 per scan depending on codebase size

---

### Enterprise Features

Enterprise edition includes:
- Advanced pattern detection
- Multi-tenant support
- Enhanced security features
- Priority support

```bash
agora-code serve ./my-api \
  --url https://api.example.com \
  --enterprise
```

---

## Troubleshooting

### No routes found

```bash
# Check what files agora-code is scanning
agora-code scan ./my-api --format json

# Try with LLM if using non-Python framework
agora-code scan ./my-api --use-llm
```

### MCP connection issues

```bash
# Test serve command manually first
agora-code serve ./my-api --url http://localhost:8000

# Should show: " MCP server ready (N tools)"
# If errors appear, check the --url is accessible
curl http://localhost:8000/health
```

### Memory/stats not working

```bash
# Install memory dependencies
pip install agora-code[memory]

# Check database exists
ls -lh agora_agent_memory.db

# Verify memory is enabled in serve command
agora-code serve ./my-api --url http://localhost:8000  # memory on by default
```

### Authentication failures

```bash
# Verify auth config exists
cat .agora-code/auth.json

# Test API manually with curl
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.example.com/endpoint

# Re-configure auth
agora-code auth ./my-api --type bearer --token NEW_TOKEN
```
