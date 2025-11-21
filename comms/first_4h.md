# First 4 Hours Comms Pack — “ToolShell” (SharePoint On-Prem)

All placeholders: `{SEV}`, `{asset}`, `{date}`, `{owner}`. Update time stamps and contact lists before sending.

---

## T+0–30 | Triage Ping
**To:** IR lead, SOC lead, IT ops on-call  
**Subject:** `{SEV} Potential SharePoint on-prem compromise – triage started`

**Body (bullet-style):**
- Current state: `{asset}` SharePoint host showing ToolShell-pattern exploitation as of `{date}`.
- Suspected vector: crafted ViewState/deserialization → webshell drop → encoded PowerShell from `w3wp.exe`.
- Immediate containment: isolating `{asset}`, taking hypervisor snapshot, collecting IIS logs, Sysmon, full memory image.
- Next update: `{date}` +30 minutes (triage channel + secure chat).

---

## T+30–120 | Scoping Standups
**Cadence:** 15-minute sync each hour (T+45, T+105).  
**Invitees:** IR core, SharePoint engineer, IAM, Network ops, Comms `{owner}`.

**Running agenda checklist:**
- IOC roll-up: attacks observed, hunts run, results (paste KQL/SPL hits).
- Workstreams: containment, forensic acquisition, credential hygiene, external exposure validation.
- Open questions: service account scope, lateral movement evidence, pending approvals.
- Parking lot for exec brief: risk statement, mitigations, decisions needed.

---

## T+120–240 | Executive Brief
**Audience:** CISO, CIO, comms `{owner}`, legal.  
**Talking points:**
- Situation summary: `{asset}` compromised via ToolShell-style exploit; likelihood of token forgery and lateral movement currently `{SEV}`.
- Actions taken: patched known CVEs, searched for webshell artifacts, rotated machine keys/ValidationKey, isolated affected servers, staged patches.
- Decisions requested: approve maintenance window to redeploy farm; restrict internet exposure to SharePoint; notify partners/regulators as required.
- Next update: T+240 (or sooner if containment shifts).

---

### ASCII Decision Tree (mirrors `figures/decision-tree.png`)
```
Start
 |
 +-- Cred theft suspected? -- yes --> Rotate machine keys + app pool creds; monitor token issuance
 |                                 |
 |                                 no
 |                                 |
 +-- Egress confirmed? ---- yes --> Block destination + capture pcaps; initiate outbound IOC sweep
 |                                 |
 |                                 no
 |                                 |
 +-- Webshell found? ------ yes --> Isolate host, pull disk/memory, hunt lateral movement
                                   |
                                   no --> Continue log review + harden farm
```

