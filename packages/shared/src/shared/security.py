"""Security hardening, prompt injection detection, and input sanitization utilities."""

import re
from typing import Any, Dict, List, Optional
from shared.exceptions import ValidationError
from shared.logging import get_logger

logger = get_logger(__name__)

# Prompt injection adversarial patterns from docs/SECURITY.md
BLOCKED_PROMPT_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+(?:an?\s+)?unrestricted",
    r"forget\s+(?:everything|all\s+prior)",
    r"jailbreak\s+mode",
    r"bypass\s+all\s+safety\s+filters",
    r"disregard\s+the\s+above\s+instructions",
]


def check_prompt_injection(text: str) -> tuple[bool, Optional[str]]:
    """Check text for known prompt injection and adversarial jailbreak patterns."""
    if not text:
        return False, None

    lower_text = text.lower()
    for pattern in BLOCKED_PROMPT_PATTERNS:
        match = re.search(pattern, lower_text, re.IGNORECASE)
        if match:
            matched_phrase = match.group(0)
            logger.warning("Prompt injection pattern detected", pattern=matched_phrase)
            return True, f"Potentially malicious input pattern detected: '{matched_phrase}'"

    return False, None


def validate_user_prompt(text: str, min_length: int = 3, max_length: int = 10000) -> str:
    """Validate user prompt for length and injection patterns."""
    if not text or len(text.strip()) < min_length:
        raise ValidationError(f"Prompt must be at least {min_length} characters long")
    if len(text) > max_length:
        raise ValidationError(f"Prompt exceeds maximum length of {max_length} characters")

    is_injection, msg = check_prompt_injection(text)
    if is_injection:
        raise ValidationError(msg or "Invalid input prompt detected")

    return sanitize_text(text, max_length=max_length)


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Remove control characters and null bytes from text."""
    if not text:
        return ""
    # Strip null bytes and control chars (except standard newlines/tabs)
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned.strip()


def is_safe_filename(filename: str) -> bool:
    """Validate filename against directory traversal attacks."""
    if not filename:
        return False
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        return False
    # Check for reserved characters
    if any(c in filename for c in '<>:"|?*\x00'):
        return False
    return True


def sanitize_log_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redact sensitive keys from dictionary data."""
    sensitive_keys = {
        "api_key", "secret", "password", "token", "authorization",
        "access_token", "refresh_token", "secret_key", "credential",
    }

    def _sanitize_val(key: str, val: Any) -> Any:
        if any(s in key.lower() for s in sensitive_keys):
            return "[REDACTED]"
        if isinstance(val, dict):
            return {k: _sanitize_val(k, v) for k, v in val.items()}
        if isinstance(val, list):
            return [_sanitize_val(key, item) if isinstance(item, dict) else item for item in val]
        return val

    return {k: _sanitize_val(k, v) for k, v in data.items()}
