import os
import json
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.messages import AIMessage, BaseMessage

def get_chat_model() -> BaseChatModel:
    """
    Returns the appropriate ChatModel based on environment variables.
    Focused strictly on model transport and provider selection.
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

    return MockChatModel()

class MockChatModel(BaseChatModel):
    """
    A minimal fallback transport that returns fixed or echo responses.
    Does NOT contain business logic or intent classification.
    """
    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"
        
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        last_msg = messages[-1].content if messages else ""
        
        # If it looks like a structured request (JSON), return a generic but valid JSON block
        if "json" in messages[0].content.lower() or "json" in last_msg.lower():
             # Return a generic response that allows the system to continue, 
             # but doesn't encode business logic here.
             content = json.dumps({
                 "normalized_query": last_msg,
                 "primary_intent": "general_chat",
                 "confidence": 0.5,
                 "requires_clarification": False,
                 "entities": [],
                 "steps": [], # For planning
                 "content": f"Mock AI response to: {last_msg[:50]}..."
             })
        else:
             content = f"Mock response to: {last_msg}"
             
        msg = AIMessage(content=content)
        return ChatResult(generations=[ChatGeneration(message=msg)])

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        return self._generate(messages, stop, **kwargs)
