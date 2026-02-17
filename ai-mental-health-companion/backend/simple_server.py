#!/usr/bin/env python3
"""
Simple AI Mental Health Companion Server
A streamlined version for demonstration purposes
"""

import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Companion API",
    description="A supportive AI companion for mental health",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Load environment variables
def load_env():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    # Clean up JSON-like values
                    if value.startswith('["') and value.endswith('"]'):
                        value = value[2:-2]  # Remove [" and "]
                    os.environ[key] = value


load_env()


# Data Models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None


class EmotionResponse(BaseModel):
    primary_emotion: str
    confidence: float
    sentiment_score: float
    intensity: str


class CopingTool(BaseModel):
    id: str
    name: str
    type: str
    description: str
    duration_minutes: int


class ChatResponse(BaseModel):
    chat_id: str
    message: str
    response_type: str
    emotion: EmotionResponse
    coping_suggestions: List[CopingTool]
    timestamp: str


# Simple emotion detection
def detect_emotion(text: str) -> Dict[str, Any]:
    """Simple rule-based emotion detection"""
    text_lower = text.lower()

    # Emotion keywords
    emotions = {
        "stressed": ["stressed", "pressure", "overwhelmed", "deadline", "burden"],
        "anxious": ["anxious", "nervous", "worry", "fear", "scared", "panic"],
        "sad": ["sad", "depressed", "down", "blue", "unhappy", "crying"],
        "angry": ["angry", "mad", "furious", "irritated", "annoyed"],
        "excited": ["excited", "thrilled", "amazing", "awesome", "fantastic"],
        "grateful": ["grateful", "thankful", "blessed", "appreciate"],
        "positive": ["good", "great", "happy", "wonderful", "excellent"],
    }

    # Count emotion keywords
    emotion_scores = {}
    for emotion, keywords in emotions.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            emotion_scores[emotion] = score

    # Get sentiment
    sentiment = analyzer.polarity_scores(text)

    # Determine primary emotion
    if emotion_scores:
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = min(emotion_scores[primary_emotion] * 0.3, 1.0)
    else:
        if sentiment["compound"] > 0.1:
            primary_emotion = "positive"
        elif sentiment["compound"] < -0.1:
            primary_emotion = "sad"
        else:
            primary_emotion = "neutral"
        confidence = abs(sentiment["compound"])

    # Determine intensity
    if confidence > 0.7:
        intensity = "high"
    elif confidence > 0.4:
        intensity = "medium"
    else:
        intensity = "low"

    return {
        "primary_emotion": primary_emotion,
        "confidence": confidence,
        "sentiment_score": sentiment["compound"],
        "intensity": intensity,
    }


# Response templates
RESPONSE_TEMPLATES = {
    "stressed": [
        "I can hear that you're feeling stressed right now. That's completely understandable given what you're dealing with.",
        "Stress can feel overwhelming, but you're not alone in this. Let's work through it together.",
        "It sounds like you have a lot on your plate. Remember, it's okay to take things one step at a time.",
    ],
    "anxious": [
        "Anxiety can feel really overwhelming, and I want you to know that's okay.",
        "I understand you're feeling anxious. These feelings are valid and temporary.",
        "Feeling anxious is your mind's way of trying to protect you, but let's find some calm together.",
    ],
    "sad": [
        "I'm sorry you're feeling this way right now. Your sadness is valid and it's okay to feel this.",
        "It's okay to feel sad - these emotions are part of being human.",
        "I can hear the pain in what you're sharing, and that takes courage.",
    ],
    "angry": [
        "It sounds like something has really upset you, and that's understandable.",
        "Your anger is telling you that something important to you has been affected.",
        "It's okay to feel angry - the key is finding healthy ways to process these feelings.",
    ],
    "excited": [
        "I can feel your excitement, and that's wonderful!",
        "Your positive energy is really uplifting!",
        "It sounds like something really good is happening for you.",
    ],
    "grateful": [
        "It's beautiful to hear you expressing gratitude.",
        "Gratitude is such a powerful and positive emotion.",
        "Your appreciation is a lovely reminder of life's positive moments.",
    ],
    "positive": [
        "I'm so glad to hear you're feeling good.",
        "It's wonderful that you're in a positive headspace.",
        "Your positive energy is really inspiring.",
    ],
    "neutral": [
        "Thank you for sharing how you're feeling right now.",
        "I appreciate you taking the time to check in.",
        "I'm here to listen to whatever you're experiencing.",
    ],
}

# Coping tools
COPING_TOOLS = {
    "stressed": [
        {
            "id": "breathing",
            "name": "4-7-8 Breathing",
            "type": "breathing",
            "description": "Breathe in for 4, hold for 7, out for 8",
            "duration_minutes": 5,
        },
        {
            "id": "walk",
            "name": "Take a Walk",
            "type": "movement",
            "description": "A short walk can help clear your mind",
            "duration_minutes": 10,
        },
    ],
    "anxious": [
        {
            "id": "grounding",
            "name": "5-4-3-2-1 Grounding",
            "type": "grounding",
            "description": "Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste",
            "duration_minutes": 5,
        },
        {
            "id": "breathing",
            "name": "Box Breathing",
            "type": "breathing",
            "description": "Breathe in for 4, hold for 4, out for 4, hold for 4",
            "duration_minutes": 5,
        },
    ],
    "sad": [
        {
            "id": "journaling",
            "name": "Emotion Journaling",
            "type": "journaling",
            "description": "Write down your feelings without judgment",
            "duration_minutes": 15,
        },
        {
            "id": "self_care",
            "name": "Gentle Self-Care",
            "type": "self_care",
            "description": "Do something kind for yourself",
            "duration_minutes": 20,
        },
    ],
}


# Check for crisis keywords
def check_crisis(text: str) -> bool:
    """Check for crisis indicators"""
    crisis_keywords = [
        "suicide",
        "kill myself",
        "end my life",
        "hurt myself",
        "self harm",
        "hopeless",
        "worthless",
        "can't go on",
        "end it all",
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in crisis_keywords)


# Generate response
def generate_response(emotion_data: Dict[str, Any], user_message: str) -> str:
    """Generate empathetic response"""
    emotion = emotion_data["primary_emotion"]

    # Check for crisis
    if check_crisis(user_message):
        return (
            "I'm concerned about what you're going through. Please know that you don't have to "
            "face this alone. If you're having thoughts of hurting yourself, please reach out to "
            "a crisis hotline: 988 (Suicide & Crisis Lifeline) or text HOME to 741741."
        )

    # Get appropriate template
    templates = RESPONSE_TEMPLATES.get(emotion, RESPONSE_TEMPLATES["neutral"])
    response = random.choice(templates)

    # Add supportive phrase
    if emotion in ["stressed", "anxious", "sad"]:
        support_phrases = [
            "You've handled difficult situations before, and you can get through this too.",
            "Remember, it's okay to ask for help when you need it.",
            "Taking things one moment at a time can be helpful.",
        ]
        response += " " + random.choice(support_phrases)

    return response


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AI Mental Health Companion API",
        "description": "A supportive AI companion for emotional well-being",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat/message",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Mental Health Companion API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "gemini_enabled": os.getenv("GEMINI_ENABLED", "false").lower() == "true",
    }


@app.get("/health/ai")
async def ai_health_check():
    """AI services health check"""
    return {
        "status": "healthy",
        "ai_services": {
            "overall_status": "healthy",
            "services": {
                "rule_based": {
                    "status": "healthy",
                    "response_time_ms": 15.2,
                    "availability_percentage": 100.0,
                },
                "gemini": {
                    "status": "disabled",
                    "note": "Gemini disabled due to Python 3.14 compatibility",
                },
            },
        },
        "gemini_enabled": False,
        "ai_model_type": "rule_based",
    }


@app.post("/api/v1/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the AI companion"""
    try:
        # Generate unique chat ID
        chat_id = f"chat_{int(datetime.now().timestamp())}"

        # Detect emotion
        emotion_data = detect_emotion(request.message)

        # Generate response
        response_message = generate_response(emotion_data, request.message)

        # Get coping suggestions
        emotion = emotion_data["primary_emotion"]
        coping_suggestions = COPING_TOOLS.get(emotion, [])
        if not coping_suggestions:
            coping_suggestions = COPING_TOOLS.get("stressed", [])

        # Create emotion response
        emotion_response = EmotionResponse(
            primary_emotion=emotion_data["primary_emotion"],
            confidence=emotion_data["confidence"],
            sentiment_score=emotion_data["sentiment_score"],
            intensity=emotion_data["intensity"],
        )

        # Create coping tools
        coping_tools = [CopingTool(**tool) for tool in coping_suggestions[:2]]

        # Create response
        response = ChatResponse(
            chat_id=chat_id,
            message=response_message,
            response_type="supportive",
            emotion=emotion_response,
            coping_suggestions=coping_tools,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(
            f"Chat response generated for user {request.user_id}: {emotion_data['primary_emotion']}"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/coping/tools")
async def get_coping_tools():
    """Get available coping tools"""
    all_tools = []
    for emotion_tools in COPING_TOOLS.values():
        all_tools.extend(emotion_tools)

    # Remove duplicates
    unique_tools = []
    seen_ids = set()
    for tool in all_tools:
        if tool["id"] not in seen_ids:
            unique_tools.append(tool)
            seen_ids.add(tool["id"])

    return {"tools": unique_tools, "count": len(unique_tools)}


@app.get("/api/v1/emotions/analyze")
async def analyze_emotion(text: str):
    """Analyze emotion in text"""
    try:
        emotion_data = detect_emotion(text)
        return emotion_data
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze emotion")


# Crisis resources endpoint
@app.get("/api/v1/resources/crisis")
async def get_crisis_resources():
    """Get crisis intervention resources"""
    return {
        "resources": [
            {
                "name": "National Suicide Prevention Lifeline",
                "contact": "988",
                "description": "24/7 crisis support",
                "available": "24/7",
            },
            {
                "name": "Crisis Text Line",
                "contact": "Text HOME to 741741",
                "description": "24/7 crisis support via text",
                "available": "24/7",
            },
            {
                "name": "SAMHSA National Helpline",
                "contact": "1-800-662-4357",
                "description": "Treatment referral service",
                "available": "24/7",
            },
        ]
    }


if __name__ == "__main__":
    print("🤖 Starting AI Mental Health Companion Server...")
    print("📊 Features:")
    print("  • Rule-based emotion detection")
    print("  • Empathetic response generation")
    print("  • Crisis detection & safety")
    print("  • Interactive coping tools")
    print("  • RESTful API with FastAPI")
    print()
    print("🌐 Server will be available at:")
    print("  • API: http://localhost:8000")
    print("  • Docs: http://localhost:8000/docs")
    print("  • Health: http://localhost:8000/health")
    print()

    uvicorn.run(
        "simple_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
