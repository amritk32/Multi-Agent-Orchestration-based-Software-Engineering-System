import re


def validate_generated_source(source: str, file_kind: str) -> None:
    """Reject only backend/frontend layer leakage during generation."""
    if file_kind == "backend":
        javascript_markers = re.search(
            r"(?i)(\b(?:const|let|var|function)\b|=>|\binterface\s+\w+|"
            r"\btype\s+\w+\s*=|\bimport\s+\{[^}]+\}\s+from\b|console\.log)",
            source,
        )
        if javascript_markers:
            raise ValueError(
                "Generated backend file contains JavaScript or TypeScript "
                f"syntax ({javascript_markers.group(0)}); backend code must be Python."
            )

    if file_kind == "backend":
        forbidden = re.search(
            r"(?i)(<!doctype\s+html|<html|<script|import\s+react|from\s+react|"
            r"document\.getelementbyid|frontend_html|createelement|window\.)",
            source,
        )
    else:
        forbidden = re.search(
            r"(?i)(from\s+(?:flask|fastapi|django)|import\s+(?:flask|fastapi|django)|"
            r"@app\.(?:route|get|post|put|delete)|sqlalchemy|\bBaseModel\b|"
            r"uvicorn\.run|create_engine|sessionmaker)",
            source,
        )

    if forbidden:
        raise ValueError(
            f"Generated {file_kind} file contains code belonging to the "
            f"other application layer ({forbidden.group(0)})."
        )
