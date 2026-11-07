from pydantic import BaseModel, Field
from typing import Literal


class ReviewResult(BaseModel):
    final_readme: str


class Module1(BaseModel):
    project_id: str = ""
    requirements: str = ""
    architecture: str = ""
    boilerplate: str = ""
    code: str = ""
    backend_code: str = ""
    frontend_code: str = ""
    syntax_valid: bool = False
    syntax_error: str | None = None
    report: str = ""
    review_result: ReviewResult | None = None


# Added Schemas for Cyber Intelligence Module
Severity = Literal["critical", "high", "medium", "low", "info"]


class SecurityFinding(BaseModel):
    title: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str
    line_number: int | None = None
    explanation: str
    recommendation: str
    verification_status: Literal[
        "evidence_present",
        "evidence_missing",
        "unverified",
    ] = "unverified"


class SecurityAnalysisOutput(BaseModel):
    findings: list[SecurityFinding] = Field(default_factory=list)
    summary: str = ""


class AuditInput(BaseModel):
    source_code: str


class FinalAuditReport(BaseModel):
    overall_summary: str
    security_findings: list[SecurityFinding]
    priority_actions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class Module3(BaseModel):
    project_id: str = ""
    source_code: str = ""

    security_result: SecurityAnalysisOutput | None = None
    final_report: FinalAuditReport | None = None
