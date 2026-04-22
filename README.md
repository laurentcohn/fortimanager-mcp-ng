# FortiManager MCP NG

`fortimanager-mcp-ng` is a maintained fork of [`rstierli/fortimanager-mcp`](https://github.com/rstierli/fortimanager-mcp). It turns the FortiManager JSON-RPC API into an MCP server so Claude Desktop, Claude Code, LM Studio, Open WebUI, and other MCP-compatible clients can manage policy packages, firewall objects, devices, scripts, templates, SD-WAN settings, and ADOM workflows through a structured tool surface.

This project is not affiliated with, endorsed by, or supported by Fortinet. FortiManager is a trademark of Fortinet, Inc.

## Why this fork exists

This fork keeps the upstream feature set but fixes a few issues that block real use and publishing:

- publishable package name and CLI entrypoint: `fortimanager-mcp-ng`
- dynamic tool execution fixed so tool modules load correctly on demand
- HTTP `/health` now reports the real FMG connection state and returns `503` if disconnected
- logging setup accepts `LOG_FORMAT=json` cleanly
- packaging fixed so editable installs and wheel builds work after renaming the distribution
- version metadata aligned between package files

## Feature overview

- firewall policy and policy-package management
- address, service, VIP, and object-group operations
- device onboarding, provisioning, and inventory workflows
- CLI script creation, execution, and result retrieval
- template and SD-WAN management helpers
- ADOM and workspace-lock operations
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

The included compose setup exposes port `8000`, mounts `./logs` and `./output`, and enables file output inside `/app/output`.

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

### Tool modes

| Mode | What loads | When to use it |
| --- | --- | --- |
| `full` | all registered tools | default and easiest option |
| `dynamic` | discovery surface plus on-demand execution | useful when context budget matters |

Dynamic mode is fixed in this fork. If you want the most straightforward behavior, keep `FMG_TOOL_MODE=full`.

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

Current fork status:

- `270 passed`
- `39 deselected`

## What changed compared with upstream

- dynamic execution now imports the correct tool modules at runtime
- health reporting is accurate for both MCP and HTTP surfaces
- packaging and install metadata work under the renamed `-ng` distribution
- logging config is more robust in local and CI environments

## Upstream, license, and support

- upstream project: [`rstierli/fortimanager-mcp`](https://github.com/rstierli/fortimanager-mcp)
- this fork started from upstream commit `78ac3d3`
- license: [MIT](LICENSE)

Small, reviewable fixes are intentional so cherry-picking changes upstream remains easy.
