"""
ONI v11.0 - Consensus Engine
Anti-hallucination through multi-provider voting.

Requires agreement from 2/3 providers before returning coordinates.
Calculates variance to measure confidence in localization.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple
import structlog
import math

logger = structlog.get_logger(__name__)


@dataclass
class ProviderResult:
    """Result from a single grounding provider."""
    provider: str
    x: int
    y: int
    confidence: float
    found: bool
    error: Optional[str] = None


@dataclass
class ConsensusResult:
    """Result from consensus voting."""
    x: int
    y: int
    confidence: float
    variance_px: float
    consensus_reached: bool
    providers_agreed: int
    providers_total: int
    provider_results: List[ProviderResult] = field(default_factory=list)
    hallucination_check: Literal["PASSED", "FAILED", "UNCERTAIN"] = "UNCERTAIN"
    
    @property
    def is_reliable(self) -> bool:
        """Check if result is reliable (low variance, high agreement)."""
        return (
            self.consensus_reached and 
            self.variance_px < 20 and 
            self.confidence > 0.7
        )


class ConsensusEngine:
    """
    Multi-provider consensus for anti-hallucination.
    
    Uses voting mechanism to ensure coordinates are real:
    1. Query multiple grounding providers in parallel
    2. Calculate coordinate variance across providers
    3. Require minimum agreement threshold
    4. Low variance = high confidence (element exists)
    
    Example:
        engine = ConsensusEngine(providers={"omniparser": op, "uitars": ut})
        result = await engine.locate("Save button", screenshot)
        if result.hallucination_check == "PASSED":
            click(result.x, result.y)
    """
    
    def __init__(
        self,
        providers: Dict[str, any] = None,
        min_agreement: int = 2,
        max_variance_px: float = 30.0,
        timeout_seconds: float = 10.0,
    ):
        """
        Initialize Consensus Engine.
        
        Args:
            providers: Dict of provider_name -> provider_instance
            min_agreement: Minimum providers that must agree
            max_variance_px: Maximum allowed coordinate variance
            timeout_seconds: Timeout for provider queries
        """
        self._providers = providers or {}
        self._min_agreement = min_agreement
        self._max_variance_px = max_variance_px
        self._timeout = timeout_seconds
        
        # Stats
        self._consensus_hits = 0
        self._consensus_misses = 0
    
    def register_provider(self, name: str, provider: any) -> None:
        """Register a grounding provider."""
        self._providers[name] = provider
        logger.info("consensus_provider_registered", provider=name)
    
    async def locate(
        self,
        query: str,
        screenshot: bytes,
        screen_size: Tuple[int, int] = (1920, 1080),
        providers: Optional[List[str]] = None,
        frame_hash: Optional[str] = None
    ) -> ConsensusResult:
        """
        Locate element using multi-provider consensus.
        
        Args:
            query: Natural language description of element
            screenshot: PNG screenshot bytes
            screen_size: Screen dimensions
            providers: Specific providers to use (or all if None)
            frame_hash: Optional dHash for coordinate/inference caching
            
        Returns:
            ConsensusResult with coordinates and confidence
        """
        # Determine which providers to use
        provider_names = providers or list(self._providers.keys())
        if not provider_names:
            logger.warning("no_providers_available")
            return ConsensusResult(
                x=0, y=0, confidence=0, variance_px=float('inf'),
                consensus_reached=False, providers_agreed=0, providers_total=0,
                hallucination_check="FAILED"
            )
        
        # Query all providers in parallel
        tasks = []
        for name in provider_names:
            if name in self._providers:
                task = self._query_provider(name, query, screenshot, screen_size, frame_hash=frame_hash)
                tasks.append(task)
        
        # Wait for results with timeout
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        valid_results: List[ProviderResult] = []
        all_results: List[ProviderResult] = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error("provider_exception", error=str(result))
                continue
            if isinstance(result, ProviderResult):
                all_results.append(result)
                if result.found and result.error is None:
                    valid_results.append(result)
        
        # Calculate consensus
        return self._calculate_consensus(valid_results, all_results)
    
    async def _query_provider(
        self,
        name: str,
        query: str,
        screenshot: bytes,
        screen_size: Tuple[int, int],
        frame_hash: Optional[str] = None
    ) -> ProviderResult:
        """Query a single provider with timeout."""
        provider = self._providers.get(name)
        if not provider:
            return ProviderResult(
                provider=name, x=0, y=0, confidence=0,
                found=False, error="Provider not found"
            )
        
        try:
            # Apply timeout
            result = await asyncio.wait_for(
                self._invoke_provider(provider, query, screenshot, screen_size, frame_hash=frame_hash),
                timeout=self._timeout
            )
            
            if result:
                return ProviderResult(
                    provider=name,
                    x=result.get("x", 0),
                    y=result.get("y", 0),
                    confidence=result.get("confidence", 0.5),
                    found=True
                )
            else:
                return ProviderResult(
                    provider=name, x=0, y=0, confidence=0,
                    found=False, error="Element not found"
                )
                
        except asyncio.TimeoutError:
            logger.warning("provider_timeout", provider=name)
            return ProviderResult(
                provider=name, x=0, y=0, confidence=0,
                found=False, error="Timeout"
            )
        except Exception as e:
            logger.error("provider_error", provider=name, error=str(e))
            return ProviderResult(
                provider=name, x=0, y=0, confidence=0,
                found=False, error=str(e)
            )
    
    async def _invoke_provider(
        self,
        provider: any,
        query: str,
        screenshot: bytes,
        screen_size: Tuple[int, int],
        frame_hash: Optional[str] = None
    ) -> Optional[Dict]:
        """Invoke a provider's locate method."""
        # Try different method signatures
        if hasattr(provider, 'find_element'):
            # Check if find_element accepts frame_hash (inspection or try/except)
            import inspect
            sig = inspect.signature(provider.find_element)
            if 'frame_hash' in sig.parameters:
                result = await provider.find_element(screenshot, query, screen_size, frame_hash=frame_hash)
            else:
                result = await provider.find_element(screenshot, query, screen_size)
                
            if result:
                return {"x": result.x, "y": result.y, "confidence": result.confidence}
        
        elif hasattr(provider, 'locate'):
            result = await provider.locate(query, screenshot)
            if result:
                return {"x": result.x, "y": result.y, "confidence": result.confidence}
        
        elif hasattr(provider, 'parse_screenshot'):
            # OmniParser style - parse then search
            import base64
            b64 = base64.b64encode(screenshot).decode()
            
            # Pass frame_hash to OmniParserProvider if it supports it
            import inspect
            sig = inspect.signature(provider.parse_screenshot)
            if 'frame_hash' in sig.parameters:
                parse_result = await provider.parse_screenshot(b64, screen_size, frame_hash=frame_hash)
            else:
                parse_result = await provider.parse_screenshot(b64, screen_size)
                
            if parse_result and parse_result.elements:
                # Find matching element by label
                query_lower = query.lower()
                for elem in parse_result.elements:
                    if query_lower in elem.label.lower():
                        return {"x": elem.x, "y": elem.y, "confidence": 0.8}
        
        return None
    
    def _calculate_consensus(
        self,
        valid_results: List[ProviderResult],
        all_results: List[ProviderResult],
    ) -> ConsensusResult:
        """Calculate consensus from provider results."""
        total_providers = len(all_results)
        agreed_providers = len(valid_results)
        
        if agreed_providers < self._min_agreement:
            self._consensus_misses += 1
            return ConsensusResult(
                x=0, y=0, confidence=0, variance_px=float('inf'),
                consensus_reached=False,
                providers_agreed=agreed_providers,
                providers_total=total_providers,
                provider_results=all_results,
                hallucination_check="FAILED"
            )
        
        # Calculate mean coordinates
        x_coords = [r.x for r in valid_results]
        y_coords = [r.y for r in valid_results]
        
        mean_x = sum(x_coords) / len(x_coords)
        mean_y = sum(y_coords) / len(y_coords)
        
        # Calculate variance (Euclidean distance from mean)
        variance = 0
        for r in valid_results:
            dist = math.sqrt((r.x - mean_x)**2 + (r.y - mean_y)**2)
            variance += dist
        variance = variance / len(valid_results) if valid_results else float('inf')
        
        # Calculate confidence based on agreement and variance
        agreement_score = agreed_providers / total_providers if total_providers else 0
        variance_score = max(0, 1 - (variance / self._max_variance_px))
        avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        
        final_confidence = (agreement_score * 0.3 + variance_score * 0.4 + avg_confidence * 0.3)
        
        # Determine hallucination status
        consensus_reached = variance < self._max_variance_px
        if consensus_reached and final_confidence > 0.7:
            hallucination_check = "PASSED"
            self._consensus_hits += 1
        elif consensus_reached:
            hallucination_check = "UNCERTAIN"
            self._consensus_hits += 1
        else:
            hallucination_check = "FAILED"
            self._consensus_misses += 1
        
        logger.info(
            "consensus_calculated",
            agreed=agreed_providers,
            total=total_providers,
            variance=round(variance, 2),
            confidence=round(final_confidence, 3),
            check=hallucination_check
        )
        
        return ConsensusResult(
            x=int(mean_x),
            y=int(mean_y),
            confidence=final_confidence,
            variance_px=variance,
            consensus_reached=consensus_reached,
            providers_agreed=agreed_providers,
            providers_total=total_providers,
            provider_results=all_results,
            hallucination_check=hallucination_check
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get consensus statistics."""
        return {
            "consensus_hits": self._consensus_hits,
            "consensus_misses": self._consensus_misses,
            "registered_providers": len(self._providers),
        }


# Global singleton
_consensus_engine: Optional[ConsensusEngine] = None


def get_consensus_engine() -> ConsensusEngine:
    """Get or create ConsensusEngine singleton."""
    global _consensus_engine
    if _consensus_engine is None:
        _consensus_engine = ConsensusEngine()
    return _consensus_engine
