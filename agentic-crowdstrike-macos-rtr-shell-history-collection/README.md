# RTR macOS Shell History Collection (Agentic)

Fully agentic RTR collection of macOS shell/script command history. A Tracecat workflow drives a CrowdStrike RTR agent that validates the host, opens a session, discovers and collects shell-history artifacts with chain of custody, produces a structured forensic analysis (secret values redacted), cleans up, and closes the session.

## Blog Post

[Outsourcing the IR playbook: an agentic AI workflow that runs macOS shell-history forensics via CrowdStrike RTR](https://stickyricebytes.com/posts/rtr-shell-history-collection-agentic/)

## Structure

```
rtr-macos-shell-history-agentic/
├── README.md
├── workflow.yaml              # The Tracecat workflow definition
└── skills/
    ├── rtr-device-validation.md
    ├── rtr-session-lifecycle.md
    ├── rtr-shell-history-discovery.md
    ├── rtr-chain-of-custody.md
    └── rtr-cleanup.md
```

## Workflow Trigger Inputs

| Input | Description |
|---|---|
| `Hostname` | Target macOS device name as seen in CrowdStrike |
| `Requester` | Name or email of whoever is triggering the workflow |
| `Reason` | Investigation reason or ticket reference |
| `SlackChannel` | Slack channel ID for status messages (bot must already be added) |

## Pre-requisites

- Tracecat instance
- CrowdStrike Falcon API client with RTR permissions
- Slack app with `chat:write` (optional, for status messages)
- Agent preset (`rtr-shell-history-collector`) configured with the system prompt and `tools.falconpy.call_command` on the allowlist
- The five skills below added to the preset

## Skills

| Skill | Phase | Purpose |
|---|---|---|
| `rtr-device-validation` | validate | Resolve hostname to AID, confirm macOS + online |
| `rtr-session-lifecycle` | collect | Open/close the RTR batch session |
| `rtr-shell-history-discovery` | collect | Find shell/script history artifacts |
| `rtr-chain-of-custody` | collect | Hash, copy, read, zip, retrieve, analyse |
| `rtr-cleanup` | collect | Remove `/tmp/shellhist_*` files |
