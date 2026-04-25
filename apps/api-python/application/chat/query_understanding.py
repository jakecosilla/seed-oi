import json
import logging
from typing import Dict, Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from .schemas import QueryUnderstandingResult, Intent, EntityType, ExtractedEntity
from .fallback import DegradedFallbackClassifier

logger = logging.getLogger(__name__)

class QueryUnderstandingService:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm
        self.fallback = DegradedFallbackClassifier()

    async def understand(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryUnderstandingResult:
        """
        Interprets a user query using an LLM to extract intent and entities.
        Falls back to a keyword classifier if LLM fails or is missing.
        """
        llm_type = getattr(self.llm, "_llm_type", "")
        is_mock = True
        if isinstance(llm_type, str) and llm_type and "mock" not in llm_type.lower():
            is_mock = False
        
        if not self.llm or is_mock:
            return self.fallback.classify(query)

        system_prompt = f"""
        You are a Supply Chain Intelligence specialist. Your task is to interpret user queries into a structured operational format.
        
        Handle typos, shorthand (e.g. 'inv' for inventory, 'mat' for material, 'po' for purchase order), and synonyms.
        
        Available Intents:
        {", ".join([i.value for i in Intent])}
        
        Available Entity Types:
        {", ".join([e.value for e in EntityType])}
        
        Current Context: {json.dumps(context or {})}
        
        Output MUST be a valid JSON object with the following structure:
        {{
            "normalized_query": "Rephrased query with fixed typos and expanded shorthand",
            "primary_intent": "one of the available intents",
            "secondary_intents": [],
            "entities": [
                {{
                    "entity_type": "one of the available entity types",
                    "value": "the extracted value",
                    "original_text": "text from query"
                }}
            ],
            "confidence": 0.0 to 1.0,
            "requires_clarification": boolean,
            "clarification_question": "Short narrow question if intent is truly ambiguous"
        }}
        """

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            # Extract JSON if LLM wraps it in markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            result = QueryUnderstandingResult(**parsed)
            
            # Confidence booster: if model is unsure and returns general_chat, 
            # check if our keyword fallback has a better idea.
            if result.primary_intent == Intent.GENERAL_CHAT and result.confidence < 0.7:
                fallback_result = self.fallback.classify(query)
                if fallback_result.primary_intent != Intent.GENERAL_CHAT:
                    logger.info(f"Boosting low-confidence general_chat to {fallback_result.primary_intent}")
                    return fallback_result
            
            return result
            
        except Exception as e:
            logger.error(f"LLM Query Understanding failed: {e}. Falling back to keyword classification.")
            return self.fallback.classify(query)
