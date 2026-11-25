# Composio App Research & Integration Intelligence Pipeline
> **Automated 100-App Research Agent, 3-Pass Verification Engine & Product Ops Intelligence Case Study**  
> *Prepared for the Composio AI Product Operations Role*

[![Dataset: 100 Apps](https://img.shields.io/badge/Dataset-100%20Apps-orange.svg)](site/data.json)
[![Verified Accuracy: 97%](https://img.shields.io/badge/Verified%20Accuracy-97.0%25-brightgreen.svg)](#accuracy-progression--verification-proof)
[![MCP Whitespace: 85%](https://img.shields.io/badge/MCP%20Whitespace-85%25-blue.svg)](#key-patterns--product-ops-takeaways)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Executive Summary

Composio turns apps into production-grade tools and Model Context Protocol (MCP) servers for AI agents. Before engineering a toolkit for an app, Product Operations must answer key buildability questions:
1. **What authorization flow is used?** (OAuth2, API key, Basic, JWT, Bearer token)
2. **What is the credential acquisition friction?** (Self-serve developer signup vs. paid plan vs. enterprise partner gate)
3. **What is the API surface?** (Public REST / GraphQL breadth, SDKs, or local CLI)
4. **Is there an existing MCP server?** (Official, community, or net-new whitespace)
5. **Buildability verdict:** Can an agent toolkit be built today, or what is the primary blocker?

This repository contains the autonomous research and multi-pass verification pipeline that analyzed **100 customer-requested apps** across 10 categories, clustered operational patterns, surfaced the massive MCP whitespace, and generated a single, self-explanatory executive case study.

---

## Key Patterns & Product Ops Takeaways

1. **OAuth2 and API Key Dominate the Protocol Landscape**
   - **OAuth2** (69 apps) and **API Key** (67 apps) represent over **85%** of target apps.
   - Dual-auth support is standard among enterprise SaaS (e.g., Salesforce, HubSpot, Stripe, Notion), supporting both user-interactive OAuth2 and headless machine-to-machine tokens.
2. **High Immediate Velocity: 71% Self-Serve Rate**
   - **71 of 100 apps** offer instantaneous developer signups, free sandboxes, or zero-cost trials.
   - Immediate sprint targets: CRM (HubSpot, Linear, Attio), Developer Platforms (Vercel, Netlify, Supabase, Cloudflare), and Productivity (Notion, ClickUp, Asana).
3. **Massive MCP Whitespace: 85% Unbuilt**
   - Only **15 of 100 apps** have documented official or community MCP servers on GitHub.
   - **85% whitespace** establishes Composio's strategic opportunity to serve as the default managed MCP gateway for AI agent developers.
4. **Operational Bottleneck is Credential Access, Not API Complexity**
   - Only **9%** of target apps lack remote APIs (e.g., local CLIs like Sherlock or closed apps like fanbasis).
   - The primary blocker for the remaining unbuilt apps is **administrative gating** (partner outreach or paid tier procurement), not protocol engineering.

---

## Accuracy Progression & Verification Proof

A critical requirement of the assignment is demonstrating **how verification loops caught agent errors and lifted accuracy**.

```
Pass 1 Raw LLM Extraction (56.0% accuracy)
    │
    ▼ [Automated Verifier: HTTP status check, subpath probing, keyword corroboration]
Pass 2 Deep Verification (97.0% accuracy, 51 corrections logged)
    │
    ▼ [Pass 3: Stratified 15-app spot-check across all categories]
Pass 3 Human Audit (100.0% agreement on 15 sampled apps)
```

### The DealCloud Case Study: Ground-Truth Auth Detection
During early pilot runs, raw LLM search grounding returned `API Key` only for **DealCloud (#10)**. Human inspection of the actual developer documentation at `api.docs.dealcloud.com/docs/token` revealed that DealCloud implements an **OAuth2 Client Credentials flow generating a 15-minute Bearer token** for subsequent authenticated calls.

To prevent this class of hallucination across all 100 apps:
1. We engineered **Method 1+3 Live Page Parsing** into the pipeline.
2. The agent probes live documentation endpoints and common subpaths (`/docs/token`, `/docs/apikeys`, `/authentication`).
3. Extracted body text is corroborated against signal lexicons for OAuth2, Bearer tokens, and Basic auth before finalizing the record.

### Automated Correction Audit Trail (Sample from 51 Diffs)
| App | Field Corrected | Pass 1 Raw Output | Pass 2 Verified Output | Grounding Corroboration Reason |
| :--- | :--- | :--- | :--- | :--- |
| **DealCloud** (#10) | `auth_methods` | `['API Key']` | `['API Key', 'Basic Auth', 'OAuth2', 'Bearer Token']` | Live page at `api.docs.dealcloud.com/docs/token` explicitly documents OAuth2 Client Credentials flow. |
| **HubSpot** (#2) | `evidence_url` | `.../docs/api/intro` (404) | `.../docs/api/overview` (200) | Automated verifier caught 404 dead link and repaired with canonical verified developer docs. |
| **Twenty** (#5) | `auth_methods` | `['API Key', 'Bearer Token']` | `['API Key', 'Bearer Token', 'OAuth2']` | Discovered OAuth2 authorization flow in live developer documentation. |
| **Stripe** (#81) | `access_tier` | `Partner / Contact-Sales Gated` | `Self-Serve Free/Trial` | Corrected hallucinated enterprise gate; Stripe offers instant self-serve `sk_test_...` keys with zero verification. |
| **Slack** (#21) | `access_tier` | `Partner / Contact-Sales Gated` | `Self-Serve Free/Trial` | Corrected access tier; free Slack workspaces provide immediate Slack App & Bot OAuth2 token provisioning. |
| **Sherlock** (#58) | `buildability_verdict` | `Easy Win — Build Today` | `Local CLI / OSS (No API)` | Corrected to local open-source Python tool; not a hosted cloud REST API. |
| **Firecrawl** (#56) | `mcp_status` | `None Found` | `Official MCP` | Identified official open-source repository `mendableai/firecrawl-mcp-server`. |

---

## Architecture & Project Structure

```
composio-app-research/
├── agent/
│   ├── __init__.py
│   ├── models.py          # Pydantic v2 schemas: AppResearchRecord, VerificationDiff, HumanAuditRow
│   ├── researcher.py      # Pass 1: Async research agent with live page parsing & checkpointing
│   ├── verifier.py        # Pass 2: Automated URL check, subpath probing & MCP registry cross-check
│   ├── human_audit.py     # Pass 3: Stratified 15-app audit generator with verified human notes
│   └── patterns.py        # Clustering, metric computation & Product Ops queue generator
├── data/
│   ├── apps_100.json           # Static seed input (100 apps across 10 categories)
│   ├── pass1_checkpoint.jsonl  # Append-only resume checkpoint
│   ├── pass1_raw.json          # Pass 1 raw output (100 records)
│   ├── pass2_verified.json     # Pass 2 verified dataset (100 records)
│   ├── verification_diff.json  # 51 logged automated corrections
│   ├── human_audit.json        # 15 stratified spot-checks with human verdicts
│   └── patterns.json           # Aggregated distributions, insights & queues
├── site/
│   ├── index.html         # Single self-contained executive case study page (148 KB)
│   ├── data.json          # Machine-readable verified dataset (100 records)
│   └── llms.txt           # Agent-readable summary for LLM context injection
├── build_site.py          # Jinja2 builder injecting data into site/
├── run_pipeline.py        # CLI entrypoint for running individual passes or full suite
├── requirements.txt       # Dependencies: google-genai, httpx, playwright, pydantic, jinja2, rich
└── README.md              # Project documentation and reproduction guide
```

---

## How to Run the Research Agent

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key (`GEMINI_API_KEY`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/composio-app-research.git
cd composio-app-research

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Install Playwright Chromium browser for headless scraping fallback
playwright install chromium
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
COMPOSIO_API_KEY=your_composio_api_key_here  # Optional: enables Composio catalog integration
```

### 4. Running the Pipeline

#### Quick Test: Run Pass 1 on First 5 Apps
```bash
python run_pipeline.py --batch 5
```

#### Run Pass 1 on All 100 Apps (with Checkpointing & Resume)
```bash
python run_pipeline.py --all
```
*Note: The pipeline checkpoints to `data/pass1_checkpoint.jsonl`. If interrupted, re-running `--all` seamlessly resumes from the last completed app without re-billing tokens.*

#### Run Pass 2: Automated Verification & Diffs Logging
```bash
python run_pipeline.py --verify
```

#### Run Pass 3: Stratified Human Audit
```bash
python run_pipeline.py --audit-template
```

#### Compute Patterns & Product Ops Queues
```bash
python run_pipeline.py --patterns
```

#### Build the Single-Page Executive Deliverable (`site/index.html`)
```bash
python run_pipeline.py --build-site
```

#### Or Run the Entire Pipeline End-to-End
```bash
python run_pipeline.py --all --verify --audit-template --patterns --build-site
```

---

## Deploying the Live Case Study

The generated `site/` folder contains everything required for immediate zero-build deployment:
- `site/index.html`: Fully self-contained single-page dashboard with Chart.js charts, responsive design, interactive search/filter matrix, diffs log, and CSV/JSON export.
- `site/data.json`: Full 100-app dataset.
- `site/llms.txt`: Machine-readable executive summary.

### GitHub Pages (Recommended)
1. Push this repository to GitHub.
2. In your repo settings, navigate to **Settings > Pages**.
3. Under **Build and deployment > Source**, select **Deploy from a branch**.
4. Choose `main` branch and `/site` folder.
5. Click **Save**. Your site will be live at `https://<username>.github.io/<repo-name>/`.

### Vercel / Netlify
- Set the publish directory to `site/`. No build command is needed.

---

## Deliverables Checklist

- [x] **100 Apps Researched:** Category, auth methods, access tier, API surface, MCP status, buildability verdict, blocker, evidence URL.
- [x] **Clustered Patterns:** Auth dominance, self-serve vs. gated breakdown, MCP whitespace, operational queues.
- [x] **Autonomous Agent Implementation:** Async Gemini pipeline with live page parsing (Method 1+3) and resume checkpointing.
- [x] **Verifiable Accuracy Loops:** Pass 1 raw (56%) → Pass 2 automated verification (97%, 51 diffs logged) → Pass 3 stratified human audit (100% agreement on 15 apps).
- [x] **Single-Page Executive Deliverable:** Clean, responsive, interactive dashboard at `site/index.html`.
- [x] **Machine-Readable Exports:** `site/data.json` and `site/llms.txt`.
- [x] **Transparent Process Journal:** Detailed operational iteration log documenting real-world pilot surprises (DealCloud OAuth2) and architectural responses.
