import os
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.messages import AIMessage, BaseMessage

def get_chat_model() -> BaseChatModel:
    """
    Returns the appropriate ChatModel based on environment variables.
    Provider agnostic implementation.
    """
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    
    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=os.getenv("OLLAMA_MODEL", "llama3"), 
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        except ImportError:
            # Fallback to community if ollama package is older
            try:
                from langchain_community.chat_models import ChatOllama
                return ChatOllama(
                    model=os.getenv("OLLAMA_MODEL", "llama3"), 
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                )
            except ImportError:
                pass
            
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"))
        except ImportError:
            pass

    # Fallback mock model that just echoes to avoid breaking if dependencies aren't installed
    class MockChatModel(BaseChatModel):
        @property
        def _llm_type(self) -> str:
            return "mock-chat-model"
            
        def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
            last_msg = messages[-1].content.lower() if messages else ""
            intent = self._classify_intent(last_msg)
            mock_json = f'{{"normalized_query": "{last_msg}", "intent": "{intent}", "entities": {{}}}}'
            msg = AIMessage(content=f"```json\n{mock_json}\n```")
            return ChatResult(generations=[ChatGeneration(message=msg)])

        async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
            return self._generate(messages, stop, **kwargs)

        def _classify_intent(self, last_msg: str) -> str:
            if "policy" in last_msg or "sop" in last_msg: return "rag_lookup"
            if "inventory" in last_msg or "risk" in last_msg or "short" in last_msg or "run out" in last_msg: return "inventory_risk"
            if "delay" in last_msg or "late" in last_msg or "po" in last_msg: return "po_delay"
            if "health" in last_msg or "protect" in last_msg: return "health"
            if "refresh" in last_msg or "changed" in last_msg: return "refresh"
            if "compare" in last_msg or "scenario" in last_msg: return "scenario_compare"
            return "general_chat"
            
    return MockChatModel()
