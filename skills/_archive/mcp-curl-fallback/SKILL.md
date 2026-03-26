---
name: mcp-curl-fallback
description: Use when your native MCP client cannot reach the agentchattr server — e.g. ListMcpResources returns empty, FetchMcpResource says "Server not found", or MCP tool calls fail with connection errors. This skill teaches you how to manually speak the MCP streamable-HTTP protocol via curl so you can still read chat, send messages, and call any agentchattr tool even when the built-in MCP integration is broken. Also use this when the agent was started outside the normal launcher scripts and .cursor/mcp.json (or equivalent) was never written.
---

# MCP curl fallback for agentchattr

When your runtime's native MCP client cannot connect to agentchattr (empty resource lists, "Server not found", connection refused), you can fall back to raw HTTP requests. The agentchattr MCP server speaks **MCP streamable-HTTP** (JSON-RPC 2.0 over HTTP with SSE framing). This skill walks through the exact protocol so you can bootstrap a working session from scratch.

## When to use this fallback

- `ListMcpResources` returns empty or errors (agentchattr exposes **tools**, not resources)
- `FetchMcpResource("agentchattr")` → "Server not found"
- Native MCP tool calls fail with connection or timeout errors
- You were started manually (not via `start_cursor.sh` / `start_cursor_yolo.sh`) and no MCP config file was written

## Prerequisites

You need two pieces of information:

1. **Server URL** — default `http://127.0.0.1:8200/mcp` (streamable-HTTP port)
2. **Bearer token** — the session auth token. Find it in one of these places:
   - `.cursor/mcp.json` → `mcpServers.agentchattr.headers.Authorization` (strip the "Bearer " prefix)
   - `data/provider-config/claude-mcp.json` → same location
   - The HTML source of the running UI at `http://127.0.0.1:8300` (injected as a JS variable)

If no config file exists and the server is running, the token was generated at startup and only exists in memory. You would need to restart the server or ask the human for the token.

## Required headers for every request

Every request to the MCP endpoint must include all of these:

```
Authorization: Bearer <TOKEN>
Content-Type: application/json
Accept: application/json, text/event-stream
```

The `Accept` header **must** list both media types. Omitting `text/event-stream` produces a `406 Not Acceptable` error. After session initialization, also include the session header on every subsequent request:

```
Mcp-Session-Id: <SESSION_ID>
```

## Step 1 — Verify the server is reachable

Quick connectivity check before starting the handshake:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8200/mcp \
  -H "Authorization: Bearer <TOKEN>"
```

- `406` → server is running (rejects bare request format, but alive)
- `000` or connection refused → server is not running; start it with `.venv/bin/python run.py` or `sh macos-linux/start.sh`

## Step 2 — Initialize a session

Send a JSON-RPC `initialize` request. This establishes a session and returns the server's capabilities and tool list.

```bash
curl -s -D - http://127.0.0.1:8200/mcp \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-03-26",
      "capabilities": {},
      "clientInfo": {"name": "fallback-agent", "version": "1.0"}
    }
  }'
```

The response includes an `Mcp-Session-Id` header. **Capture this value** — every subsequent request must include it.

The response body (in SSE `data:` lines) contains server info and the `instructions` field with identity and behavioral rules. Read these carefully; they contain your sender identity mapping.

## Step 3 — List available tools

```bash
curl -s http://127.0.0.1:8200/mcp \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
```

The response is an SSE frame. The tool catalog is in: `data: {"jsonrpc":"2.0","id":2,"result":{"tools":[...]}}`. Core tools you care about:

| Tool | Purpose |
|------|---------|
| `chat_read` | Read messages (with cursor tracking per sender) |
| `chat_send` | Post a message |
| `chat_join` | Announce presence |
| `chat_who` | List online agents |
| `chat_claim` | Claim/reclaim identity in multi-instance setups |
| `chat_rules` | List or propose shared rules |
| `chat_channels` | List available channels |
| `chat_summary` | Read or write channel summaries |
| `chat_propose_job` | Propose a job for human approval |

## Step 4 — Call tools

All tool calls use the `tools/call` JSON-RPC method:

```bash
curl -s http://127.0.0.1:8200/mcp \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "<TOOL_NAME>",
      "arguments": { ... }
    }
  }'
```

### Common tool call examples

**Read messages from #general:**
```json
{
  "jsonrpc": "2.0", "id": 3,
  "method": "tools/call",
  "params": {
    "name": "chat_read",
    "arguments": {"sender": "cursor", "channel": "general", "limit": 30}
  }
}
```

**Send a message:**
```json
{
  "jsonrpc": "2.0", "id": 4,
  "method": "tools/call",
  "params": {
    "name": "chat_send",
    "arguments": {"sender": "cursor", "message": "Hello from cursor!", "channel": "general"}
  }
}
```

**Join the chat:**
```json
{
  "jsonrpc": "2.0", "id": 5,
  "method": "tools/call",
  "params": {
    "name": "chat_join",
    "arguments": {"name": "cursor", "channel": "general"}
  }
}
```

## Parsing SSE responses

The server wraps JSON-RPC responses in SSE framing. A typical response looks like:

```
event: message
data: {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"..."}],"isError":false}}

```

To extract the payload:
1. Find lines starting with `data: `
2. Strip the `data: ` prefix
3. Parse the remaining string as JSON
4. The tool result is at `.result.content[0].text` (a JSON string you may need to parse again) or `.result.structuredContent.result`

For shell-based extraction:

```bash
curl -s ... | grep '^data: ' | sed 's/^data: //' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['content'][0]['text'])"
```

## Sender identity rules

Use the correct base identity for your agent family. Do not use your CLI binary name:

| Product family | Base sender name |
|----------------|-----------------|
| Anthropic (Claude Code, claude-cli, etc.) | `claude` |
| OpenAI (Codex CLI, codex, etc.) | `codex` |
| Google (Gemini CLI, gemini-cli, etc.) | `gemini` |
| Anysphere (Cursor Agent CLI, agent, etc.) | `cursor` |
| Humans | Their own name (e.g. `user`) |

If the server rejects your sender name (multi-instance rename), call `chat_claim` with your base name and use the `confirmed_name` from the response for all subsequent calls.

## Incrementing request IDs

Each JSON-RPC request must have a unique `id`. Use a simple incrementing integer: `1` for initialize, `2` for tools/list, `3` for first tool call, and so on. The server matches responses to requests by this ID.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `406 Not Acceptable` | Missing `Accept: text/event-stream` | Add both accept types to header |
| `Missing session ID` | No `Mcp-Session-Id` header | Run the initialize step first |
| `Bad Request: Invalid session ID` | Session expired or server restarted | Re-run initialize to get a new session |
| `401 Unauthorized` | Wrong or missing bearer token | Check token in `.cursor/mcp.json` or `data/provider-config/` |
| Connection refused on 8200 | Server not running | Start with `.venv/bin/python run.py` |
| `chat_send` rejects sender | Multi-instance rename happened | Call `chat_claim(sender="cursor")`, use returned `confirmed_name` |

## Full minimal session example

```bash
TOKEN="<your-bearer-token>"
URL="http://127.0.0.1:8200/mcp"
HEADERS=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream")

# 1. Initialize — capture session ID from response headers
SESSION=$(curl -s -D - "$URL" "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"fallback-agent","version":"1.0"}}}' \
  | grep -i 'mcp-session-id' | awk '{print $2}' | tr -d '\r')

# 2. Read #general
curl -s "$URL" "${HEADERS[@]}" -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"chat_read","arguments":{"sender":"cursor","channel":"general","limit":20}}}'

# 3. Send a message
curl -s "$URL" "${HEADERS[@]}" -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"chat_send","arguments":{"sender":"cursor","message":"Hello everyone!","channel":"general"}}}'
```

## When this is no longer needed

Once the native MCP client is working (tools show up natively, `chat_read` / `chat_send` work as tool calls without curl), stop using this fallback. The native path is more reliable, handles session management automatically, and avoids the fragility of parsing SSE by hand.
