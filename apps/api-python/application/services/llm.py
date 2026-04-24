import os
from langchain_core.language_models.chat_models import BaseChatModel

def get_chat_model() -> BaseChatModel:
    """
    Returns the appropriate ChatModel based on environment variables.
    Provider agnostic implementation.
    """
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    
    if provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        except ImportError:
            pass
            
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"))
        except ImportError:
            pass

    # Fallback mock model that just echoes to avoid breaking if dependencies aren't installed
    # In a real system, this would be an actual LLM requirement
    from langchain_core.messages import AIMessage
    class MockChatModel(BaseChatModel):
        @property
        def _llm_type(self) -> str:
            return "mock-chat-model"
            
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            from langchain_core.outputs import ChatResult, ChatGeneration
            
            # Simple mock logic based on the last message
            last_msg = messages[-1].content.lower() if messages else ""
            
            if "policy" in last_msg or "sop" in last_msg:
                intent = "rag_lookup"
            elif "inventory" in last_msg or "risk" in last_msg or "short" in last_msg or "run out" in last_msg:
                intent = "inventory_risk"
            elif "delay" in last_msg or "late" in last_msg or "po" in last_msg:
                intent = "po_delay"
            elif "health" in last_msg or "protect" in last_msg:
                intent = "health"
            elif "refresh" in last_msg or "changed" in last_msg:
                intent = "refresh"
            elif "compare" in last_msg or "scenario" in last_msg:
                intent = "scenario_compare"
            else:
                intent = "general_chat"
                
            mock_json = f'{{"normalized_query": "{last_msg}", "intent": "{intent}", "entities": {{}}}}'
            msg = AIMessage(content=f"```json\n{mock_json}\n```")
            return ChatResult(generations=[ChatGeneration(message=msg)])
            
    return MockChatModel()
