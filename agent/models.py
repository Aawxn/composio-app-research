"""Pydantic v2 data models for Composio App Research pipeline."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class AccessTier(str, Enum):
    SELF_SERVE = "Self-Serve Free/Trial"
    PAID = "Paid Plan Required"
    ADMIN = "Admin/Workspace Approval"
    PARTNER = "Partner / Contact-Sales Gated"
    LOCAL = "Local CLI / Open-Source"


class Buildability(str, Enum):
    EASY_WIN = "Easy Win — Build Today"
    NEEDS_PAID = "Buildable — Needs Paid/Test Account"
    NEEDS_PARTNER = "Needs Partner Outreach"
    NOT_API = "Not an API Toolkit (CLI/Closed)"


class MCPStatus(str, Enum):
    OFFICIAL = "Official MCP"
    COMMUNITY = "Community MCP"
    NONE = "None Found"


class VerificationStatus(str, Enum):
    PASS1 = "verified_pass1"
    CORRECTED = "corrected_pass2"
    HUMAN = "human_verified"
    FLAGGED = "flagged_uncertain"


class AppResearchRecord(BaseModel):
    id: int = Field(ge=1, le=100)
    app_name: str
    category: str
    category_num: int = Field(ge=1, le=10)
    one_liner: str
    auth_methods: List[str]
    access_tier: str
    api_surface: str
    mcp_status: str
    mcp_link: Optional[str] = None
    buildability_verdict: str
    main_blocker: str
    evidence_url: str
    verification_status: str = "verified_pass1"
    notes: Optional[str] = None
    composio_status: Optional[str] = "Not in Catalog"


class VerificationDiff(BaseModel):
    app_id: int
    app_name: str
    field_changed: str
    old_value: str
    new_value: str
    reason: str


class HumanAuditRow(BaseModel):
    app_id: int
    app_name: str
    category: str
    agent_auth: List[str]
    agent_access_tier: str
    agent_buildability: str
    agent_evidence_url: str
    human_agrees: Optional[bool] = None
    human_notes: Optional[str] = None
    selection_reason: str
