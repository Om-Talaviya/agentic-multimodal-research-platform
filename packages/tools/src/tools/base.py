"""Tool base classes and protocols."""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any, Optional
from enum import Enum


class Permission(str, Enum):
    WEB_ACCESS = "web_access"
    DOCUMENT_ACCESS = "document_access"
    FILE_SYSTEM_READ = "file_system_read"
    FILE_SYSTEM_WRITE = "file_system_write"
    CODE_EXECUTION = "code_execution"
    DATABASE_READ = "database_read"
    DATABASE_WRITE = "database_write"


class ToolParameter(BaseModel):
    """JSON Schema for tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[list[Any]] = None
    default: Any = None


class ToolSchema(BaseModel):
    """Tool definition for model consumption."""
    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)
    returns: str = "Any"
    permissions: list[Permission] = Field(default_factory=list)


class Tool(ABC):
    """Base class for tools."""
    
    schema: ToolSchema
    
    def __init__(self):
        if not hasattr(self, 'schema'):
            raise NotImplementedError("Tool must define 'schema' class attribute")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
    
    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        for param in self.schema.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.schema.name,
                "description": self.schema.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
    
    def check_permissions(self, agent_permissions: set[Permission]) -> bool:
        """Check if agent has required permissions."""
        return all(p in agent_permissions for p in self.schema.permissions)