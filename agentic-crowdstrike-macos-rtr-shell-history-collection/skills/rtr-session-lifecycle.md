# rtr-session-lifecycle

**Phase:** collect (open at start, close at end)

**Purpose:** Open, extract identifiers for, and cleanly close CrowdStrike Falcon RTR batch sessions against a validated macOS host.

## Skill Instructions

```text
RTR Session Lifecycle

You manage the RTR batch session that every collection command runs inside. A session is
a live channel to the endpoint — open it late, close it promptly.

Tenant & transport
Use tools.falconpy.call_command, base URL https://api.us1.crowdstrike.com.

Open a session

Call BatchInitSessions:

params:
  body:
    host_ids: ["<AID>"]
    queue_offline: false
queue_offline: false — we only collect from hosts that are online right now. Do not
queue commands for later delivery.

A successful init returns HTTP 201. Anything else is a failure — report and stop.

Extract identifiers

From the init response extract:
batch_id — passed to every BatchCmd / BatchAdminCmd call
session_id — the per-host session inside the batch
Return both. Every later phase needs them.

Session hygiene
RTR sessions expire after a period of inactivity (~10 minutes). Keep the collection
phase moving; do not idle.

If a later command fails with a session/timeout error, the session has expired — report
it so the phase can be re-run, rather than silently continuing.

Close a session
When collection and cleanup are complete, call RTR_DeleteSession for the session.
Never leave a session open. Closing is mandatory even on the failure path.

Output (fill these fields of the shared schema)
phase: "session"
success: true if init returned 201 and both IDs were extracted
batch_id, session_id: the extracted identifiers
summary: one line — session opened/closed, or the error

```
