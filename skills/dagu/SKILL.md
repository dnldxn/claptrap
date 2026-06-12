---
name: dagu
description: Use when working with Dagu workflow orchestration, DAG YAML, Dagu schedules, Dagu REST API calls, Dagu MCP tools, workflow runs, queues, logs, retries, approvals, or debugging failed Dagu jobs. Consult this skill before creating, editing, operating, monitoring, or troubleshooting Dagu workflows.
---

# Dagu

Use this skill when the task involves Dagu: workflow YAML, scheduling, queues, run operations, REST API integration, MCP operation, logs, approvals, retries, or debugging failed jobs.

## What Dagu Is

Dagu is a local-first workflow orchestrator. It runs DAGs defined in YAML, starts as one self-contained binary with file-backed state, and can scale to queues, workers, distributed execution, MCP, and AI-agent steps.

Good fit:

- Replacing cron with visible DAG dependencies, logs, retries, and run history.
- Running existing scripts, CLIs, SQL, HTTP calls, containers, SSH commands, or AI agents without rewriting them.
- Giving operators Web UI/API controls for starting, stopping, retrying, approving, and inspecting jobs.

Core docs:

- Overview: https://docs.dagu.sh/overview/
- Quickstart: https://docs.dagu.sh/getting-started/quickstart
- YAML specification: https://docs.dagu.sh/writing-workflows/yaml-specification
- REST API overview: https://docs.dagu.sh/overview/api
- REST API reference: https://docs.dagu.sh/web-ui/api
- MCP tools: https://docs.dagu.sh/mcp/tools

## How It Works

- A workflow is one YAML DAG. If `name` is omitted, Dagu uses the file name.
- Steps run in `graph` mode by dependency edges (`depends`) or in `chain` mode by file order.
- A run captures status, logs, stdout/stderr, outputs, artifacts, timings, and history.
- `dagu start-all` runs Web UI, REST API, scheduler, and runtime together.
- `dagu server` runs Web UI + REST API; `dagu scheduler` handles cron and queued work.
- State is file-backed by default. No external DB/message broker required for basic use.
- Schedules use cron strings, multiple cron entries, optional `CRON_TZ`, and one-off `at` times.
- Queues provide concurrency control; omitted `queue` means a per-DAG local FIFO queue.
- Distributed mode adds coordinator + workers; worker labels can route specialized workloads.

## Authoring Defaults

Prefer these unless project conventions say otherwise:

- Use `type: graph` for new DAGs.
- Put stable `id` on every step.
- Use explicit `depends` for ordering.
- Use `dagu validate <dag.yaml>` and `dagu schema dag` instead of guessing fields.
- Use `dagu dry <dag.yaml>` before changing live workflows.
- Use `enqueue` for scheduled/operator work; use `start` for immediate/manual execution.
- Use `stdout: { artifact: path }` for large logs/reports; use `output: VAR` only for small stdout values.
- Pass env/params explicitly into sub-DAGs; do not assume inheritance.

Minimal DAG:

```yaml
type: graph
schedule: "CRON_TZ=America/Los_Angeles 0 6 * * *"
overlap_policy: skip
params:
  - name: dry_run
    type: boolean
    default: true
steps:
  - id: run_job
    run: ./scripts/job.sh --dry-run="${dry_run}"
```

## REST API Basics

Base URL defaults to `http://localhost:8080/api/v1`. Mounted deployments can change the path; fetch `GET /api/v1/openapi.json` from the live server and trust `servers[0].url`.

Headers:

```text
Accept: application/json
Content-Type: application/json
Authorization: Bearer $DAGU_API_KEY
```

Auth modes:

- API keys: `Authorization: Bearer dagu_<key>`; best for automation.
- JWT: bearer token from login.
- Basic auth: `Authorization: Basic ...`.
- No auth: local/dev only when disabled.

API key docs: https://docs.dagu.sh/server-admin/authentication/api-keys

## Key REST Endpoints

Always check live schema for exact request/response shapes: `GET /api/v1/openapi.json` or UI `/api-docs`.

| Action | Endpoint | Input variables |
| --- | --- | --- |
| Health check | `GET /api/v1/health` | none |
| Discover API schema | `GET /api/v1/openapi.json` | none |
| List DAGs | `GET /api/v1/dags` | query: `page`, `perPage`, `name`, `labels`, `sort`, `order`, `remoteNode` |
| Validate DAG YAML | `POST /api/v1/dags/validate` | body: `spec` YAML string, optional `name` |
| Read/update DAG YAML | `GET|PUT /api/v1/dags/{fileName}/spec` | path: `fileName`; PUT body: `spec` YAML string |
| Start stored DAG now | `POST /api/v1/dags/{fileName}/start` | path: `fileName`; body: `params` JSON string, optional `dagRunId`, `dagName` |
| Enqueue stored DAG | `POST /api/v1/dags/{fileName}/enqueue` | path: `fileName`; body: `params` JSON string, optional `dagName`, `queue` |
| Run inline YAML once | `POST /api/v1/dag-runs` | body: `spec` YAML string, optional `name`, `params` JSON string, `dagRunId`, `singleton`; query: `remoteNode` |
| List runs | `GET /api/v1/dag-runs` | query: `name`, `status`, `limit`, `cursor`, optional date/status filters from OpenAPI |
| Get run details | `GET /api/v1/dag-runs/{name}/{dagRunId}` | path: `name`, `dagRunId` |
| Read logs | `GET /api/v1/dag-runs/{name}/{dagRunId}/log` or `/steps/{stepName}/log` | path: `name`, `dagRunId`, optional `stepName`; query: `tail` if supported by server |
| Stop run | `POST /api/v1/dag-runs/{name}/{dagRunId}/stop` | path: `name`, `dagRunId` |
| Retry run | `POST /api/v1/dag-runs/{name}/{dagRunId}/retry` | path: `name`, `dagRunId`; body: optional new `dagRunId`, optional `stepName` if supported |
| Inspect queues | `GET /api/v1/queues` and `GET /api/v1/queues/{name}/items` | query for items: `type=queued|running`, `page`, `perPage`; path: queue `name` |
| Audit events | `GET /api/v1/event-logs` | query: `kind`, `type`, `dagName`, `dagRunId`, `attemptId`, `sessionId`, `userId`, `model`, `startTime`, `endTime`, `limit`, `offset`, `cursor` |

## Request Patterns

Start stored DAG with typed params. `params` is a JSON string payload:

```sh
curl -X POST "$DAGU_URL/api/v1/dags/nightly/start" \
  -H "Authorization: Bearer $DAGU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"params":"{\"env\":\"prod\",\"dry_run\":false}","dagRunId":"manual-20260612"}'
```

Enqueue with queue override:

```sh
curl -X POST "$DAGU_URL/api/v1/dags/nightly/enqueue" \
  -H "Authorization: Bearer $DAGU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"params":"{\"env\":\"prod\"}","queue":"default"}'
```

Validate before update:

```sh
curl -X POST "$DAGU_URL/api/v1/dags/validate" \
  -H "Authorization: Bearer $DAGU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"nightly","spec":"steps:\n  - id: hello\n    run: echo hello"}'
```

Tail root log:

```sh
curl -H "Authorization: Bearer $DAGU_API_KEY" \
  "$DAGU_URL/api/v1/dag-runs/nightly/$DAG_RUN_ID/log?tail=200"
```

## MCP Shortcut

If a Dagu MCP server is available, prefer MCP for agent-operated workflows because it exposes safer intent-level tools:

- `dagu_read` — read DAG specs/details, runs, logs, list views, references.
- `dagu_change` — preview/apply validated DAG YAML upserts.
- `dagu_execute` — start, enqueue, retry, or stop runs.

Use REST directly when integrating scripts, CI, services, or when MCP is unavailable.

## Debug Checklist

1. Read live OpenAPI: `GET /api/v1/openapi.json`.
2. Check server: `GET /api/v1/health` and `GET /api/v1/metrics`.
3. Inspect DAG spec: `GET /api/v1/dags/{fileName}/spec`; validate with `POST /api/v1/dags/validate` or `dagu validate`.
4. Inspect run detail: `GET /api/v1/dag-runs/{name}/{dagRunId}`.
5. Read root log, then failed step log.
6. Check queues: `GET /api/v1/queues` and `GET /api/v1/queues/{name}/items`.
7. Check event logs for failure/audit context.
8. Stop/retry only after identifying whether the run is active, queued, failed, waiting for approval, or pending retry.

## Links By Topic

- Scheduling: https://docs.dagu.sh/writing-workflows/scheduling
- Execution control: https://docs.dagu.sh/writing-workflows/execution-control
- Error handling: https://docs.dagu.sh/writing-workflows/error-handling
- Durable execution: https://docs.dagu.sh/writing-workflows/durable-execution
- Queues: https://docs.dagu.sh/writing-workflows/queues
- Approval gates: https://docs.dagu.sh/writing-workflows/approval
- Artifacts: https://docs.dagu.sh/writing-workflows/artifacts
- Outputs: https://docs.dagu.sh/writing-workflows/outputs
- Persistent state: https://docs.dagu.sh/writing-workflows/persistent-state
- Web UI: https://docs.dagu.sh/overview/web-ui
- Server config: https://docs.dagu.sh/server-admin/server
- API keys: https://docs.dagu.sh/server-admin/authentication/api-keys
- Webhooks: https://docs.dagu.sh/server-admin/authentication/webhooks
- Prometheus metrics: https://docs.dagu.sh/server-admin/prometheus-metrics
- Distributed workers: https://docs.dagu.sh/server-admin/distributed/workers/
