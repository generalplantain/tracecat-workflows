# rtr-device-validation

**Phase:** validate

**Purpose:** Resolve a macOS hostname to a CrowdStrike AID and confirm the device is eligible for RTR shell-history collection (Mac, online). Read-only.

## Skill Instructions

```text
RTR Device Validation

You validate that a target host is safe and eligible to collect from before any
RTR session is opened. This phase is read-only — it never opens a session or runs
commands on the host.

Tenant & transport

All CrowdStrike calls go through the tools.falconpy.call_command action.

Base URL: https://api.us1.crowdstrike.com 

Procedure

1. Resolve hostname → AID

Call QueryDevicesByFilter with:

params:
  filter: "hostname:'<HOSTNAME>'"

If zero devices return, set eligible=false, success=false, explain "hostname not found".
If more than one device returns, do not guess. Set eligible=false and list the
candidate AIDs in summary for a human to disambiguate.

2. Fetch device details

Call GetDeviceDetails for the single resolved AID.

3. Apply eligibility rules

Mark eligible=true only if all hold:
platform_name is Mac

status is normal (the host is online / not contained or offline)

If the host is offline, contained, or a non-Mac platform, set eligible=false and state
the exact reason. Never attempt collection on an ineligible host.

Output (fill these fields of the shared schema)
phase: "validate"
success: true if the lookup completed without error
eligible: true only if the rules above pass
device_id: the resolved AID (empty string if not resolved)
platform: e.g. "Mac 14.5"

summary: one line — what host, what AID, eligible or why not


```
