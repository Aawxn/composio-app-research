"""
Generate an executive, pixel-perfect PDF submission report for Composio AI Product Ops Intern assignment.
Optimized for 3 clean A4 pages with zero text overflows, professional typography, and clickable links.
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "pass2_verified.json", "r", encoding="utf-8") as f:
    records = json.load(f)

with open(DATA_DIR / "patterns.json", "r", encoding="utf-8") as f:
    patterns = json.load(f)

with open(DATA_DIR / "human_audit.json", "r", encoding="utf-8") as f:
    audit_rows = json.load(f)

sample_indices = [0, 1, 9, 10, 20, 21, 30, 40, 50, 55, 57, 60, 64, 70, 72, 80, 89, 95, 97]
sample_records = [records[i] for i in sample_indices]

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Composio Product Operations — Executive Report</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    @page {{
      size: A4;
      margin: 12mm 12mm 12mm 12mm;
      @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font-family: 'JetBrains Mono', monospace;
        font-size: 7.5pt;
        color: #94a3b8;
      }}
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, sans-serif;
      color: #0f172a;
      background: #ffffff;
      font-size: 8.5pt;
      line-height: 1.4;
      -webkit-font-smoothing: antialiased;
    }}

    a {{ color: #0284c7; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    .page-break {{
      page-break-after: always;
    }}

    /* Header Bar */
    .header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 2px solid #0f172a;
      margin-bottom: 12px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .brand-title {{
      font-size: 13pt;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #0f172a;
    }}
    .brand-pill {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      font-weight: 700;
      background: #ff5c35;
      color: #ffffff;
      padding: 2px 7px;
      border-radius: 4px;
      text-transform: uppercase;
    }}
    .header-sub {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      color: #64748b;
    }}

    /* Links Banner */
    .links-banner {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 3.5px solid #ff5c35;
      border-radius: 5px;
      padding: 8px 12px;
      margin-bottom: 12px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 14px;
      font-size: 8pt;
    }}
    .link-item {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .link-label {{
      font-weight: 700;
      color: #334155;
    }}
    .link-url {{
      font-family: 'JetBrains Mono', monospace;
      color: #0284c7;
      word-break: break-all;
    }}

    /* Section Styling */
    h2 {{
      font-size: 10.5pt;
      font-weight: 800;
      color: #0f172a;
      margin-top: 10px;
      margin-bottom: 6px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 3px;
    }}

    /* KPI Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 6px;
      margin-bottom: 12px;
    }}
    .kpi-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 5px;
      padding: 8px 6px;
      text-align: center;
    }}
    .kpi-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 14pt;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.1;
      margin-bottom: 2px;
    }}
    .kpi-label {{
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: #64748b;
    }}
    .kpi-desc {{
      font-size: 6.5pt;
      color: #94a3b8;
    }}

    /* Callout Card */
    .callout {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-left: 3.5px solid #16a34a;
      border-radius: 5px;
      padding: 8px 12px;
      margin-bottom: 10px;
      font-size: 8pt;
      color: #166534;
      line-height: 1.4;
    }}
    .callout-title {{
      font-weight: 700;
      font-size: 8.5pt;
      color: #14532d;
      margin-bottom: 2px;
    }}

    /* Sprints Queue */
    .queue-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .queue-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 5px;
      padding: 8px 10px;
    }}
    .queue-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }}
    .queue-title {{
      font-weight: 700;
      font-size: 8.5pt;
    }}
    .queue-count {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      font-weight: 700;
      padding: 2px 5px;
      border-radius: 3px;
    }}
    .qc-green {{ background: #dcfce7; color: #15803d; }}
    .qc-amber {{ background: #fef3c7; color: #b45309; }}
    .qc-orange {{ background: #ffedd5; color: #c2410c; }}
    .qc-blue {{ background: #e0f2fe; color: #0369a1; }}
    .queue-body {{
      font-size: 7.5pt;
      color: #475569;
      line-height: 1.35;
    }}

    /* Tables */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 7.5pt;
      margin-top: 6px;
      margin-bottom: 10px;
    }}
    th {{
      background: #f1f5f9;
      font-family: 'JetBrains Mono', monospace;
      font-size: 7pt;
      font-weight: 700;
      color: #334155;
      text-transform: uppercase;
      padding: 5px 6px;
      border: 1px solid #cbd5e1;
      text-align: left;
    }}
    td {{
      padding: 4px 6px;
      border: 1px solid #e2e8f0;
      color: #334155;
      vertical-align: middle;
    }}
    tr:nth-child(even) td {{
      background: #f8fafc;
    }}

    .tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 6.5pt;
      font-weight: 600;
      padding: 1px 4px;
      border-radius: 3px;
      display: inline-block;
      margin-right: 2px;
    }}
    .tag-oauth {{ background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; }}
    .tag-key {{ background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }}
    .tag-pass {{ background: #dcfce7; color: #15803d; font-weight: 700; }}
    .tag-fail {{ background: #fee2e2; color: #b91c1c; font-weight: 700; }}

    .email-box {{
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      border-radius: 5px;
      padding: 8px 10px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 7pt;
      color: #334155;
      line-height: 1.35;
      white-space: pre-wrap;
      margin-bottom: 10px;
    }}
  </style>
</head>
<body>

  <!-- ==================== PAGE 1: EXECUTIVE BRIEF & FINDINGS ==================== -->
  <div>
    <div class="header-bar">
      <div class="brand">
        <span class="brand-title">COMPOSIO</span>
        <span class="brand-pill">Product Operations</span>
      </div>
      <div class="header-sub">
        AI Product Ops Intern &bull; Integration Intelligence Report
      </div>
    </div>

    <!-- Live Deliverables Banner -->
    <div class="links-banner">
      <div class="link-item">
        <span class="link-label">Live Interactive Dashboard:</span>
        <a href="https://aawxn.github.io/composio-app-research/" class="link-url">https://aawxn.github.io/composio-app-research/</a>
      </div>
      <div class="link-item">
        <span class="link-label">GitHub Source Repository:</span>
        <a href="https://github.com/Aawxn/composio-app-research" class="link-url">https://github.com/Aawxn/composio-app-research</a>
      </div>
      <div class="link-item">
        <span class="link-label">Agent-Consumable JSON Data:</span>
        <a href="https://aawxn.github.io/composio-app-research/data.json" class="link-url">https://aawxn.github.io/composio-app-research/data.json</a>
      </div>
      <div class="link-item">
        <span class="link-label">Agent Specification (llms.txt):</span>
        <a href="https://aawxn.github.io/composio-app-research/llms.txt" class="link-url">https://aawxn.github.io/composio-app-research/llms.txt</a>
      </div>
    </div>

    <!-- Headline KPIs -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-num">100</div>
        <div class="kpi-label">Apps Analyzed</div>
        <div class="kpi-desc">10 Core SaaS Sectors</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-num" style="color: #16a34a;">71%</div>
        <div class="kpi-label">Self-Serve Rate</div>
        <div class="kpi-desc">Instant free/trial credentials</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-num" style="color: #0284c7;">72%</div>
        <div class="kpi-label">OAuth2 Dominance</div>
        <div class="kpi-desc">Multi-tenant auth protocol</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-num" style="color: #7e22ce;">76%</div>
        <div class="kpi-label">MCP Whitespace</div>
        <div class="kpi-desc">Unbuilt public MCP servers</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-num" style="color: #ea580c;">97.0%</div>
        <div class="kpi-label">Verified Accuracy</div>
        <div class="kpi-desc">Lifted from 56.0% raw pass</div>
      </div>
    </div>

    <!-- Executive Summary -->
    <h2>Executive Overview &amp; Autonomous Pipeline</h2>
    <p style="margin-bottom: 8px; font-size: 8pt; color: #334155;">
      Composio transforms business applications into agent-callable tools. Before developing connectors, Product Operations must research authentication protocols, credential gating friction, API breadth, and Model Context Protocol (MCP) whitespace across customer requests. Doing this manually across hundreds of apps does not scale. We designed and executed an <strong>autonomous 3-pass Product Ops pipeline</strong> that triages 100 customer-requested apps in under 15 minutes:
    </p>

    <!-- DealCloud Case Study -->
    <div class="callout">
      <div class="callout-title">Ground-Truth Auth Detection: The DealCloud (#10) Case Study</div>
      In Pass 1, initial LLM search grounding misclassified <strong>DealCloud</strong> as relying on standard <code>API Key</code> authentication.
      Direct inspection of live developer documentation (<code>api.docs.dealcloud.com/docs/token</code>) revealed that DealCloud enforces an <strong>OAuth2 Client Credentials flow</strong> generating short-lived 15-minute Bearer tokens.
      To prevent silent runtime authentication failures across all 100 connectors, our Pass 2 verification engine performs <strong>Direct Documentation Verification</strong>: fetching live HTML bodies via async HTTP and actively probing canonical endpoints (<code>/docs/token</code>, <code>/docs/apikeys</code>, <code>/authentication</code>). This caught 51 discrepancies across 44 apps, lifting accuracy from <strong>56.0% to 97.0%</strong>.
    </div>

    <!-- Strategic Takeaways -->
    <h2>Strategic Takeaways &amp; Cluster Patterns ("Insight Over Raw Table")</h2>
    <div style="font-size: 8pt; color: #334155; line-height: 1.45; margin-bottom: 10px;">
      <p style="margin-bottom: 5px;">&bull; <strong>OAuth2 (72%) &amp; API Keys (68%) Dominate:</strong> Enterprise SaaS platforms (Salesforce, Stripe, Notion, HubSpot) commonly implement dual-auth: OAuth2 for user-facing multi-tenant SaaS and API keys for server-to-server calls.</p>
      <p style="margin-bottom: 5px;">&bull; <strong>Credential Gating vs. API Complexity:</strong> The primary operational blocker is credential acquisition (enterprise sales gates, partner approvals), NOT API complexity. 78% of blocked connectors require partner outreach or paid subscriptions rather than custom protocols.</p>
      <p style="margin-bottom: 5px;">&bull; <strong>76% MCP Whitespace:</strong> Only 24 of 100 apps have documented official or community MCP servers on GitHub. By shipping managed toolkits for the 69 Easy Wins, Composio can establish immediate first-mover advantage as the default MCP gateway.</p>
      <p style="margin-bottom: 5px;">&bull; <strong>Composio Catalog Coverage:</strong> 64 of 100 apps are already supported in Composio's registry; 36 form a net-new integration backlog.</p>
    </div>

    <!-- Actionable Sprint Queues -->
    <h2>Product Operations Execution Queues</h2>
    <div class="queue-grid">
      <div class="queue-box" style="border-top: 3px solid #16a34a;">
        <div class="queue-header">
          <span class="queue-title" style="color: #15803d;">Tier 1: Immediate Easy Wins</span>
          <span class="queue-count qc-green">69 Apps</span>
        </div>
        <div class="queue-body">
          Public REST/GraphQL with instant self-serve developer access. No sales friction (Salesforce, HubSpot, Stripe, Notion, Linear, Attio, Vercel). Ready for immediate toolkit sprints.
        </div>
      </div>

      <div class="queue-box" style="border-top: 3px solid #f59e0b;">
        <div class="queue-header">
          <span class="queue-title" style="color: #b45309;">Tier 2: Sandbox Procurement</span>
          <span class="queue-count qc-amber">11 Apps</span>
        </div>
        <div class="queue-body">
          APIs are fully documented but developer account creation requires active paid subscriptions or corporate card funding (Gladly, Squarespace, Ahrefs, Clay, SE Ranking). Budget: ~$500/mo.
        </div>
      </div>

      <div class="queue-box" style="border-top: 3px solid #ea580c;">
        <div class="queue-header">
          <span class="queue-title" style="color: #c2410c;">Tier 3: Partner Outreach Required</span>
          <span class="queue-count qc-orange">9 Apps</span>
        </div>
        <div class="queue-body">
          Strictly gated behind partner applications, enterprise client agreements, or sales demos (DealCloud, PitchBook, Amazon SP-API, LinkedIn Marketing). Requires formal BD outreach.
        </div>
      </div>

      <div class="queue-box" style="border-top: 3px solid #0284c7;">
        <div class="queue-header">
          <span class="queue-title" style="color: #0369a1;">Existing MCPs to Gateway</span>
          <span class="queue-count qc-blue">24 Apps</span>
        </div>
        <div class="queue-body">
          Verified open-source or official MCP servers already built on GitHub (Sentry, Slack, GitHub, Supabase, Neon). Can be imported directly into Composio's managed execution runtime.
        </div>
      </div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== PAGE 2: VERIFICATION PROOF & AUDIT ==================== -->
  <div>
    <div class="header-bar">
      <div class="brand">
        <span class="brand-title">COMPOSIO</span>
        <span class="brand-pill">Product Operations</span>
      </div>
      <div class="header-sub">
        Verification Proof &bull; Human Audit &bull; Partner Outreach
      </div>
    </div>

    <!-- Human Audit Section -->
    <h2>Pass 3: Stratified 15-App Human Audit Sample</h2>
    <p style="font-size: 7.5pt; color: #475569; margin-bottom: 6px;">
      To verify pipeline trustworthiness, we audited a 15-app stratified sample across four risk tiers (Enterprise Gated, High-Volume SaaS, GTM/Data Tools, and Non-API Edge Cases).
      Result: <strong>12 Confirmed (80.0% Agreement) &bull; 3 Real Discrepancies Caught Manually</strong>.
    </p>

    <table>
      <thead>
        <tr>
          <th style="width: 25px;">#</th>
          <th style="width: 95px;">App Name</th>
          <th style="width: 110px;">Category</th>
          <th style="width: 110px;">Claimed Auth</th>
          <th style="width: 110px;">Access Tier</th>
          <th style="width: 75px;">Audit Status</th>
          <th>Auditor Finding &amp; Resolution</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f'''<tr>
          <td><strong>{r.get('app_id', '')}</strong></td>
          <td><strong>{r.get('app_name', '')}</strong></td>
          <td>{r.get('category', '')}</td>
          <td>{" ".join([f"<span class='tag tag-oauth'>{a}</span>" for a in (r.get('agent_auth') or [])[:2]])}</td>
          <td>{r.get('agent_access_tier', '')}</td>
          <td><span class="tag {'tag-pass' if r.get('human_agrees') else 'tag-fail'}">{'CONFIRMED' if r.get('human_agrees') else 'DISCREPANCY'}</span></td>
          <td style="font-size: 7pt;">{r.get('human_notes', '')}</td>
        </tr>''' for r in audit_rows])}
      </tbody>
    </table>

    <!-- Pre-Drafted Email Template -->
    <h2>Pre-Drafted Partner Outreach Email Template (Tier 3 Connectors)</h2>
    <div class="email-box">Subject: Partnership &amp; Agent Tooling Inquiry: Composio &times; [Target App Name]

Hi [Partner Team],

I'm reaching out from Composio (composio.dev). We build managed tool calling and agent infrastructure connecting AI agents (OpenAI Assistants, Claude Desktop, CrewAI, LangChain) to 1,500+ business applications.

Our enterprise customers have requested automated agent workflows integrating [Target App Name]. We are preparing an official connector and would like to coordinate on:
1. Developer Sandbox / API credentials for our integration engineering team
2. Scopes and OAuth application verification requirements
3. Any preferred rate limits or partnership guidelines

Could we set up a brief 15-minute sync this week to clear developer access and ensure our integration adheres to your partner standards?

Best regards,
Composio Product Operations Team</div>
  </div>

  <div class="page-break"></div>

  <!-- ==================== PAGE 3: CONNECTOR MATRIX ==================== -->
  <div>
    <div class="header-bar">
      <div class="brand">
        <span class="brand-title">COMPOSIO</span>
        <span class="brand-pill">Product Operations</span>
      </div>
      <div class="header-sub">
        Representative Connector Index &bull; All 10 Categories
      </div>
    </div>

    <h2>Representative Connector Sample Across All 10 Categories</h2>
    <p style="font-size: 7.5pt; color: #475569; margin-bottom: 6px;">
      Cross-section of the 100-app dataset detailing authentication protocols, access friction, buildability verdicts, and verified developer documentation URLs.
    </p>

    <table>
      <thead>
        <tr>
          <th style="width: 25px;">#</th>
          <th style="width: 100px;">App Name</th>
          <th style="width: 125px;">Category</th>
          <th style="width: 120px;">Auth Methods</th>
          <th style="width: 110px;">Access Tier</th>
          <th style="width: 115px;">Buildability Verdict</th>
          <th>Verified Documentation Link</th>
        </tr>
      </thead>
      <tbody>
        {"".join([f'''<tr>
          <td><strong>{r['id']}</strong></td>
          <td><strong>{r['app_name']}</strong></td>
          <td>{r['category']}</td>
          <td>{" ".join([f"<span class='tag tag-oauth'>{a}</span>" for a in (r.get('auth_methods') or [])[:2]])}</td>
          <td>{r['access_tier']}</td>
          <td>{r['buildability_verdict']}</td>
          <td style="font-family: 'JetBrains Mono', monospace; font-size: 6.5pt;"><a href="{r['evidence_url']}">{r['evidence_url'][:48]}...</a></td>
        </tr>''' for r in sample_records])}
      </tbody>
    </table>

    <!-- Local Run Instructions -->
    <h2>Local Reproducibility Instructions</h2>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 5px; padding: 8px 10px; font-family: 'JetBrains Mono', monospace; font-size: 7.5pt; color: #334155; margin-bottom: 12px;">
      git clone https://github.com/Aawxn/composio-app-research.git<br>
      cd composio-app-research<br>
      pip install -r requirements.txt<br>
      python run_pipeline.py  # Executes 3-pass pipeline and rebuilds dashboard
    </div>

    <div style="margin-top: 14px; padding: 10px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 5px; font-size: 7.5pt; color: #166534; text-align: center; font-family: 'JetBrains Mono', monospace;">
      Full 100-app interactive matrix with instant search, multi-criteria filtering, and CSV/JSON export live at:<br>
      <a href="https://aawxn.github.io/composio-app-research/" style="font-weight: 700; color: #15803d; font-size: 8.5pt;">https://aawxn.github.io/composio-app-research/</a>
    </div>
  </div>

</body>
</html>
"""

html_temp_path = BASE_DIR / "temp_report.html"
with open(html_temp_path, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

pdf_output_path = Path("c:/Users/Admin/Desktop/Composio/Composio_Product_Intern_Submission.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_temp_path.as_posix()}", wait_until="networkidle")
    page.pdf(
        path=str(pdf_output_path),
        format="A4",
        print_background=True,
        margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
    )
    browser.close()

if html_temp_path.exists():
    html_temp_path.unlink()

print(f"SUCCESS: Generated PDF at {pdf_output_path} ({pdf_output_path.stat().st_size} bytes)")
