from typing import Dict, Any
from .schemas import QueryUnderstandingResult, Intent, EntityType, ExtractedEntity

class DegradedFallbackClassifier:
    """
    A minimal keyword-based classifier used when the LLM is unavailable.
    Intentionally limited in scope to encourage restoration of LLM services.
    """
    
    def classify(self, query: str) -> QueryUnderstandingResult:
        q = query.lower()
        
        # Default
        intent = Intent.GENERAL_CHAT
        confidence = 0.4
        entities = []
        
        # Basic mapping - Specific intents first
        if "policy" in q or "sop" in q or "note" in q:
            intent = Intent.RAG_LOOKUP
        elif "po" in q or "delay" in q or "late" in q or "delayed" in q:
            intent = Intent.PO_DELAY
        elif "shipment" in q or "shipped" in q or "track" in q or "transit" in q or "arriving" in q:
            intent = Intent.SHIPMENT_STATUS
        elif "slow" in q or "fast" in q or "production" in q or "performance" in q or "throughput" in q or "velocity" in q or "selling" in q:
            intent = Intent.PERFORMANCE
        elif "inventory" in q or "short" in q or "run out" in q or "risk" in q or "shortage" in q:
            intent = Intent.INVENTORY_RISK
        elif "health" in q or "protected" in q or "healthy" in q:
            intent = Intent.HEALTH
        elif "available" in q or "how many" in q or "stock" in q or "material" in q or "product" in q or "item" in q or "warehouse" in q or "on hand" in q or "code" in q or "sku" in q:
            intent = Intent.INVENTORY_STATUS
        elif "scenario" in q or "compare" in q:
            intent = Intent.SCENARIO_COMPARE
            
        return QueryUnderstandingResult(
            normalized_query=query,
            primary_intent=intent,
            confidence=confidence,
            entities=entities,
            is_degraded=True
        )
