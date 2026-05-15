# 🛡️ CrowdStrike Custom IOA → Claude Code YOLO-Mode Response

> Catch Claude Code's `--dangerously-skip-permissions` (and similar AI CLI permission-skip flags) at the endpoint, block execution, then DM the user, reply in the alerts channel, run an AI investigation, and write the whole thing up as a Tracecat case.

---

## 📋 Overview

When a user runs `claude --dangerously-skip-permissions` (YOLO mode), a CrowdStrike Custom IOA blocks the process at creation time and fires a Falcon Fusion webhook into this Tracecat workflow.

From there, the workflow runs in seconds:

1. **DMs the user** with a calm, plain-English explanation of what got blocked and why
2. **Replies in the CrowdStrike alerts Slack channel thread** so the security team has immediate visibility
3. **Runs an investigator preset agent** against Falcon (process tree, related detections, host context, IP reputation) and posts the findings as a thread reply
4. **Creates a Tracecat case** with the DM, the thread replies, and the full investigation documented end-to-end

The pattern generalises beyond Claude Code: any AI CLI permission-skip flag (Codex `--full-auto`, Gemini `--yolo`, etc.) and any EDR that supports behavioural detection + webhook response can slot into the same shape.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| 🚫 **Hard block at the endpoint** | Custom IOA prevents the process from running — not just an alert |
| 💬 **User DM in seconds** | Soft-tone explanation, the blocked command verbatim, safer alternatives, and an escape hatch to security |
| 🧵 **Thread replies, not channel noise** | Automated response + AI findings nest under the original Falcon alert |
| 🤖 **Agentic investigation** | Preset agent runs process-tree, host, related-detections, and IP-rep queries automatically |
| 🗃️ **Single Tracecat case** | DM copy, thread replies, agent findings, and detection details all stitched into one auditable artifact |
| 🪞 **Teach, don't scold** | The DM is calibrated for someone who reached for a flag for productivity reasons, not for malicious intent |

---

## 🚀 Prerequisites

### Infrastructure

| Requirement | Notes |
|-------------|-------|
| Tracecat instance | Self-hosted or cloud-hosted |
| CrowdStrike Falcon | Custom IOA + Falcon Fusion for the webhook trigger |
| Slack workspace | App with `chat:write`, `users:read`, and `users:read.email`, added to the alerts channel |
| Investigator agent preset | A Tracecat preset (e.g. `crowdstrike-investigator-agent`) with Falcon tools, AbuseIPDB, and Slack posting |

### CrowdStrike Custom IOA

Create a Custom IOA on the **Process Creation** rule type with the following behaviour:

- **Image filename regex**: matches the `claude` binary
- **Command line regex**: `.*--dangerously-skip-permissions.*`
- **Action**: `Block Execution` (use `Monitor` while rolling out)
- **Severity**: tune to your environment

### Falcon Fusion Webhook

A thin Fusion workflow with three steps:

1. **Trigger**: Detection → EPP Detection
2. **Condition**: Custom IOA rule name matches yours
3. **Action**: Call webhook → your Tracecat webhook URL with the full detection JSON payload

All response logic lives in Tracecat — Fusion just delivers the event.

### Investigator Preset

Create a Tracecat preset named `crowdstrike-investigator-agent` (or update the `preset:` value in `investigate_and_post`) with these tools attached:

- `tools.crowdstrike.list_detects`, `list_alerts`, `list_incidents`
- The full Falcon MCP toolset
- `tools.abuseipdb.lookup_ip_address`
- `tools.falconpy.call_command` (generic CrowdStrike API fallback)
- `tools.slack.post_message`

The system prompt for this preset is in the [accompanying blog post](https://stickyricebytes.com/posts/crowdstrike-custom-ioa-claude-code/).

---

## 📥 Installation

### Step 1: Import the Workflow

Download `crowdstrike-custom-ioa-claude-code.yaml` and import into Tracecat:

```
Tracecat → Workflows → Import → Select YAML file
```

### Step 2: Update Placeholders

The YAML ships with placeholders that need replacing per install:

| Placeholder | Location | Update To |
|-------------|----------|-----------|
| `@company.com` | `build_context.args.value.email` | Your corporate email domain |
| `channel: XXXX` | `reply_to_alert_thread`, `post_case_link` | Your CrowdStrike alerts channel ID |
| `channel: XXXXX` | `search_alert_message.args.params.channel` | Same channel ID |
| `channel XXXX` in agent instructions | `investigate_and_post.args.instructions` | Same channel ID |
| `workspaces/XX-/cases/` | `post_case_link` Slack block | Your Tracecat workspace ID |
| `base_url` in preset prompt | Investigator preset | Your Falcon API region (US-1/US-2/EU-1) |

### Step 3: Configure Falcon

Create the Custom IOA and the Fusion webhook workflow per the prerequisites above. Point the Fusion webhook at the Tracecat workflow's trigger URL.

### Step 4: Test

1. From a test endpoint enrolled in Falcon with the Custom IOA applied, run:
   ```bash
   claude --dangerously-skip-permissions
   ```
2. The process should be killed by Falcon.
3. The Tracecat workflow should fire, deliver the DM within seconds, and complete the investigation in 1–2 minutes.

---

## 🏗️ Workflow Structure

```
              ┌────────────────────────────┐
              │  build_context             │
              │  core.transform.reshape    │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  lookup_slack_user         │
              │  slack.lookup_user_by_email│
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  dm_user                   │
              │  slack.post_message        │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  search_alert_message      │
              │  slack_sdk.call_method     │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  find_matching_alert       │
              │  core.transform.filter     │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  reply_to_alert_thread     │
              │  slack.post_message        │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  investigate_and_post      │
              │  ai.preset_agent           │
              │  (Falcon + AbuseIPDB)      │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  create_case               │
              │  core.cases.create_case    │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  post_case_link            │
              │  slack.post_message        │
              └────────────────────────────┘
```

| Ref | Action type | Job |
|-----|-------------|-----|
| `build_context` | `core.transform.reshape` | Parse the Falcon webhook payload, extract fields downstream actions need |
| `lookup_slack_user` | `tools.slack.lookup_user_by_email` | Resolve the user's Slack user ID from `${username}@company.com` |
| `dm_user` | `tools.slack.post_message` | Send the user the friendly Security Control Notification DM |
| `search_alert_message` | `tools.slack_sdk.call_method` | Pull the last 10 messages from the CrowdStrike alerts channel |
| `find_matching_alert` | `core.transform.filter` | Pick the alert message matching this host (used for `thread_ts`) |
| `reply_to_alert_thread` | `tools.slack.post_message` | Post the "user notified" reply in the alert thread |
| `investigate_and_post` | `ai.preset_agent` | Run the CrowdStrike investigator agent, post findings in the same thread |
| `create_case` | `core.cases.create_case` | Stitch everything into one Tracecat case |
| `post_case_link` | `tools.slack.post_message` | Reply to the thread with the case link |

---

## 🧠 Design Choices

**Block at the endpoint, teach in Slack.** The Custom IOA is a hard block — the process won't run. That moment of friction (the tool won't run my command!) is what the DM converts into a teaching opportunity.

**Soft-tone DM, not a policy citation.** *"Don't worry — this is a protective measure, and your machine is safe."* The first line answers the user's first question. Three pieces of context, the blocked command verbatim, two sentences on why it matters, three numbered alternatives ordered by friction, and an escape hatch to security.

**Thread replies, not channel posts.** All automation chatter (the "user notified" confirmation, the AI investigator's findings, the case link) nests under the original Falcon alert. Keeps the alerts channel scannable.

**Evidence-first investigator agent.** The preset prompt bans speculation: *"If you cannot cite a supporting field/event from the data, do not include the statement."* No probabilistic language, no attribution without telemetry support, ask for missing identifiers rather than guess.

**One preset, multiple workflows.** The investigator preset returns a pinned JSON schema, which lets other CrowdStrike-driven workflows reuse the same agent for case creation.

---

## 🔧 Adapting

The reusable shape is:

> **endpoint detection → block the action → DM the user with context → reply in the alerts channel → run an agentic investigation → close the loop with a case**

| Component | Swap with |
|-----------|-----------|
| Custom IOA for Claude Code | Custom IOA for Codex CLI (`--full-auto`), Gemini CLI (`--yolo`), Aider, etc. |
| CrowdStrike | Any EDR with behavioural detection rules + webhook/API hooks |
| Falcon Fusion | Any webhook source that can post the detection payload to Tracecat |
| Slack | Microsoft Teams, email, PagerDuty (DM + thread mechanics adapt) |
| Investigator preset | Any vendor-specific investigator agent that returns the same JSON schema |

For each AI CLI you support, write a separate Custom IOA matching the CLI binary plus its current permission-skip flag, and tailor the DM copy per tool.

---

## 📚 Tutorial

The full design walk-through, the Custom IOA configuration, the Fusion workflow, the DM copy choices, and the investigator preset prompt are covered in the accompanying blog post:

[Preventing friendly fire from Claude Code's YOLO mode: an agentic CrowdStrike automation powered by Tracecat](https://stickyricebytes.com/posts/crowdstrike-custom-ioa-claude-code/)

---

## 🐛 Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| DM never lands | Slack user lookup failing | Confirm `${username}@company.com` matches a real Slack email; adjust construction in `build_context` if your usernames differ across systems |
| Thread reply goes to a new top-level message | `find_matching_alert` returned no rows | Confirm the alerts channel ID is correct and the Falcon alert message contains the hostname; increase the `limit` in `search_alert_message` if alerts are noisy |
| Investigator agent says "no tools available" | Preset missing tool grants | Re-check the `actions` list on `investigate_and_post` matches what the preset has access to |
| Case link 404s in Slack | Workspace ID placeholder not updated | Update `workspaces/XX-/cases/...` in `post_case_link` |
| Falcon API calls 403 from the agent | API client missing scopes | Grant read on Detections, Alerts, Incidents, Hosts, and Event Search; no write scopes needed |

---

## 📄 License

MIT — see repo root.
