"""
AI Service Manager

Coordinates between different AI services (rule-based, Gemini, ML) and handles
fallbacks, load balancing, and service health monitoring for the mental health companion.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from app.ai.emotion_detection import EmotionDetectionService, EmotionResult
from app.ai.response_generator import ResponseGenerator, ResponseResult
from app.core.config import get_settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)
settings = get_settings()


class AIServiceType(Enum):
    """Available AI service types"""

    RULE_BASED = "rule_based"
    GEMINI = "gemini"
    HYBRID = "hybrid"
    ML = "ml"


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class ServiceHealth:
    """Service health information"""

    service_type: AIServiceType
    status: ServiceStatus
    last_check: datetime
    response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    last_error: Optional[str] = None
    availability_percentage: float = 100.0


@dataclass
class AIProcessingResult:
    """Combined result from AI processing"""

    emotion_result: EmotionResult
    response_result: ResponseResult
    processing_time_ms: float
    services_used: List[str] = field(default_factory=list)
    fallbacks_triggered: List[str] = field(default_factory=list)
    health_status: Dict[str, ServiceHealth] = field(default_factory=dict)


class AIServiceManager:
    """
    Manages multiple AI services with intelligent fallbacks and health monitoring
    """

    def __init__(self):
        """Initialize AI service manager"""
        self.settings = get_settings()

        # Initialize data structures first
        self.service_health: Dict[AIServiceType, ServiceHealth] = {}
        self.circuit_breakers: Dict[AIServiceType, Dict[str, Any]] = {}
        self.performance_history: Dict[AIServiceType, List[float]] = {}

        # Circuit breaker settings
        self.circuit_breaker_threshold = 5  # failures before opening circuit
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.max_history_size = 100

        # Initialize health tracking
        self._initialize_health_tracking()

        # Initialize services
        self.emotion_service = EmotionDetectionService()
        self.response_generator = ResponseGenerator()

        logger.info("AI Service Manager initialized")

    def _initialize_health_tracking(self):
        """Initialize health tracking for all services"""
        services = [
            AIServiceType.RULE_BASED,
            AIServiceType.GEMINI,
            AIServiceType.HYBRID,
            AIServiceType.ML,
        ]

        for service_type in services:
            self.service_health[service_type] = ServiceHealth(
                service_type=service_type,
                status=ServiceStatus.HEALTHY,
                last_check=datetime.now(),
            )
            self.circuit_breakers[service_type] = {
                "failures": 0,
                "last_failure": None,
                "is_open": False,
            }
            self.performance_history[service_type] = []

    async def process_user_input(
        self,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None,
        preferred_service: Optional[AIServiceType] = None,
    ) -> AIProcessingResult:
        """
        Process user input through the AI pipeline with intelligent service selection

        Args:
            user_input: User's message
            user_context: Additional context about the user
            preferred_service: Preferred AI service to use

        Returns:
            AIProcessingResult with emotion analysis and response
        """
        start_time = time.time()
        services_used = []
        fallbacks_triggered = []

        try:
            # Determine which service to use
            selected_service = self._select_optimal_service(preferred_service)
            services_used.append(selected_service.value)

            # Process emotion detection
            emotion_result = await self._process_emotion_detection(
                user_input, selected_service
            )

            # Generate response
            response_result = await self._generate_response(
                user_input, emotion_result, user_context, selected_service
            )

            # Update service health
            processing_time = (time.time() - start_time) * 1000
            await self._update_service_health(
                selected_service, processing_time, success=True
            )

            return AIProcessingResult(
                emotion_result=emotion_result,
                response_result=response_result,
                processing_time_ms=processing_time,
                services_used=services_used,
                fallbacks_triggered=fallbacks_triggered,
                health_status=dict(self.service_health),
            )

        except Exception as e:
            logger.error(f"AI processing failed: {e}")

            # Try fallback service
            fallback_service = self._get_fallback_service(selected_service)
            if fallback_service and fallback_service != selected_service:
                fallbacks_triggered.append(
                    f"{selected_service.value}_to_{fallback_service.value}"
                )
                services_used.append(fallback_service.value)

                try:
                    emotion_result = await self._process_emotion_detection(
                        user_input, fallback_service
                    )
                    response_result = await self._generate_response(
                        user_input, emotion_result, user_context, fallback_service
                    )

                    processing_time = (time.time() - start_time) * 1000

                    return AIProcessingResult(
                        emotion_result=emotion_result,
                        response_result=response_result,
                        processing_time_ms=processing_time,
                        services_used=services_used,
                        fallbacks_triggered=fallbacks_triggered,
                        health_status=dict(self.service_health),
                    )

                except Exception as fallback_error:
                    logger.error(f"Fallback service also failed: {fallback_error}")
                    await self._update_service_health(
                        fallback_service, 0, success=False, error=str(fallback_error)
                    )

            # Update health for failed primary service
            await self._update_service_health(
                selected_service, 0, success=False, error=str(e)
            )

            # Return emergency fallback
            return await self._emergency_fallback_response(
                user_input, services_used, fallbacks_triggered
            )

    async def _process_emotion_detection(
        self, user_input: str, service_type: AIServiceType
    ) -> EmotionResult:
        """Process emotion detection using specified service"""

        if self._is_circuit_breaker_open(service_type):
            raise AIServiceError(f"Circuit breaker open for {service_type.value}")

        try:
            if service_type == AIServiceType.GEMINI:
                return self.emotion_service.analyze_emotion(user_input, method="gemini")
            elif service_type == AIServiceType.HYBRID:
                return self.emotion_service.analyze_emotion(user_input, method="hybrid")
            elif service_type == AIServiceType.ML:
                return self.emotion_service.analyze_emotion(user_input, method="ml")
            else:  # RULE_BASED
                return self.emotion_service.analyze_emotion(
                    user_input, method="rule_based"
                )

        except Exception as e:
            self._record_service_failure(service_type, str(e))
            raise

    async def _generate_response(
        self,
        user_input: str,
        emotion_result: EmotionResult,
        user_context: Optional[Dict[str, Any]],
        service_type: AIServiceType,
    ) -> ResponseResult:
        """Generate response using specified service"""

        if self._is_circuit_breaker_open(service_type):
            raise AIServiceError(f"Circuit breaker open for {service_type.value}")

        try:
            # The response generator will automatically use the appropriate method
            # based on settings and service availability
            return self.response_generator.generate_response(
                user_input, emotion_result, user_context
            )

        except Exception as e:
            self._record_service_failure(service_type, str(e))
            raise

    def _select_optimal_service(
        self, preferred: Optional[AIServiceType] = None
    ) -> AIServiceType:
        """Select optimal AI service based on health, performance, and settings"""

        # Use preferred service if specified and healthy
        if preferred and self._is_service_healthy(preferred):
            return preferred

        # Use configured AI model type
        configured_type = AIServiceType(self.settings.AI_MODEL_TYPE.lower())
        if self._is_service_healthy(configured_type):
            return configured_type

        # Fallback to best available service
        healthy_services = [
            service_type
            for service_type in AIServiceType
            if self._is_service_healthy(service_type)
        ]

        if not healthy_services:
            logger.warning(
                "No healthy services available, using rule-based as last resort"
            )
            return AIServiceType.RULE_BASED

        # Select service with best performance
        best_service = min(
            healthy_services, key=lambda s: self._get_average_response_time(s)
        )

        return best_service

    def _get_fallback_service(
        self, failed_service: AIServiceType
    ) -> Optional[AIServiceType]:
        """Get appropriate fallback service for a failed service"""

        fallback_chain = {
            AIServiceType.GEMINI: [AIServiceType.HYBRID, AIServiceType.RULE_BASED],
            AIServiceType.HYBRID: [AIServiceType.RULE_BASED, AIServiceType.GEMINI],
            AIServiceType.ML: [AIServiceType.RULE_BASED, AIServiceType.HYBRID],
            AIServiceType.RULE_BASED: [AIServiceType.HYBRID],  # Last resort fallback
        }

        for fallback in fallback_chain.get(failed_service, []):
            if self._is_service_healthy(fallback):
                return fallback

        return AIServiceType.RULE_BASED  # Always available

    def _is_service_healthy(self, service_type: AIServiceType) -> bool:
        """Check if a service is healthy and available"""

        health = self.service_health.get(service_type)
        if not health:
            return False

        # Check circuit breaker
        if self._is_circuit_breaker_open(service_type):
            return False

        # Check service-specific availability
        if service_type == AIServiceType.GEMINI:
            return (
                health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
                and self._is_gemini_available()
            )
        elif service_type == AIServiceType.HYBRID:
            return health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
        elif service_type == AIServiceType.ML:
            return False  # ML not implemented yet
        else:  # RULE_BASED
            return True  # Always available

    def _is_gemini_available(self) -> bool:
        """Check if Gemini service is available"""
        try:
            from app.ai.gemini_service import gemini_service

            return gemini_service.is_available()
        except ImportError:
            return False

    def _is_circuit_breaker_open(self, service_type: AIServiceType) -> bool:
        """Check if circuit breaker is open for service"""

        cb = self.circuit_breakers.get(service_type, {})
        if not cb.get("is_open", False):
            return False

        # Check if timeout has passed
        last_failure = cb.get("last_failure")
        if last_failure:
            timeout_passed = (
                datetime.now() - last_failure
            ).total_seconds() > self.circuit_breaker_timeout
            if timeout_passed:
                # Reset circuit breaker
                cb["is_open"] = False
                cb["failures"] = 0
                logger.info(f"Circuit breaker reset for {service_type.value}")
                return False

        return True

    def _record_service_failure(self, service_type: AIServiceType, error: str):
        """Record a service failure and potentially open circuit breaker"""

        cb = self.circuit_breakers[service_type]
        cb["failures"] += 1
        cb["last_failure"] = datetime.now()

        if cb["failures"] >= self.circuit_breaker_threshold:
            cb["is_open"] = True
            logger.warning(
                f"Circuit breaker opened for {service_type.value} after {cb['failures']} failures"
            )

    async def _update_service_health(
        self,
        service_type: AIServiceType,
        response_time: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Update health metrics for a service"""

        health = self.service_health[service_type]
        health.last_check = datetime.now()

        if success:
            health.success_count += 1
            health.response_time_ms = response_time

            # Update performance history
            perf_history = self.performance_history[service_type]
            perf_history.append(response_time)
            if len(perf_history) > self.max_history_size:
                perf_history.pop(0)

            # Update status based on performance
            avg_response_time = sum(perf_history) / len(perf_history)
            if avg_response_time < 1000:  # < 1 second
                health.status = ServiceStatus.HEALTHY
            elif avg_response_time < 3000:  # < 3 seconds
                health.status = ServiceStatus.DEGRADED
            else:
                health.status = ServiceStatus.DEGRADED

        else:
            health.error_count += 1
            health.last_error = error

            # Calculate availability percentage
            total_requests = health.success_count + health.error_count
            health.availability_percentage = (
                health.success_count / total_requests
            ) * 100

            # Update status based on error rate
            if health.availability_percentage < 50:
                health.status = ServiceStatus.UNAVAILABLE
            elif health.availability_percentage < 90:
                health.status = ServiceStatus.DEGRADED
            else:
                health.status = ServiceStatus.HEALTHY

    def _get_average_response_time(self, service_type: AIServiceType) -> float:
        """Get average response time for a service"""

        perf_history = self.performance_history.get(service_type, [])
        if not perf_history:
            return float("inf")  # Penalize services with no history

        return sum(perf_history) / len(perf_history)

    async def _emergency_fallback_response(
        self, user_input: str, services_used: List[str], fallbacks_triggered: List[str]
    ) -> AIProcessingResult:
        """Generate emergency fallback response when all services fail"""

        fallbacks_triggered.append("emergency_fallback")

        # Create minimal emotion result
        emotion_result = EmotionResult(
            primary_emotion="neutral",
            confidence=0.0,
            secondary_emotions=[],
            sentiment_score=0.0,
            intensity="low",
            keywords_matched=[],
            processing_time_ms=0.0,
            source="emergency_fallback",
        )

        # Create emergency response
        emergency_messages = [
            "I'm having some technical difficulties right now, but I want you to know that I'm here for you.",
            "I'm experiencing some issues, but your feelings and experiences are still valid and important.",
            "While I'm having some technical problems, please know that reaching out was the right thing to do.",
            "I'm having trouble processing right now, but if you're in crisis, please contact 988 for immediate support.",
        ]

        import random

        emergency_message = random.choice(emergency_messages)

        response_result = ResponseResult(
            message=emergency_message,
            response_type="emergency_fallback",
            coping_suggestions=["Take deep breaths", "Reach out to someone you trust"],
            resources=[
                {
                    "name": "Crisis Text Line",
                    "contact": "Text HOME to 741741",
                    "description": "24/7 crisis support",
                }
            ],
            follow_up_questions=["Are you in a safe place right now?"],
            safety_intervention=False,
            generation_time_ms=0.0,
            source="emergency_fallback",
        )

        return AIProcessingResult(
            emotion_result=emotion_result,
            response_result=response_result,
            processing_time_ms=0.0,
            services_used=services_used,
            fallbacks_triggered=fallbacks_triggered,
            health_status=dict(self.service_health),
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all AI services"""

        health_report = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "circuit_breakers": {},
            "performance_metrics": {},
        }

        overall_healthy = True

        for service_type in AIServiceType:
            health = self.service_health[service_type]

            # Test service if it's been a while since last check
            time_since_check = (datetime.now() - health.last_check).total_seconds()
            if time_since_check > 300:  # 5 minutes
                await self._test_service_health(service_type)

            health_report["services"][service_type.value] = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "response_time_ms": health.response_time_ms,
                "error_count": health.error_count,
                "success_count": health.success_count,
                "availability_percentage": health.availability_percentage,
                "last_error": health.last_error,
            }

            if health.status == ServiceStatus.UNAVAILABLE:
                overall_healthy = False

            # Circuit breaker status
            cb = self.circuit_breakers[service_type]
            health_report["circuit_breakers"][service_type.value] = {
                "is_open": cb.get("is_open", False),
                "failure_count": cb.get("failures", 0),
                "last_failure": cb.get("last_failure").isoformat()
                if cb.get("last_failure")
                else None,
            }

            # Performance metrics
            perf_history = self.performance_history.get(service_type, [])
            if perf_history:
                health_report["performance_metrics"][service_type.value] = {
                    "average_response_time_ms": sum(perf_history) / len(perf_history),
                    "min_response_time_ms": min(perf_history),
                    "max_response_time_ms": max(perf_history),
                    "sample_count": len(perf_history),
                }

        health_report["overall_status"] = "healthy" if overall_healthy else "degraded"

        return health_report

    async def _test_service_health(self, service_type: AIServiceType):
        """Test specific service health with a simple request"""

        test_input = "How are you today?"
        start_time = time.time()

        try:
            if service_type == AIServiceType.GEMINI:
                await self._test_gemini_health()
            elif service_type == AIServiceType.RULE_BASED:
                # Rule-based is always available, just test basic functionality
                self.emotion_service.analyze_emotion(test_input, method="rule_based")
            elif service_type == AIServiceType.HYBRID:
                self.emotion_service.analyze_emotion(test_input, method="hybrid")

            response_time = (time.time() - start_time) * 1000
            await self._update_service_health(service_type, response_time, success=True)

        except Exception as e:
            await self._update_service_health(
                service_type, 0, success=False, error=str(e)
            )

    async def _test_gemini_health(self):
        """Test Gemini service health"""
        try:
            from app.ai.gemini_service import gemini_service

            return await gemini_service.health_check()
        except ImportError:
            raise AIServiceError("Gemini service not available")

    def get_service_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service usage statistics"""

        stats = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_metrics": {
                "total_requests": 0,
                "total_errors": 0,
                "overall_availability": 0.0,
                "average_response_time": 0.0,
            },
        }

        total_requests = 0
        total_errors = 0
        total_response_time = 0.0

        for service_type in AIServiceType:
            health = self.service_health[service_type]
            service_total = health.success_count + health.error_count

            if service_total > 0:
                availability = (health.success_count / service_total) * 100
            else:
                availability = 100.0

            perf_history = self.performance_history.get(service_type, [])
            avg_response_time = (
                sum(perf_history) / len(perf_history) if perf_history else 0.0
            )

            stats["services"][service_type.value] = {
                "total_requests": service_total,
                "successful_requests": health.success_count,
                "failed_requests": health.error_count,
                "availability_percentage": availability,
                "average_response_time_ms": avg_response_time,
                "current_status": health.status.value,
            }

            total_requests += service_total
            total_errors += health.error_count
            total_response_time += avg_response_time

        if total_requests > 0:
            stats["overall_metrics"]["total_requests"] = total_requests
            stats["overall_metrics"]["total_errors"] = total_errors
            stats["overall_metrics"]["overall_availability"] = (
                (total_requests - total_errors) / total_requests
            ) * 100
            stats["overall_metrics"]["average_response_time"] = (
                total_response_time / len(AIServiceType)
            )

        return stats


# Global AI service manager instance
ai_service_manager = AIServiceManager()
