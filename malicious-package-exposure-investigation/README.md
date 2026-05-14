# 🧪 Malicious Package Exposure Investigation

> Fan out a malicious-package advisory to Sourcegraph (code) and CrowdStrike Falcon (endpoints) in parallel via MCP, then collapse both results into a Tracecat case and a Slack summary.

---

## 📋 Overview

This workflow answers a single question: **are we exposed to this compromised package?**

When a new supply-chain advisory drops, the workflow takes a package name and affected versions and runs two scoped investigations in parallel:

- **Code side** — Sourcegraph MCP searches manifests, lockfiles, and imports across repositories.
- **Endpoint side** — CrowdStrike Falcon MCP searches software inventory, NGSIEM events, file paths, processes, and network indicators on devices.

Both branches converge into a single Tracecat case and a short Slack summary.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| 🪢 **Parallel investigation** | Code and endpoint searches run concurrently — no waiting for sequential agents |
| 🔌 **MCP-driven** | Sourcegraph and Falcon are reached through their MCP servers, called by a single Tracecat preset agent |
| 📚 **Evidence-backed reporting** | Agent is prompted to extract IOCs, plan searches, classify findings, and cite evidence |
| 🗃️ **Case as source of truth** | Full agent outputs (tool calls, repos hit, hostnames, evidence) land in the Tracecat case |
| 💬 **Concise Slack notification** | Short, stakeholder-facing mrkdwn summary with a link back to the case |
| 🚫 **Exposure only, not response** | No auto-quarantine, no PRs, no isolation — read, classify, report |

---

## 🚀 Prerequisites

### Infrastructure

| Requirement | Notes |
|-------------|-------|
| Tracecat instance | Self-hosted or cloud-hosted |
| Sourcegraph instance | Any plan that supports access tokens |
| CrowdStrike Falcon | API client with read scopes for Hosts, Detections, NGSIEM/Event Search, and Software/Application Inventory |
| Slack workspace *(optional)* | Bot with `chat:write`, added to the target channel |

### MCP Integrations

Both MCP servers run as custom MCP integrations in Tracecat. Auth is passed in as custom environment variables on the integration.

**Sourcegraph MCP** — see [sourcegraph.com/docs/api/mcp](https://sourcegraph.com/docs/api/mcp)

```json
{"Authorization": "token YOUR_SOURCEGRAPH_TOKEN"}
```

Generate the token from Sourcegraph → User settings → Access tokens. The `token ` prefix is required by Sourcegraph's auth scheme.

**Falcon MCP** — see [github.com/CrowdStrike/falcon-mcp](https://github.com/CrowdStrike/falcon-mcp)

```bash
FALCON_CLIENT_ID="your-client-id"
FALCON_CLIENT_SECRET="your-client-secret"
FALCON_BASE_URL="https://api.crowdstrike.com"
```

`FALCON_BASE_URL` needs to match your Falcon region:
- US-1: `https://api.crowdstrike.com`
- US-2: `https://api.us-2.crowdstrike.com`
- EU-1: `https://api.eu-1.crowdstrike.com`

### Agent Preset

Create a Tracecat preset named `malicious-package-exposure-investigator` with:

- The system prompt from the [blog post](https://stickyricebytes.com/posts/malicious-package-exposure-investigation/) (or your adapted version)
- The Sourcegraph MCP and Falcon MCP attached as **Allowed MCP integrations**
- Internet access enabled if you want the agent to fetch advisories from URLs

---

## 📥 Installation

### Step 1: Import the Workflow

Download `malicious-package-exposure-investigation.yaml` and import into Tracecat:

```
Tracecat → Workflows → Import → Select YAML file
```

### Step 2: Configure the MCP Integrations

Add the Sourcegraph MCP and Falcon MCP integrations in Tracecat with the env vars above.

### Step 3: Create the Agent Preset

Create the `malicious-package-exposure-investigator` preset and attach both MCP integrations as tools. Paste in the system prompt from the blog post.

### Step 4: Update Workflow Variables

| Variable | Location | Update To |
|----------|----------|-----------|
| Slack channel ID | `post_to_slack.args.channel` | Your channel ID (placeholder is `XXXX`) |
| Tracecat workspace URL | `post_to_slack` blocks | Your Tracecat workspace ID (placeholder is `X` in the case link) |
| `preset` | `search_sourcegraph` and `search_falcon` | Your preset name if you renamed it |

### Step 5: Run an Advisory

In the `search_sourcegraph` and `search_falcon` actions, update the `Affected packages:` block in each `user_prompt`. The YAML ships with an example:

```yaml
Affected packages:
@tanstack/history: 1.161.9, 1.161.12
```

Everything else (extraction, planning, classification, output formatting) lives in the preset, so this is the only thing you change between advisories.

---

## 🏗️ Workflow Structure

```
┌────────────────────────────┐   ┌────────────────────────────┐
│  search_sourcegraph        │   │  search_falcon             │
│  ai.preset_agent           │   │  ai.preset_agent           │
│  Sourcegraph MCP only      │   │  Falcon MCP only           │
└────────────┬───────────────┘   └───────────────┬────────────┘
             │                                   │
             └─────────────┬─────────────────────┘
                           ▼
              ┌────────────────────────────┐
              │  create_case               │
              │  core.cases.create_case    │
              │  join_strategy: all        │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  generate_slack_summary    │
              │  ai.action (formatter)     │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  post_to_slack             │
              │  tools.slack.post_message  │
              └────────────────────────────┘
```

| Ref | Action type | Job |
|-----|-------------|-----|
| `search_sourcegraph` | `ai.preset_agent` | Search code repos for references to the malicious package |
| `search_falcon` | `ai.preset_agent` | Search endpoint telemetry for install/exec evidence |
| `create_case` | `core.cases.create_case` | Persist both reports as a Tracecat case |
| `generate_slack_summary` | `ai.action` | Compose a concise Slack summary |
| `post_to_slack` | `tools.slack.post_message` | Post the summary with a link back to the case |

---

## 🧠 Why one preset, two scoped branches?

Both branches call the same preset because the *reasoning* is identical: given a package name and version, look for evidence in your data source and report findings with enough context that a human can verify them.

The thing that differs is *which* data source, and that's enforced at call time by the user prompt:

- `search_sourcegraph` prompt starts with `SCOPE: Sourcegraph code search ONLY. Do NOT use Falcon or endpoint tools.`
- `search_falcon` prompt starts with `SCOPE: CrowdStrike Falcon endpoint search ONLY. Do NOT use Sourcegraph or code search tools.`

Splitting into two scoped branches (vs. one agent doing both jobs) is a time optimisation — long advisories with many packages run noticeably faster in parallel.

---

## 🔧 Swappable Tooling

Nothing in this workflow is religious about the tooling. The pattern is "fan out a single question to a code source and an endpoint source, then merge." Swap as needed:

| Branch | Swap with |
|--------|-----------|
| Sourcegraph (code) | Any code/repo search tool with an MCP server or API |
| Falcon (endpoints) | Any EDR with software inventory + event search via MCP or API |
| Slack | Microsoft Teams, email, PagerDuty, etc. |

The shape generalises to any "is X present anywhere in our environment?" question — binary hashes, leaked credential prefixes, vulnerable library versions, IOC domains.

---

## 📚 Tutorial

The design choices, preset system prompt, and end-to-end walkthrough are covered in the accompanying blog post:

[Checking Supply Chain Exposure in Parallel with Sourcegraph, CrowdStrike, and Tracecat](https://stickyricebytes.com/posts/malicious-package-exposure-investigation/)

---

## 🐛 Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Agent claims "no exposure" with no searches performed | Preset prompt missing or tools not attached | Re-check the preset's Allowed MCP integrations and system prompt |
| Sourcegraph MCP returns 401 | Token missing `token ` prefix or expired | Re-issue token from Sourcegraph → Access tokens; ensure header is `token XX` |
| Falcon MCP returns 403 on inventory queries | API client missing read scopes | Grant Hosts, Detections, NGSIEM/Event Search, and Software/Application Inventory |
| Slack action posts to the wrong channel | Placeholder `channel: XXXX` not updated | Update `post_to_slack.args.channel` to your channel ID |
| Case link in Slack is broken | Workspace placeholder `workspaces/X` not updated | Update the workspace ID in the Slack `blocks` context element |

---

## 📄 License

MIT — see repo root.
