# rtr-shell-history-discovery

**Phase:** collect

**Purpose:** Enumerate human users on a macOS host and discover shell, script, and REPL command-history artifacts for each, via read-only RTR commands.

## Skill Instructions

```text
RTR Shell / Script History Discovery

You enumerate users and find every shell/script command-history artifact worth
collecting. This phase uses read-only commands (ls) only — no copying yet.

Tenant & transport
Use tools.falconpy.call_command, base URL https://api.us1.crowdstrike.com.

Read-only listing uses BatchCmd. Every command needs batch_id and session_id.

IMPORTANT: RTR's ls is a cloud built-in, NOT bash. It does NOT accept -l, -a, or
-la flags (they cause error 40014 "Unrecognized flag"). Always call ls with a PATH
and NO flags.

1. Enumerate users

BatchCmd → ls /Users/ (no flags).
Exclude non-human entries: Shared, Guest, .localized, anything starting with _,
daemon, nobody, root, admin.

2. Discover history artifacts per user

For each remaining user, check each candidate path below by running ls on the FULL path
with NO flags, one path per command (e.g. ls /Users/<u>/.zsh_history). A path that exists
returns its entry (including size); a missing path returns not-found — that is normal,
record only the files that exist. Listing the full file path directly is the reliable way
to find dotfiles.


Artifact
Path
Value
Zsh history
/Users/<u>/.zsh_history
Default macOS shell
Zsh sessions
/Users/<u>/.zsh_sessions/
Per-terminal history; survives history -c
Bash history
/Users/<u>/.bash_history
Older shell / scripts
Bash sessions
/Users/<u>/.bash_sessions/
Per-terminal bash history
sh history
/Users/<u>/.sh_history
Fallback shell
Fish history
/Users/<u>/.local/share/fish/fish_history

If fish installed
Python REPL
/Users/<u>/.python_history
Interactive python one-liners
Zsh rc
/Users/<u>/.zshrc
Detect anti-forensics config
Bash rc
/Users/<u>/.bashrc, /Users/<u>/.bash_profile

Detect anti-forensics config

3. Anti-forensics awareness

While listing, note (for the collection/analysis phases) any signal that history was
suppressed: missing history files on an active account, zero-byte history files, or rc
files present (they may contain HISTSIZE=0, unset HISTFILE, setopt HIST_IGNORE_ALL).
Do not draw conclusions here — just make sure the rc files are captured for analysis.

Output (fill these fields of the shared schema)

phase: "discovery"
success: true if enumeration completed
users: list of human usernames
files: array of {user, path, size_bytes} for every artifact that exists
summary: one line — N files across M users


```
