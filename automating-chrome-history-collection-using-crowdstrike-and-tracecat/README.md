# 🔍 macOS Chrome History Collection via CrowdStrike RTR

> Automated forensic collection of Chrome browser history from macOS endpoints using CrowdStrike Real-Time Response (RTR) and Tracecat SOAR.

---

## 📋 Overview

This workflow automates the manual process of collecting Chrome browser history files from macOS devices during incident response. It handles everything from device validation to evidence packaging, maintaining chain of custody documentation throughout.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| 🖥️ **Device Validation** | Validates target device is macOS and RTR-accessible |
| 👤 **Auto-Discovery** | Discovers all user accounts and Chrome profiles automatically |
| 🔐 **Integrity Hashing** | Generates MD5, SHA1, SHA256 hashes before and after collection |
| 📦 **Evidence Packaging** | Packages evidence into timestamped ZIP archives |
| ☁️ **Secure Upload** | Uploads to CrowdStrike RTR cloud for secure retrieval |
| 🧹 **Clean Execution** | Cleans up temporary files without destroying evidence |
| 📝 **Full Audit Trail** | Documents every step in case management and Slack |

### ⏱️ Execution Time
```
Automated: ~2 minutes
Manual:    30-45 minutes
```

---

## 🚀 Prerequisites

### Infrastructure

| Requirement | Notes |
|-------------|-------|
| Tracecat instance | Self-hosted or cloud-hosted |
| CrowdStrike Falcon EDR | With RTR enabled |
| Slack workspace | For notifications |

### Credentials

Configure the following in Tracecat Secrets:

| Secret | Required Permissions |
|--------|---------------------|
| CrowdStrike API Client | `Real Time Response (Admin)` - Read/Write |
| Slack Bot Token | `chat:write` scope |

### Test Environment

- ✅ macOS device enrolled in CrowdStrike with RTR enabled
- ✅ Chrome browser installed with at least one profile
- ✅ Device must be online and in "normal" status

> ⚠️ **Warning:** This workflow creates temporary files in `/tmp` and removes them after collection. Test in a non-production environment first.

---

## 📥 Installation

### Step 1: Import the Workflow

Download `rtr-extract-chrome-browser-history.yaml` and import into Tracecat:
```
Tracecat → Workflows → Import → Select YAML file
```

### Step 2: Configure Secrets

**CrowdStrike:**
```yaml
Name: crowdstrike
Keys:
  - client_id: YOUR_CLIENT_ID
  - client_secret: YOUR_CLIENT_SECRET
```

**Slack:**
```yaml
Name: slack
Keys:
  - bot_token: xoxb-YOUR-BOT-TOKEN
```

### Step 3: Update Workflow Variables

| Variable | Location | Update To |
|----------|----------|-----------|
| Slack Channel ID | All `post_message` actions | Your channel ID  |
| Tracecat Workspace URL | Slack message blocks | Your Tracecat instance URL |
| CrowdStrike Console URL | Slack message blocks | Your Falcon console URL |

### Step 4: Test the Workflow

1. Open the workflow in Tracecat
2. Click the trigger dropdown
3. Enter a test hostname (must match CrowdStrike exactly — case-sensitive)
4. Run and monitor execution

---

## 🏗️ Workflow Structure

The workflow consists of **45 actions** across three phases:
```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Foundation & Discovery                                │
│  ─────────────────────────────────                              │
│  Create case → Query device → Validate macOS → Init RTR         │
│  → Discover users → Locate Chrome profiles                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Collection Engine                                     │
│  ──────────────────────────                                     │
│  Hash originals → Copy to /tmp → Validate copies                │
│  → Create ZIP → Hash archive → Upload to RTR cloud              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Professional Polish                                   │
│  ────────────────────────────                                   │
│  Remove temp files → Verify cleanup → Close RTR session         │
│  → Final documentation and notifications                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Tutorial Series

This workflow is documented in a three-part tutorial series:

| Part | Title | Description |
|:----:|-------|-------------|
| **1** | [Foundation & Discovery](https://stickyricebytes.com/posts/macos-chrome-forensics-part1/) | Device validation, RTR session, user discovery |
| **2** | [The Collection Engine](https://stickyricebytes.com/posts/macos-chrome-forensics-part2/) | Hashing, copying, packaging, upload |
| **3** | [Professional Polish](https://stickyricebytes.com/posts/macos-chrome-forensics-part3/) | Cleanup, session closure, final audit |

The tutorials walk through every action with explanations of **what it does**, **why it matters**, and **how to configure it**.

---

## 📤 Retrieving Collected Evidence

After successful workflow execution:

1. Open **CrowdStrike Falcon Console**
2. Navigate to `Response → Real Time Response → Session Audit Logs`
3. Find the session for your target device
4. Download the ZIP file from the **Retrieved Files** section

**ZIP filename format:**
```
case_[CASE_NUMBER]_chrome_history_collection_[YYYY-MM-DD_HH-MM-SS].zip
```

---

## 🔧 Customisation Ideas

This workflow can be extended for:

| Extension | Details |
|-----------|---------|
| **Other Browsers** | Firefox (`places.sqlite`), Safari (`History.db`), Edge |
| **Windows Endpoints** | Adjust paths for `%LocalAppData%\Google\Chrome\User Data\` |
| **Additional Artifacts** | Bookmarks, cookies, login data, extensions |
| **Notification Channels** | Microsoft Teams, email, PagerDuty |

---

## 🐛 Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Device not found | Hostname case mismatch | Verify exact hostname in CrowdStrike console |
| RTR session fails | Device offline or RTR disabled | Check device status in Falcon |
| No Chrome profiles found | Chrome not installed or different user | Verify Chrome exists for discovered user |
| Cleanup verification fails | Race condition | Increase `start_delay` on listing action |

---

## 🙏 Acknowledgements

- [Tracecat](https://tracecat.com) — Open source SOAR platform
- [CrowdStrike](https://crowdstrike.com) — RTR capabilities
- [Objective-See](https://objective-see.org) — macOS security inspiration

---

<p align="center">
  <strong>Questions?</strong> Open an issue or reach out on the <a href="https://discord.gg/tracecat">Tracecat Discord</a>.
</p>
