# FortiManager MCP NG

`fortimanager-mcp-ng` is a maintained fork of [`rstierli/fortimanager-mcp`](https://github.com/rstierli/fortimanager-mcp). It turns the FortiManager JSON-RPC API into an MCP server so Claude Desktop, Claude Code, LM Studio, Open WebUI, and other MCP-compatible clients can manage policy packages, firewall objects, devices, scripts, templates, SD-WAN settings, and ADOM workflows through a structured tool surface.

This is an independent community project. It is not affiliated with, endorsed by, or supported by Fortinet. FortiManager is a trademark of Fortinet, Inc. This MCP server can create, modify, and delete configurations on FortiManager. Misuse or misconfiguration can impact production networks. Use at your own risk, test in a non-production environment first, and ensure appropriate ADOM permissions are configured.

## Why this fork exists

This fork keeps the upstream feature set and current upstream security fixes, while preserving the fork-specific packaging and runtime improvements needed for reliable operation:

- publishable package name and CLI entrypoint: `fortimanager-mcp-ng`
- dynamic tool execution fixed so on-demand module loading works correctly
- HTTP `/health` reports the real FMG connection state and returns `503` if disconnected
- logging setup accepts `LOG_FORMAT=json` cleanly
- packaging remains fixed for editable installs and wheel builds after renaming the distribution
- upstream script and policy safety guardrails are included
- upstream error-handling consolidation is included

## Feature overview

- firewall policy and policy-package management
- address, service, VIP, and object-group operations
- device onboarding, provisioning, and inventory workflows
- CLI script creation, execution, and result retrieval
- template and SD-WAN management helpers
- ADOM and workspace-lock operations
- built-in safety guardrails for dangerous scripts and overly permissive policies
- stdio mode for desktop MCP clients and HTTP mode for container or gateway deployments

## Requirements

- Python 3.12+
- a reachable FortiManager instance with JSON-RPC API access
- an API token or username/password with sufficient rights
- HTTPS connectivity from the host running this server to FortiManager

## Quick start

```bash
git clone https://github.com/laurentcohn/fortimanager-mcp-ng.git
cd fortimanager-mcp-ng

uv venv
source .venv/bin/activate
uv sync

cp .env.example .env
```

Minimal `.env`:

```env
FORTIMANAGER_HOST=fmg.example.local
FORTIMANAGER_API_TOKEN=replace-me
FORTIMANAGER_VERIFY_SSL=false
DEFAULT_ADOM=root
FMG_TOOL_MODE=full
LOG_LEVEL=INFO
```

Run locally:

```bash
fortimanager-mcp-ng
```

The legacy alias `fortimanager-mcp` is still installed for compatibility, but `fortimanager-mcp-ng` is the preferred command for this fork.

## Installation

### Option 1: `uv` (recommended)

```bash
git clone https://github.com/laurentcohn/fortimanager-mcp-ng.git
cd fortimanager-mcp-ng

uv venv
source .venv/bin/activate
uv sync
```

### Option 2: `pip`

```bash
git clone https://github.com/laurentcohn/fortimanager-mcp-ng.git
cd fortimanager-mcp-ng

python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 3: Docker / Compose

This repository ships a local `Dockerfile` and `docker-compose.yml`. The container is built locally from the checked-out source, so no external image registry is required.

```bash
cp .env.example .env
docker compose up --build -d
```

The bundled compose setup exposes port `8000`, mounts `./logs` and `./output`, and enables file output inside `/app/output`.

## Configuration

Create your local config from the example file:

```bash
cp .env.example .env
```

Important settings:

| Variable | Required | Purpose |
| --- | --- | --- |
| `FORTIMANAGER_HOST` | yes | Hostname or IP of the FortiManager appliance |
| `FORTIMANAGER_API_TOKEN` | recommended | Preferred authentication method |
| `FORTIMANAGER_USERNAME` / `FORTIMANAGER_PASSWORD` | optional | Alternative to token auth |
| `FORTIMANAGER_VERIFY_SSL` | no | Disable only for self-signed lab environments |
| `DEFAULT_ADOM` | no | Default ADOM if a tool call omits one |
| `FMG_TOOL_MODE` | no | `full` or `dynamic` |
| `MCP_SERVER_MODE` | no | `stdio`, `http`, or `auto` |
| `MCP_AUTH_TOKEN` | no | Bearer token for HTTP mode |
| `MCP_ALLOWED_HOSTS` | no | JSON array of allowed reverse-proxy host headers |
| `FMG_ALLOWED_OUTPUT_DIRS` | no | Comma-separated allowlist for file-writing tools |
| `FMG_SCRIPT_SAFETY` | no | `strict` or `disabled` for dangerous CLI command blocking |
| `FMG_POLICY_SAFETY` | no | `strict`, `warn`, or `disabled` for permissive policy blocking |

### Tool modes

| Mode | What loads | When to use it |
| --- | --- | --- |
| `full` | all registered tools | default and easiest option |
| `dynamic` | discovery surface plus on-demand execution | useful when context budget matters |

Dynamic mode is fixed in this fork. If you want the most straightforward behavior, keep `FMG_TOOL_MODE=full`.

### Safety guardrails

The current upstream safety guardrails are integrated in this fork and are enabled by default.

#### Script content safety

`FMG_SCRIPT_SAFETY=strict` blocks dangerous CLI commands such as:

- `execute factory-reset`
- `execute reboot`
- `execute shutdown`
- `execute format`
- `execute erase-disk`

Set `FMG_SCRIPT_SAFETY=disabled` only if you explicitly want to allow such commands.

#### Policy permissiveness safety

`FMG_POLICY_SAFETY=strict` blocks overly permissive firewall policies where:

- `srcaddr=all`
- `dstaddr=all`
- `action=accept`

Available modes:

- `strict`: block the operation
- `warn`: allow it, but return a warning
- `disabled`: allow it without guardrails

### File output security

This fork is secure by default for write operations:

- read and query tools work without any output directory configuration
- tools that write files require `FMG_ALLOWED_OUTPUT_DIRS`
- writes outside the configured allowlist are rejected

For Docker, the bundled compose file mounts `./output` and sets `FMG_ALLOWED_OUTPUT_DIRS=/app/output`.

## Running the server

### Stdio mode

Use stdio mode when Claude Desktop or another MCP client launches the server directly:

```bash
fortimanager-mcp-ng
```

or:

```bash
python -m fortimanager_mcp
```

### HTTP mode

Use HTTP mode for Docker, reverse proxy, or remote gateway deployments:

```bash
MCP_SERVER_MODE=http fortimanager-mcp-ng
```

Health check:

```bash
curl http://localhost:8000/health
```

Typical healthy response:

```json
{
  "status": "healthy",
  "service": "fortimanager-mcp-ng",
  "fortimanager_connected": true,
  "tool_mode": "full"
}
```

If the FortiManager connection is unavailable, `/health` returns HTTP `503` with `status: "degraded"`.

## Claude Desktop

Example Claude Desktop config entry:

```json
{
  "mcpServers": {
    "fortimanager-ng": {
      "command": "/absolute/path/to/fortimanager-mcp-ng/.venv/bin/fortimanager-mcp-ng",
      "env": {
        "FORTIMANAGER_HOST": "fmg.example.local",
        "FORTIMANAGER_API_TOKEN": "replace-me",
        "FORTIMANAGER_VERIFY_SSL": "false",
        "DEFAULT_ADOM": "root",
        "FMG_TOOL_MODE": "full",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Claude Code

Example `~/.claude/mcp_servers.json` entry:

```json
{
  "mcpServers": {
    "fortimanager-ng": {
      "command": "/absolute/path/to/fortimanager-mcp-ng/.venv/bin/fortimanager-mcp-ng",
      "env": {
        "FORTIMANAGER_HOST": "fmg.example.local",
        "FORTIMANAGER_API_TOKEN": "replace-me",
        "FORTIMANAGER_VERIFY_SSL": "false",
        "DEFAULT_ADOM": "root",
        "FMG_TOOL_MODE": "full",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Security notes

- store API tokens in `.env` or a secrets backend, never in source control
- keep SSL verification enabled in production whenever possible
- use least-privilege FMG accounts
- protect `.env` files with restrictive permissions such as `chmod 600 .env`
- set `MCP_AUTH_TOKEN` when exposing the HTTP endpoint beyond localhost
- rely on ADOM locking and change windows for write-heavy automation

## Testing

Development install:

```bash
pip install -e '.[dev]'
```

Run the non-integration suite:

```bash
FORTIMANAGER_HOST=test-fmg.example.com \
FORTIMANAGER_API_TOKEN=dummy \
DEFAULT_ADOM=root \
pytest -m "not integration"
```

Current validated fork status:

- `312 passed`
- `39 deselected`

## Upstream, versioning, and support

- upstream project: [`rstierli/fortimanager-mcp`](https://github.com/rstierli/fortimanager-mcp)
- current upstream base integrated in this fork: `v1.2.1-beta`
- fork package version tracks the integrated upstream line with an `-ng` suffix
- license: [MIT](LICENSE)
