from pydantic import BaseModel, Field
from typing import Literal


class ReviewResult(BaseModel):
    final_readme: str


class Module1(BaseModel):
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


class StaticFinding(BaseModel):
    title: str
    severity: Severity
    rule_id: str
    source_tool: str
    line_number: int | None = None
    evidence: str = ""
    message: str


class StaticAnalysisOutput(BaseModel):
    findings: list[StaticFinding] = Field(default_factory=list)
    syntax_valid: bool
    tools_completed: list[str] = Field(default_factory=list)
    tool_errors: list[str] = Field(default_factory=list)


class ComplexityFinding(BaseModel):
    function_name: str
    line_number: int
    cyclomatic_complexity: int
    assessment: str
    recommendation: str


class ComplexityAnalysisOutput(BaseModel):
    findings: list[ComplexityFinding] = Field(default_factory=list)
    total_functions: int = 0
    summary: str = ""


class AuditInput(BaseModel):
    source_code: str


class FinalAuditReport(BaseModel):
    overall_summary: str
    security_findings: list[SecurityFinding]
    static_findings: list[StaticFinding]
    complexity_findings: list[ComplexityFinding]
    priority_actions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class Module3(BaseModel):
    source_code: str = ""

    security_result: SecurityAnalysisOutput | None = None
    static_result: StaticAnalysisOutput | None = None
    complexity_result: ComplexityAnalysisOutput | None = None
    final_report: FinalAuditReport | None = None
