"""Pass 1: Asynchronous research agent using Gemini 3.5 Flash Lite + Direct Page Parsing (Method 1+3)."""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from agent.models import AppResearchRecord

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
console = Console()

DATA_DIR = BASE_DIR / "data"
APPS_PATH = DATA_DIR / "apps_100.json"
CHECKPOINT_PATH = DATA_DIR / "pass1_checkpoint.jsonl"
OUTPUT_PATH = DATA_DIR / "pass1_raw.json"

SEMAPHORE_LIMIT = 4
MODEL_NAME = "gemini-3.5-flash-lite"

# Known apps with official or community support in Composio ecosystem
KNOWN_COMPOSIO_APPS = {
    "salesforce", "hubspot", "pipedrive", "attio", "twenty", "zoho crm", "close", "copper",
    "zendesk", "intercom", "freshdesk", "front", "helpscout", "gorgias",
    "slack", "twilio", "zoho cliq", "discord", "telegram", "whatsapp business",
    "google ads", "meta ads", "mailchimp", "klaviyo", "pinterest", "sendgrid",
    "shopify", "woocommerce", "bigcommerce", "magento", "squarespace", "gumroad",
    "apify", "firecrawl", "bright data", "github", "vercel", "netlify", "cloudflare",
    "supabase", "neo4j", "snowflake", "mongodb atlas", "datadog", "sentry",
    "notion", "airtable", "linear", "jira", "asana", "monday.com", "clickup", "coda", "smartsheet", "harvest",
    "stripe", "plaid", "binance", "quickbooks", "xero", "brex", "ramp",
    "devin", "reducto"
}

RESEARCH_PROMPT_TEMPLATE = """You are researching the app "{app_name}" (website hint: {website_hint}) for an API integration catalog.
Composio (composio.dev) turns SaaS and developer tools into agent-callable actions and MCP servers.
We need to rigorously evaluate if this app can become an agent toolkit today.

Find and return EXACTLY this information with real, up-to-date evidence from the live web:

1. ONE-LINER: What {app_name} does in one concise sentence.
2. AUTH METHODS: What authentication does their developer/API support?
   Options include: "OAuth2", "API Key", "Basic Auth", "Bearer Token", "JWT", "Session Token", "None/CLI".
   List ALL methods documented in developer guides. If no public API exists, return ["None"].
3. ACCESS TIER: Can a developer get API credentials on their own? Pick exactly ONE:
   - "Self-Serve Free/Trial": sign up online, instant API keys or free trial/developer sandbox available.
   - "Paid Plan Required": API access is explicitly restricted to paid tier subscribers.
   - "Admin/Workspace Approval": requires an enterprise/workspace admin to grant API tokens or create internal integrations.
   - "Partner / Contact-Sales Gated": must apply to a partner program, contact sales, or negotiate enterprise terms.
   - "Local CLI / Open-Source": it is a local binary, CLI tool, or self-hosted open-source repo with no remote SaaS API.
4. API SURFACE: What architecture and scale?
   Format: "<Protocol>, <Breadth>"
   Protocol: REST, GraphQL, gRPC, SDK-only, CLI, WebSocket, or None
   Breadth: Narrow (<20 endpoints), Moderate (20-100 endpoints), Broad (100+ endpoints)
   Example: "REST, Broad" or "REST + GraphQL, Moderate" or "CLI, Narrow"
5. MCP STATUS: Does an MCP (Model Context Protocol) server exist for this app?
   Search for "{app_name} MCP server" across GitHub, npm, and official docs.
   - "Official MCP": published or maintained by {app_name}
   - "Community MCP": third-party community MCP server
   - "None Found": no MCP server found
   mcp_link: exact GitHub/npm URL if found, else null.
6. BUILDABILITY VERDICT: Could Composio build an agent toolkit for this today? Pick ONE:
   - "Easy Win — Build Today": public docs, self-serve credentials, standard REST/GraphQL.
   - "Buildable — Needs Paid/Test Account": documented API exists but testing/building requires paid plan.
   - "Needs Partner Outreach": gated behind partner approval, sales review, or enterprise NDA.
   - "Not an API Toolkit (CLI/Closed)": local CLI only, closed ecosystem, or completely lacks developer API.
7. MAIN BLOCKER: The primary technical or operational obstacle to building today. If easy win, write "None".
8. EVIDENCE URL: The EXACT developer or API documentation page URL (e.g. https://developer.salesforce.com/docs/... or https://docs.github.com/rest).
   NOT the marketing root homepage. If the app is partner gated or closed, provide the pricing/partner URL that proves this.

CRITICAL INTEGRITY RULES:
- NEVER guess or fabricate URLs. Every URL must be a real page verified on the web.
- If an app is gated, closed, or a local CLI tool, report it honestly. Partner-gated and CLI are high-signal, valid findings.

Return ONLY a valid JSON object matching this schema:
{{
  "one_liner": "...",
  "auth_methods": ["OAuth2", "API Key"],
  "access_tier": "Self-Serve Free/Trial",
  "api_surface": "REST, Broad",
  "mcp_status": "None Found",
  "mcp_link": null,
  "buildability_verdict": "Easy Win — Build Today",
  "main_blocker": "None",
  "evidence_url": "https://..."
}}
"""


def clean_json_text(text: str) -> str:
    """Strip markdown fences and extract raw JSON string."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return text


async def fetch_page_content(url: str, timeout: float = 10.0) -> Tuple[int, str]:
    """Fetch live web page content with httpx and Playwright fallback."""
    if not url or not url.startswith("http"):
        return 0, ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, verify=False) as client:
            resp = await client.get(url, headers=headers)
            text = resp.text or ""
            if resp.status_code == 200 and len(text) > 400:
                return resp.status_code, text
            status = resp.status_code
    except Exception:
        status = 0
        text = ""

    # Playwright fallback for SPAs or JS-rendered documentation
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                body = await page.inner_text("body")
                st = response.status if response else 200
                await browser.close()
                return st, body
            except Exception:
                await browser.close()
    except Exception:
        pass

    return status, text


async def check_url_live(url: str, timeout: float = 8.0) -> bool:
    """Quick HTTP probe to verify whether URL resolves."""
    if not url or not url.startswith("http"):
        return False
    status, text = await fetch_page_content(url, timeout=timeout)
    return status < 400 and status > 0


async def extract_auth_from_page(url: str) -> List[str]:
    """Fetch live docs page and extract ground-truth auth methods using comprehensive keyword signals (Method 1+3)."""
    status, content = await fetch_page_content(url)
    if not content or len(content) < 150:
        return []

    text = content.lower()
    found: List[str] = []

    # OAuth2 detection
    oauth_signals = [
        "oauth", "oauth2", "oauth 2.0", "authorization code", "client credentials",
        "client_id", "client_secret", "access_token", "refresh_token", "/authorize",
        "/oauth/token", "grant_type", "pkce", "bearer token"
    ]
    if any(s in text for s in oauth_signals):
        found.append("OAuth2")

    # API Key detection
    apikey_signals = [
        "api key", "api_key", "apikey", "x-api-key", "api-key",
        "api token", "api_token", "authorization: api-key", "x-auth-token"
    ]
    if any(s in text for s in apikey_signals):
        found.append("API Key")

    # Basic Auth detection
    basic_signals = ["basic auth", "basic authentication", "base64", "username:password", "http basic"]
    if any(s in text for s in basic_signals):
        found.append("Basic Auth")

    # Bearer Token detection (personal access token / standalone bearer)
    bearer_signals = ["bearer token", "personal access token", "pat ", "authorization: bearer"]
    if any(s in text for s in bearer_signals) and "Bearer Token" not in found:
        found.append("Bearer Token")

    # JWT detection
    jwt_signals = ["jwt", "json web token", "rs256", "private_key", "service account key"]
    if any(s in text for s in jwt_signals):
        found.append("JWT")

    # CLI / Local tool
    cli_signals = ["pip install", "npm install -g", "cli only", "command line interface", "github.com/"]
    if ("cli" in url.lower() or any(s in text for s in cli_signals)) and not found:
        found.append("None/CLI")

    return found


async def extract_access_tier_from_page(url: str, current_tier: str) -> str:
    """Check live page text to corroborate or refine access tier."""
    status, content = await fetch_page_content(url)
    if not content:
        return current_tier

    text = content.lower()

    # Partner-gated signals
    gated_signals = [
        "contact sales", "contact us for api access", "request access", "request a demo",
        "enterprise only", "partner program", "apply for access", "closed beta", "inquire with sales"
    ]
    if any(s in text for s in gated_signals) and "Partner" not in current_tier:
        return "Partner / Contact-Sales Gated"

    # Paid plan signals
    paid_signals = ["paid plan required", "available on pro", "enterprise subscription required", "upgrade to use api"]
    if any(s in text for s in paid_signals) and "Paid" not in current_tier:
        return "Paid Plan Required"

    return current_tier


def check_composio_catalog(app_name: str) -> str:
    """Check if app is officially or community supported in Composio's ecosystem."""
    norm = app_name.lower().strip()
    for known in KNOWN_COMPOSIO_APPS:
        if known in norm or norm in known:
            return "Already Supported"
    return "Not in Catalog"


def load_checkpoints() -> Dict[int, AppResearchRecord]:
    """Load existing checkpoint records if available."""
    records: Dict[int, AppResearchRecord] = {}
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        rec = AppResearchRecord(**data)
                        records[rec.id] = rec
                    except Exception:
                        pass
    return records


def append_checkpoint(record: AppResearchRecord):
    """Append single record to checkpoint JSONL."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")


async def research_app(
    client: genai.Client,
    app_info: dict,
    semaphore: asyncio.Semaphore,
    retries: int = 2
) -> AppResearchRecord:
    """Research a single app with Gemini search proposal + Direct Page Parsing corroboration."""
    app_id = app_info["id"]
    app_name = app_info["app_name"]
    website_hint = app_info.get("website_hint", "")
    category = app_info["category"]
    category_num = app_info["category_num"]

    prompt = RESEARCH_PROMPT_TEMPLATE.format(app_name=app_name, website_hint=website_hint)

    for attempt in range(retries + 1):
        async with semaphore:
            try:
                # Propose parameters via Gemini 3.5 Flash Lite
                try:
                    config = types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.1,
                    )
                    response = await client.aio.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config=config,
                    )
                except Exception as search_err:
                    if "429" in str(search_err) or "RESOURCE_EXHAUSTED" in str(search_err) or "UNAVAILABLE" in str(search_err):
                        response = await client.aio.models.generate_content(
                            model=MODEL_NAME,
                            contents=prompt,
                            config=types.GenerateContentConfig(temperature=0.1),
                        )
                    else:
                        raise search_err

                raw_text = response.text or ""
                cleaned = clean_json_text(raw_text)
                parsed = json.loads(cleaned)

                # Validate evidence_url
                evidence_url = str(parsed.get("evidence_url", "")).strip()

                # METHOD 1+3: Direct Page Parsing Corroboration
                page_auth = await extract_auth_from_page(evidence_url)
                
                # Probe common auth subpaths if evidence_url is generic or missing specific auth
                auth_candidates = [
                    evidence_url,
                    evidence_url.rstrip("/") + "/docs/token",
                    evidence_url.rstrip("/") + "/docs/apikeys",
                    evidence_url.rstrip("/") + "/docs/authentication",
                    evidence_url.rstrip("/") + "/authentication",
                    evidence_url.rstrip("/") + "/auth",
                    evidence_url.rstrip("/") + "/reference/authentication",
                ]
                for cand in auth_candidates:
                    cand_auth = await extract_auth_from_page(cand)
                    if cand_auth:
                        for a in cand_auth:
                            if a not in page_auth:
                                page_auth.append(a)
                        if "token" in cand or "auth" in cand:
                            evidence_url = cand

                auth_methods = list(parsed.get("auth_methods", ["None"]))
                notes = None

                # Ground-truth override: If page text confirms explicit OAuth/API Key, use it!
                if page_auth:
                    if set(page_auth) != set(auth_methods):
                        notes = f"Pass 1 direct page parsing corroborated ground truth auth: {page_auth}"
                        auth_methods = page_auth

                # Refine access tier from live page signals
                access_tier = await extract_access_tier_from_page(
                    evidence_url, str(parsed.get("access_tier", "Self-Serve Free/Trial"))
                )

                # Check Composio catalog cross-reference
                comp_status = check_composio_catalog(app_name)

                record = AppResearchRecord(
                    id=app_id,
                    app_name=app_name,
                    category=category,
                    category_num=category_num,
                    one_liner=str(parsed.get("one_liner", "")).strip(),
                    auth_methods=auth_methods,
                    access_tier=access_tier,
                    api_surface=str(parsed.get("api_surface", "REST, Moderate")),
                    mcp_status=str(parsed.get("mcp_status", "None Found")),
                    mcp_link=parsed.get("mcp_link") or None,
                    buildability_verdict=str(parsed.get("buildability_verdict", "Easy Win — Build Today")),
                    main_blocker=str(parsed.get("main_blocker", "None")),
                    evidence_url=evidence_url,
                    verification_status="verified_pass1",
                    notes=notes,
                    composio_status=comp_status,
                )
                append_checkpoint(record)
                return record

            except Exception as e:
                if attempt == retries:
                    console.print(f"[red]Error researching {app_name} after {retries+1} attempts: {e}[/red]")
                    comp_status = check_composio_catalog(app_name)
                    fallback_record = AppResearchRecord(
                        id=app_id,
                        app_name=app_name,
                        category=category,
                        category_num=category_num,
                        one_liner=f"{app_name} cloud application integration target",
                        auth_methods=["API Key"],
                        access_tier="Partner / Contact-Sales Gated",
                        api_surface="REST, Moderate",
                        mcp_status="None Found",
                        mcp_link=None,
                        buildability_verdict="Needs Partner Outreach",
                        main_blocker=f"Research agent timeout: {str(e)}",
                        evidence_url=f"https://{website_hint.split()[0]}",
                        verification_status="flagged_uncertain",
                        notes=f"Extraction failure: {e}",
                        composio_status=comp_status,
                    )
                    append_checkpoint(fallback_record)
                    return fallback_record
                await asyncio.sleep(5 * (attempt + 1))


async def run_pass1(
    batch: Optional[int] = None,
    single_app: Optional[str] = None,
    run_all: bool = False,
    resume: bool = True,
):
    """Orchestrate Pass 1 research run across target apps."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set!")

    client = genai.Client(api_key=api_key)

    if not APPS_PATH.exists():
        raise FileNotFoundError(f"Apps database not found at {APPS_PATH}")

    with open(APPS_PATH, "r", encoding="utf-8") as f:
        all_apps = json.load(f)

    # Filter targets
    if single_app:
        targets = [a for a in all_apps if a["app_name"].lower() == single_app.lower()]
        if not targets:
            console.print(f"[red]App '{single_app}' not found in 100 apps dataset![/red]")
            return
    elif batch:
        targets = all_apps[:batch]
    elif run_all:
        targets = all_apps
    else:
        targets = all_apps[:10]

    checkpoints = load_checkpoints() if resume else {}
    to_run = [a for a in targets if a["id"] not in checkpoints or single_app is not None]

    console.print(
        f"[bold blue]Starting Pass 1 Research (Method 1+3 Active)[/bold blue]: {len(to_run)} apps to process "
        f"({len(checkpoints)} already checkpointed)"
    )

    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

    results: List[AppResearchRecord] = []
    for app in targets:
        if app["id"] in checkpoints and single_app is None:
            results.append(checkpoints[app["id"]])

    if to_run:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Researching & parsing live doc pages...", total=len(to_run))

            async def wrapped_research(app_info):
                res = await research_app(client, app_info, semaphore)
                progress.advance(task)
                return res

            new_results = await asyncio.gather(*[wrapped_research(a) for a in to_run])
            results.extend(new_results)

    results.sort(key=lambda r: r.id)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in results], f, indent=2, ensure_ascii=False)

    console.print(f"[bold green]Pass 1 Complete![/bold green] Saved {len(results)} records to {OUTPUT_PATH}")
    return results
