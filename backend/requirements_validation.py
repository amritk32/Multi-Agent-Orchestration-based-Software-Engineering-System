import re

_SOFTWARE_TERMS = {
    "api",
    "app",
    "application",
    "backend",
    "database",
    "dashboard",
    "frontend",
    "login",
    "platform",
    "project",
    "service",
    "website",
    "web",
}
_REQUEST_ACTIONS = {
    "build",
    "create",
    "design",
    "develop",
    "implement",
    "make",
}


def validate_requirements(requirements: str) -> str | None:
    """Return a user-facing error when input is not a meaningful software request."""
    text = " ".join(requirements.split())
    if len(text) < 12:
        return (
            "Please describe the software you want to build in more detail. "
            "Include its purpose and at least one feature."
        )

    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    if len(words) < 3:
        return (
            "Please provide clear project requirements instead of a short or "
            "incomplete input."
        )

    if not (
        _SOFTWARE_TERMS.intersection(words) or _REQUEST_ACTIONS.intersection(words)
    ):
        return (
            "Please describe a software project or an action you want the "
            "system to implement."
        )

    if " " not in text and not any(term in text.lower() for term in _SOFTWARE_TERMS):
        return (
            "That does not look like a software requirement. Please describe "
            "the application, feature, or problem you want to solve."
        )

    unique_characters = set(re.sub(r"[^a-z]", "", text.lower()))
    if len(text) >= 24 and len(unique_characters) <= 6 and " " not in text:
        return (
            "That input looks like random text. Please provide meaningful "
            "software requirements."
        )

    return None
