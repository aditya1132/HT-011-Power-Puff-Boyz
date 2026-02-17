# AI Mental Health Companion - AI Module
# This file makes the ai directory a Python package and exports AI/NLP functionality

from .emotion_detection import (
    EmotionResult,
    EmotionKeywords,
    RuleBasedEmotionDetector,
    MLEmotionDetector,
    EmotionDetectionService,
    emotion_service
)

from .response_generator import (
    ResponseResult,
    ResponseTemplates,
    SafetyChecker,
    ResponseGenerator
)

from .coping_tools import (
    CopingTool,
    CopingToolType,
    EmotionTarget,
    BreathingExercises,
    GroundingTechniques,
    MindfulnessExercises,
    JournalingPrompts,
    PhysicalTechniques,
    CognitiveTechniques,
    CopingToolsService,
    coping_service
)

__all__ = [
    # Emotion Detection
    "EmotionResult",
    "EmotionKeywords",
    "RuleBasedEmotionDetector",
    "MLEmotionDetector",
    "EmotionDetectionService",
    "emotion_service",

    # Response Generation
    "ResponseResult",
    "ResponseTemplates",
    "SafetyChecker",
    "ResponseGenerator",

    # Coping Tools
    "CopingTool",
    "CopingToolType",
    "EmotionTarget",
    "BreathingExercises",
    "GroundingTechniques",
    "MindfulnessExercises",
    "JournalingPrompts",
    "PhysicalTechniques",
    "CognitiveTechniques",
    "CopingToolsService",
    "coping_service"
]

# AI Module Version
AI_MODULE_VERSION = "1.0.0"

# AI Pipeline Configuration
AI_PIPELINE_CONFIG = {
    "emotion_detection": {
        "default_method": "rule_based",
        "confidence_threshold": 0.6,
        "supported_emotions": [
            "stressed", "anxious", "sad", "overwhelmed", "neutral",
            "positive", "angry", "excited", "confused", "grateful"
        ]
    },
    "response_generation": {
        "max_response_length": 500,
        "safety_enabled": True,
        "crisis_keywords_enabled": True
    },
    "coping_tools": {
        "total_tools": 13,
        "interactive_tools": 8,
        "tool_categories": [
            "breathing", "grounding", "mindfulness", "journaling",
            "physical", "cognitive", "relaxation", "creativity", "social"
        ]
    }
}

# Safety Configuration
SAFETY_CONFIG = {
    "crisis_keywords": [
        "suicide", "kill myself", "end my life", "hurt myself",
        "self harm", "cutting", "overdose", "die", "death wish",
        "worthless", "hopeless", "can't go on", "no point in living"
    ],
    "professional_help_threshold": 0.8,
    "crisis_resources": [
        {"name": "National Suicide Prevention Lifeline", "contact": "988"},
        {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
        {"name": "SAMHSA Helpline", "contact": "1-800-662-4357"}
    ]
}

def get_ai_system_info():
    """Get information about the AI system capabilities"""
    return {
        "version": AI_MODULE_VERSION,
        "emotion_detection": {
            "method": "rule_based",
            "supported_emotions": len(AI_PIPELINE_CONFIG["emotion_detection"]["supported_emotions"]),
            "confidence_threshold": AI_PIPELINE_CONFIG["emotion_detection"]["confidence_threshold"]
        },
        "coping_tools": {
            "total_available": AI_PIPELINE_CONFIG["coping_tools"]["total_tools"],
            "interactive_tools": AI_PIPELINE_CONFIG["coping_tools"]["interactive_tools"],
            "categories": len(AI_PIPELINE_CONFIG["coping_tools"]["tool_categories"])
        },
        "safety_features": {
            "crisis_detection": True,
            "safety_keywords": len(SAFETY_CONFIG["crisis_keywords"]),
            "professional_help_integration": True,
            "resource_suggestions": len(SAFETY_CONFIG["crisis_resources"])
        }
    }

def validate_ai_system():
    """Validate that all AI components are properly initialized"""
    try:
        # Test emotion detection
        test_result = emotion_service.analyze_emotion("I feel happy today")
        if not test_result.primary_emotion:
            return False, "Emotion detection not working"

        # Test response generation
        import asyncio
        generator = ResponseGenerator()
        try:
            test_response = asyncio.run(generator.generate_response(
                "Hello", test_result
            ))
            if not test_response.message:
                return False, "Response generation not working"
        except Exception as e:
            return False, f"Response generation test failed: {str(e)}"

        # Test coping tools
        tools = coping_service.get_all_tools()
        if len(tools) == 0:
            return False, "Coping tools not loaded"

        return True, "All AI systems operational"

    except Exception as e:
        return False, f"AI system validation failed: {str(e)}"
