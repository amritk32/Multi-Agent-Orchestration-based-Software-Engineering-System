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
