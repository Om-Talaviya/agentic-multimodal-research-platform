# Security

## Principles

- **Defense in depth**: Multiple layers of protection
- **Least privilege**: Minimum permissions for each component
- **Fail secure**: Secure by default, explicit allow
- **No secrets in code**: All secrets via environment variables
- **Audit everything**: Structured logging for security events

## Secrets Management

```bash
# .env.example - committed to repo
# .env - NEVER committed, created locally

# Model providers
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/research

# Vector store
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Redis
REDIS_URL=redis://localhost:6379/0

# Search API (optional)
SEARCH_API_URL=https://api.search.com
SEARCH_API_KEY=...

# Application
SECRET_KEY=generate-with-openssl-rand-base64-32
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# File upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800  # 50MB
```

```python
# packages/shared/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Model providers
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    
    # Database
    database_url: str
    
    # Vector store
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Search
    search_api_url: str | None = None
    search_api_key: str | None = None
    
    # App
    secret_key: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Upload
    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 50 * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Input Validation

```python
# All API inputs validated with Pydantic
from pydantic import BaseModel, Field, validator
from typing import Optional

class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=10, max_length=5000)
    context: Optional[str] = Field(None, max_length=10000)
    constraints: list[str] = Field(default_factory=list, max_length=20)
    preferred_sources: list[str] = Field(default_factory=list, max_length=10)
    
    @validator('question')
    def validate_question(cls, v):
        # Block prompt injection attempts
        blocked_patterns = [
            "ignore previous instructions",
            "system prompt",
            "you are now",
            "forget everything",
        ]
        lower = v.lower()
        for pattern in blocked_patterns:
            if pattern in lower:
                raise ValueError("Invalid input detected")
        return v
```

## File Upload Security

```python
# apps/api/src/services/upload_service.py
import magic
from pathlib import Path
from packages.shared.config import settings

ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
    "image/webp",
}

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp"}

def validate_upload(file: UploadFile, content: bytes) -> tuple[bool, str]:
    """Validate uploaded file."""
    
    # Check file size
    if len(content) > settings.max_upload_size:
        return False, f"File too large (max {settings.max_upload_size} bytes)"
    
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed: {ext}"
    
    # Check MIME type (magic bytes)
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file content: {mime}"
    
    # Check for malicious content (basic)
    if b"<script" in content.lower() or b"eval(" in content.lower():
        return False, "Potentially malicious content detected"
    
    return True, "OK"

async def save_upload(file: UploadFile, job_id: str | None = None) -> Path:
    """Save validated upload to secure location."""
    content = await file.read()
    valid, msg = validate_upload(file, content)
    if not valid:
        raise ValidationError(msg)
    
    # Create job-specific directory
    subdir = job_id or "unassigned"
    upload_dir = settings.upload_dir / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Use secure filename
    import uuid
    safe_name = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    file_path = upload_dir / safe_name
    
    file_path.write_bytes(content)
    return file_path
```

## Tool Permission Boundaries

```python
# packages/tools/base.py
from enum import Enum

class Permission(str, Enum):
    WEB_ACCESS = "web_access"
    DOCUMENT_ACCESS = "document_access"
    FILE_SYSTEM_READ = "file_system_read"
    FILE_SYSTEM_WRITE = "file_system_write"
    CODE_EXECUTION = "code_execution"  # Dangerous - disabled by default
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"

# Tools declare required permissions
class WebSearchTool(Tool):
    permissions = [Permission.WEB_ACCESS]

class DocumentReadTool(Tool):
    permissions = [Permission.DOCUMENT_ACCESS]

class CodeExecutionTool(Tool):
    permissions = [Permission.CODE_EXECUTION]  # Requires explicit enable
```

## Agent Sandboxing

```python
# packages/agents/base.py
class AgentContext:
    def __init__(self, ..., permissions: set[Permission] = None):
        self.permissions = permissions or {Permission.WEB_ACCESS, Permission.DOCUMENT_ACCESS}
    
    def get_tool(self, name: str) -> Tool | None:
        tool = tool_registry.get(name)
        if tool and tool.permissions:
            # Check if agent has required permissions
            if not all(p in self.permissions for p in tool.permissions):
                raise PermissionError(f"Agent lacks permission for tool: {name}")
        return tool
```

## Rate Limiting

```python
# apps/api/src/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request, FastAPI

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/research")
@limiter.limit("10/minute")
async def create_research(request: Request, ...):
    ...
```

## Logging Security

```python
# packages/shared/logging.py
import structlog
from packages.shared.config import settings

def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from logs."""
    sensitive_keys = {
        "api_key", "secret", "password", "token", "authorization",
        "credit_card", "ssn", "private_key"
    }
    
    def _sanitize(obj):
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if any(s in k.lower() for s in sensitive_keys) else _sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        return obj
    
    return _sanitize(data)

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        lambda _, __, event_dict: sanitize_log_data(event_dict),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
)
```

## CORS

```python
# apps/api/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Dev only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Future: Authentication

```python
# packages/shared/auth.py (placeholder for Phase 6)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate JWT token
    # Return user object
    pass

# Apply to routes:
# @app.post("/api/v1/research", dependencies=[Depends(get_current_user)])
```

---

*Security is an ongoing process. Review and update regularly.*