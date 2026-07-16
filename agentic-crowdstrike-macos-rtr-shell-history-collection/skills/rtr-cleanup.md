# rtr-cleanup

**Phase:** collect

**Purpose:** Remove temporary shell-history evidence from a macOS host after RTR retrieval and confirm /tmp is clean, then close the RTR session.

## Skill Instructions

```text
RTR Cleanup

You remove every temporary artifact this collection created and confirm the host is left
clean. Cleanup runs only after the evidence zip has been retrieved to Falcon cloud —
never delete before retrieval is confirmed.

Tenant & transport

Use tools.falconpy.call_command, base URL https://api.us1.crowdstrike.com.

rm uses BatchAdminCmd; ls uses BatchCmd (path only, no flags). Needs batch_id/session_id.

Procedure

1. Remove copied history files

For each /tmp/shellhist_<user>_<artifact> created during collection:
BatchAdminCmd → rm "/tmp/shellhist_<user>_<artifact>".

2. Remove the evidence zip

BatchAdminCmd → rm "/tmp/shellhist_<CASE>_<UTC>.zip".

3. Confirm clean

BatchCmd → ls /tmp/ (no flags — RTR ls rejects -l/-a). Confirm no shellhist_
entries remain. If any survive, report cleanup_confirmed=false and name them — do not
claim success.

Only ever remove files this workflow created under /tmp with the shellhist_ prefix.
Never remove original user history files or anything outside that prefix.

4. Close the session

Hand back to the session-lifecycle skill to call RTR_DeleteSession. The session must be
closed once cleanup is confirmed.

Output (fill these fields of the shared schema)
phase: "cleanup"
success: true if all temp files removed and session closed
cleanup_confirmed: true only if ls /tmp/ shows no shellhist_* remaining
summary: one line — cleaned N files, session closed

```
