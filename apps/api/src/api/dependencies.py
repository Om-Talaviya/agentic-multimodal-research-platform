from typing import Optional
from ai.gateway.model_gateway import ModelGateway
from ai.providers.gemini_web2api import GeminiWeb2APIProvider
from ai.providers.ollama import OllamaProvider
from ai.providers.openai_compatible import OpenAICompatibleProvider
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.factory import DEFAULT_GEMINI_MODEL_DEFINITIONS
from agents.orchestrator import AgentOrchestrator
from agents.registry import AgentRegistry, registry as agent_registry
from tools.registry import ToolRegistry, tool_registry
from tools.definitions.web_search import WebSearchTool, WebFetchTool
from tools.definitions.document_read import DocumentReadTool
from agents.planner.planner_agent import PlannerAgent
from agents.research.web_agent import WebResearchAgent
from agents.research.document_agent import DocumentAnalysisAgent
from agents.critic.critic_agent import CriticAgent
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)

# Global instances
_model_router: Optional[ModelRouter] = None
_model_gateway: Optional[ModelGateway] = None
_orchestrator: Optional[AgentOrchestrator] = None


async def init_providers() -> None:
    """Initialize all providers and registries."""
    global _model_router, _model_gateway, _orchestrator
    
    # Initialize Ollama provider
    ollama = OllamaProvider(base_url=settings.ollama_base_url)
    try:
        await ollama._load_models()
    except Exception as e:
        logger.warning("Failed to initialize Ollama models on startup", error=str(e))
    
    providers_llm = [ollama]
    providers_vision = [ollama]
    providers_embedding = [ollama]
    providers_reranker = []

    # Initialize Gemini Web2API provider
    if settings.gemini_web2api_base_url:
        gemini = GeminiWeb2APIProvider(
            base_url=settings.gemini_web2api_base_url,
            api_key=settings.gemini_web2api_api_key,
            default_model=settings.gemini_default_model,
        )
        try:
            await gemini._load_models()
        except Exception as e:
            logger.warning("Failed to load Gemini Web2API models on startup", error=str(e))
        providers_llm.append(gemini)
        providers_vision.append(gemini)
    
    if settings.openai_api_key:
        openai = OpenAICompatibleProvider(
            api_key=settings.openai_api_key,
            name="openai",
        )
        providers_llm.append(openai)
        providers_vision.append(openai)
        providers_embedding.append(openai)
    
    if settings.anthropic_api_key:
        anthropic = OpenAICompatibleProvider(
            api_key=settings.anthropic_api_key,
            base_url="https://api.anthropic.com/v1",
            name="anthropic",
        )
        providers_llm.append(anthropic)
    
    # Create registries and model router
    model_registry = ModelRegistry()
    provider_registry = ProviderRegistry()

    for p in providers_llm:
        provider_registry.register_llm(p)
    for p in providers_vision:
        provider_registry.register_vision(p)
    for p in providers_embedding:
        provider_registry.register_embedding(p)
    for p in providers_reranker:
        provider_registry.register_reranker(p)

    if settings.gemini_web2api_base_url:
        for model_def in DEFAULT_GEMINI_MODEL_DEFINITIONS:
            model_registry.register(model_def)

    _model_router = ModelRouter(
        model_registry=model_registry,
        provider_registry=provider_registry,
    )

    _model_gateway = ModelGateway(
        router=_model_router,
        model_registry=model_registry,
        provider_registry=provider_registry,
    )
    
    # Register agents
    agent_registry.register("planner", PlannerAgent)
    agent_registry.register("web_research", WebResearchAgent)
    agent_registry.register("document_analysis", DocumentAnalysisAgent)
    agent_registry.register("critic", CriticAgent)
    
    # Register tools
    tool_registry.register(WebSearchTool())
    tool_registry.register(WebFetchTool())
    tool_registry.register(DocumentReadTool())
    
    # Create orchestrator
    _orchestrator = AgentOrchestrator(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=_model_router,
    )
    
    logger.info("Providers initialized", 
                llm_providers=[p.name for p in providers_llm],
                agents=list(agent_registry._agents.keys()),
                tools=list(tool_registry._tools.keys()))


async def get_model_router() -> ModelRouter:
    if _model_router is None:
        await init_providers()
    return _model_router


async def get_model_gateway() -> ModelGateway:
    if _model_gateway is None:
        await init_providers()
    return _model_gateway


async def get_orchestrator() -> AgentOrchestrator:
    if _orchestrator is None:
        await init_providers()
    return _orchestrator


async def get_agent_registry() -> AgentRegistry:
    return agent_registry


async def get_tool_registry() -> ToolRegistry:
    return tool_registry