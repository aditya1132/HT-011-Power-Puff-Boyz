#!/usr/bin/env python3
"""
AI Mental Health Companion - Complete FastAPI Server
A comprehensive FastAPI server with OpenAI integration for mental health support
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import uuid
import datetime
import random
import asyncio
import logging
from pathlib import Path

# OpenAI integration
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Using template responses only.")

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = None
use_openai = False

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    try:
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        use_openai = True
        logger.info("✅ OpenAI client initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize OpenAI client: {e}")
        use_openai = False
else:
    logger.info("ℹ️ OpenAI not available. Using template responses.")

# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Companion API",
    description="A supportive, privacy-first API providing emotional support, mood tracking, and personalized coping tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# In-memory storage for demo (replace with database in production)
demo_data = {
    "users": {},
    "mood_logs": {},
    "chat_history": {},
    "coping_sessions": {}
}

# Pydantic Models
class UserCreateRequest(BaseModel):
    preferred_coping_tools: Optional[List[str]] = []
    notification_preferences: Optional[Dict[str, bool]] = {}
    privacy_settings: Optional[Dict[str, bool]] = {}

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class EmotionResult(BaseModel):
    primary_emotion: str
    confidence: float
    sentiment_score: float
    intensity: str
    keywords_matched: List[str] = []
    processing_time_ms: float = 120.0

class CopingSuggestion(BaseModel):
    id: str
    name: str
    description: str
    duration_minutes: int

class SafetyInfo(BaseModel):
    intervention_triggered: bool
    safety_level: str
    crisis_resources: List[Dict[str, str]] = []
    professional_help_suggested: bool

class ChatResponse(BaseModel):
    chat_id: str
    message: str
    response_type: str
    emotion_detected: EmotionResult
    coping_suggestions: List[CopingSuggestion] = []
    follow_up_questions: List[str] = []
    resources: List[Dict[str, str]] = []
    safety_info: SafetyInfo
    processing_time_ms: float
    session_id: str
    timestamp: str

class MoodLogRequest(BaseModel):
    user_id: str
    mood_score: int = Field(..., ge=1, le=10)
    emotion_category: str
    notes: Optional[str] = None
    triggers: Optional[List[str]] = []

# Crisis detection keywords
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "hurt myself", "self harm",
    "cutting", "overdose", "die", "death wish", "worthless", "hopeless",
    "can't go on", "no point in living", "want to disappear",
    "better off dead", "end it all", "can't take it anymore"
]

# Simple emotion detection
def analyze_emotion(text: str) -> EmotionResult:
    """Enhanced emotion detection with crisis keyword checking"""
    text_lower = text.lower()

    # Check for crisis keywords first
    crisis_keywords_found = [kw for kw in CRISIS_KEYWORDS if kw in text_lower]

    # Emotion keywords
    emotions = {
        "stressed": ["stressed", "pressure", "overwhelmed", "burden", "deadlines", "too much"],
        "anxious": ["anxious", "nervous", "worry", "fear", "scared", "panic", "worried"],
        "sad": ["sad", "depressed", "down", "blue", "crying", "hurt", "broken"],
        "overwhelmed": ["overwhelmed", "can't handle", "too much", "drowning"],
        "angry": ["angry", "mad", "furious", "frustrated", "rage", "pissed"],
        "excited": ["excited", "thrilled", "amazing", "awesome", "great", "fantastic"],
        "positive": ["good", "happy", "wonderful", "excellent", "brilliant"],
        "grateful": ["grateful", "thankful", "blessed", "appreciate"],
        "confused": ["confused", "lost", "uncertain", "don't know"],
        "hopeless": ["hopeless", "pointless", "useless", "worthless"],
        "neutral": ["okay", "fine", "normal", "alright"]
    }

    detected_emotion = "neutral"
    confidence = 0.5
    keywords_matched = []

    # Check for crisis emotions first
    if crisis_keywords_found:
        detected_emotion = "crisis"
        confidence = 0.95
        keywords_matched = crisis_keywords_found
    else:
        # Regular emotion detection
        for emotion, keywords in emotions.items():
            matched = [kw for kw in keywords if kw in text_lower]
            if matched:
                detected_emotion = emotion
                confidence = min(0.95, 0.6 + len(matched) * 0.1)
                keywords_matched = matched
                break

    # Calculate sentiment score
    negative_emotions = ["stressed", "anxious", "sad", "overwhelmed", "angry", "hopeless", "crisis"]
    positive_emotions = ["excited", "positive", "grateful"]

    if detected_emotion in negative_emotions:
        sentiment_score = -0.9 if detected_emotion == "crisis" else -0.4
    elif detected_emotion in positive_emotions:
        sentiment_score = 0.7
    else:
        sentiment_score = 0.1

    # Determine intensity
    intensity = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"

    return EmotionResult(
        primary_emotion=detected_emotion,
        confidence=confidence,
        sentiment_score=sentiment_score,
        intensity=intensity,
        keywords_matched=keywords_matched,
        processing_time_ms=125.0
    )

# OpenAI response generation
async def generate_openai_response(user_input: str, emotion_result: EmotionResult) -> str:
    """Generate response using OpenAI GPT-4o-mini"""
    if not use_openai or not openai_client:
        raise Exception("OpenAI not available")

    # System prompt for mental health companion
    system_prompt = """You are a compassionate AI mental health companion. Your role is to provide empathetic, supportive responses that validate emotions and offer gentle guidance.

CORE PRINCIPLES:
- Always be empathetic and supportive
- Validate the user's emotions as normal and understandable
- Offer gentle coping suggestions when appropriate
- Never provide medical diagnosis or replace professional therapy
- Encourage professional help for significant distress
- Keep responses under 200 words
- Use warm, understanding tone

SAFETY GUIDELINES:
- If someone expresses suicidal thoughts, prioritize crisis resources
- For high distress, gently encourage professional support
- Never minimize or dismiss serious mental health concerns

RESPONSE STRUCTURE:
1. Acknowledge and validate their feelings
2. Provide supportive perspective
3. Offer one practical suggestion if appropriate
4. End with encouragement or gentle question"""

    # Add emotion-specific guidance
    emotion_guidance = {
        "anxious": "Focus on grounding techniques and reassurance about managing worry.",
        "stressed": "Emphasize breaking things down and self-care practices.",
        "sad": "Validate the pain while offering hope and connection.",
        "overwhelmed": "Help prioritize and suggest manageable steps.",
        "angry": "Acknowledge the emotion's validity and suggest healthy expression.",
        "crisis": "Provide immediate support and crisis resources with utmost care.",
        "hopeless": "Offer hope and encourage immediate professional support."
    }

    if emotion_result.primary_emotion in emotion_guidance:
        system_prompt += f"\n\nSPECIFIC GUIDANCE: The user is feeling {emotion_result.primary_emotion}. {emotion_guidance[emotion_result.primary_emotion]}"

    # Build user prompt
    user_prompt = f"""User's message: "{user_input}"

Detected emotion: {emotion_result.primary_emotion} (intensity: {emotion_result.intensity})
Sentiment score: {emotion_result.sentiment_score:.2f}

Please provide a supportive, empathetic response that validates their feelings and offers gentle guidance."""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7,
            timeout=10.0
        )

        ai_message = response.choices[0].message.content.strip()

        # Ensure response stays under 200 words
        words = ai_message.split()
        if len(words) > 200:
            ai_message = ' '.join(words[:200]) + "..."

        return ai_message

    except asyncio.TimeoutError:
        raise Exception("OpenAI request timed out")
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise Exception(f"OpenAI service error: {str(e)}")

# Template responses (fallback)
RESPONSE_TEMPLATES = {
    "crisis": [
        "I'm really concerned about what you've shared. Your life has value and meaning, and I want to help you get through this difficult time. Please reach out for immediate support - you don't have to face this alone.",
        "I can hear that you're in tremendous pain right now. Please know that these feelings, while overwhelming, are temporary. It's crucial that you connect with someone who can provide immediate support."
    ],
    "stressed": [
        "It sounds like you're carrying a lot right now, and that feeling of stress is completely valid. Remember that it's okay to take things one step at a time.",
        "I can hear that you're feeling overwhelmed, and that's understandable. You don't have to handle everything perfectly - just doing your best is enough."
    ],
    "anxious": [
        "Anxiety can feel really overwhelming, and I want you to know that's completely normal. Try to focus on what you can control right now.",
        "I hear that you're feeling worried, and those feelings are valid. Remember that most of our worries never actually happen."
    ],
    "sad": [
        "I'm sorry you're feeling this way right now. Your sadness is valid and it's important to acknowledge these feelings.",
        "It takes courage to share these feelings. Remember that healing isn't linear, and that's perfectly normal."
    ],
    "neutral": [
        "Thank you for sharing how you're feeling right now. I'm here to listen to whatever you're experiencing.",
        "I appreciate you taking the time to check in with yourself today."
    ]
}

# Coping suggestions
COPING_SUGGESTIONS = {
    "stressed": [
        CopingSuggestion(
            id="breathing_478",
            name="4-7-8 Breathing",
            description="Breathe in for 4, hold for 7, exhale for 8",
            duration_minutes=5
        ),
        CopingSuggestion(
            id="progressive_relaxation",
            name="Progressive Muscle Relaxation",
            description="Tense and relax each muscle group",
            duration_minutes=10
        )
    ],
    "anxious": [
        CopingSuggestion(
            id="grounding_54321",
            name="5-4-3-2-1 Grounding",
            description="Name 5 things you see, 4 you hear, 3 you feel, 2 you smell, 1 you taste",
            duration_minutes=5
        ),
        CopingSuggestion(
            id="box_breathing",
            name="Box Breathing",
            description="Inhale 4, hold 4, exhale 4, hold 4",
            duration_minutes=3
        )
    ],
    "sad": [
        CopingSuggestion(
            id="journaling",
            name="Emotion Journaling",
            description="Write about your feelings without judgment",
            duration_minutes=10
        ),
        CopingSuggestion(
            id="self_compassion",
            name="Self-Compassion Practice",
            description="Speak to yourself like you would a good friend",
            duration_minutes=5
        )
    ]
}

# Crisis resources
CRISIS_RESOURCES = [
    {"name": "National Suicide Prevention Lifeline", "contact": "988", "type": "phone"},
    {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "type": "text"},
    {"name": "Emergency Services", "contact": "911", "type": "phone"},
    {"name": "International Association for Suicide Prevention", "contact": "https://www.iasp.info/resources/Crisis_Centres/", "type": "website"}
]

# API Routes
@app.get("/")
async def root():
    openai_status = "✅ Enabled" if use_openai else "❌ Disabled (using templates)"
    return {
        "message": "Welcome to AI Mental Health Companion API",
        "version": "1.0.0",
        "status": "running",
        "openai_integration": openai_status,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "register": "POST /api/v1/users/register",
            "chat": "POST /api/v1/chat/message",
            "mood": "POST /api/v1/mood/log"
        },
        "safety_note": "🚨 Crisis Support: National Suicide Prevention Lifeline 988"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Mental Health Companion API",
        "version": "1.0.0",
        "openai_enabled": use_openai,
        "timestamp": datetime.datetime.now().isoformat()
    }

# User Registration
@app.post("/api/v1/users/register")
async def register_user(request: UserCreateRequest):
    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "created_at": datetime.datetime.now().isoformat(),
        "streak_count": 0,
        "total_check_ins": 0,
        "is_active": True,
        "preferred_coping_tools": request.preferred_coping_tools,
        "notification_preferences": request.notification_preferences,
        "privacy_settings": request.privacy_settings
    }

    demo_data["users"][user_id] = user
    return user

@app.get("/api/v1/users/profile/{user_id}")
async def get_user_profile(user_id: str):
    if user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    return demo_data["users"][user_id]

# Chat Message Route - THIS IS THE MISSING ROUTE!
@app.post("/api/v1/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    if request.user_id not in demo_data["users"]:
        # Auto-create user if not exists (for demo purposes)
        demo_data["users"][request.user_id] = {
            "user_id": request.user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "streak_count": 0,
            "total_check_ins": 0,
            "is_active": True
        }

    start_time = datetime.datetime.now()

    # Analyze emotion
    emotion_result = analyze_emotion(request.message)

    # Check for crisis situation
    is_crisis = emotion_result.primary_emotion == "crisis"
    needs_intervention = is_crisis or emotion_result.sentiment_score < -0.6

    # Generate response
    response_message = ""
    response_type = "supportive"

    if is_crisis:
        response_type = "crisis_intervention"
        response_message = random.choice(RESPONSE_TEMPLATES["crisis"])
    else:
        # Try OpenAI first, fallback to templates
        if use_openai:
            try:
                response_message = await generate_openai_response(request.message, emotion_result)
                response_type = "ai_supportive"
            except Exception as e:
                logger.error(f"OpenAI failed: {e}, using template fallback")
                emotion_templates = RESPONSE_TEMPLATES.get(emotion_result.primary_emotion, RESPONSE_TEMPLATES["neutral"])
                response_message = random.choice(emotion_templates)
                response_type = "template_supportive"
        else:
            emotion_templates = RESPONSE_TEMPLATES.get(emotion_result.primary_emotion, RESPONSE_TEMPLATES["neutral"])
            response_message = random.choice(emotion_templates)
            response_type = "template_supportive"

    # Get coping suggestions
    coping_suggestions = COPING_SUGGESTIONS.get(emotion_result.primary_emotion, [])

    # Generate follow-up questions
    follow_up_questions = [
        f"What's been the most challenging part about feeling {emotion_result.primary_emotion}?",
        "Is there someone you can talk to about this?",
        "What usually helps you feel better?"
    ][:2]

    # Safety info
    safety_info = SafetyInfo(
        intervention_triggered=needs_intervention,
        safety_level="crisis" if is_crisis else "high" if needs_intervention else "normal",
        crisis_resources=CRISIS_RESOURCES if is_crisis else [],
        professional_help_suggested=needs_intervention
    )

    # Calculate processing time
    processing_time = (datetime.datetime.now() - start_time).total_seconds() * 1000

    # Store chat record
    chat_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())

    chat_record = {
        "chat_id": chat_id,
        "user_id": request.user_id,
        "user_message": request.message,
        "ai_response": response_message,
        "emotion_detected": emotion_result.dict(),
        "response_type": response_type,
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id
    }

    demo_data["chat_history"][chat_id] = chat_record

    return ChatResponse(
        chat_id=chat_id,
        message=response_message,
        response_type=response_type,
        emotion_detected=emotion_result,
        coping_suggestions=coping_suggestions,
        follow_up_questions=follow_up_questions,
        resources=[],
        safety_info=safety_info,
        processing_time_ms=processing_time,
        session_id=session_id,
        timestamp=datetime.datetime.now().isoformat()
    )

@app.post("/api/v1/mood/log")
async def log_mood(request: MoodLogRequest):
    if request.user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    log_id = str(uuid.uuid4())
    mood_log = {
        "log_id": log_id,
        "user_id": request.user_id,
        "mood_score": request.mood_score,
        "emotion_category": request.emotion_category,
        "notes": request.notes,
        "triggers": request.triggers,
        "timestamp": datetime.datetime.now().isoformat(),
        "date_only": datetime.date.today().isoformat()
    }

    demo_data["mood_logs"][log_id] = mood_log
    return mood_log

@app.get("/api/v1/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    if user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    user_chats = [chat for chat in demo_data["chat_history"].values() if chat["user_id"] == user_id]
    user_chats.sort(key=lambda x: x["timestamp"], reverse=True)
    return user_chats[:limit]

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An internal server error occurred.",
            "type": "internal_server_error"
        }
    )

# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import time

    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Add request ID to headers
    request.state.request_id = request_id

    # Log incoming request
    logger.info(f"Request {request_id}: {request.method} {request.url}")

    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    # Log response
    logger.info(f"Request {request_id} completed in {process_time:.3f}s with status {response.status_code}")

    return response

if __name__ == "__main__":
    import uvicorn

    print("🌱 Starting AI Mental Health Companion API Server...")
    print("📡 API Documentation: http://localhost:8000/docs")
    print(f"🤖 OpenAI Integration: {'✅ Enabled' if use_openai else '❌ Disabled (add OPENAI_API_KEY to .env)'}")
    print("❤️  Remember: This is a supportive tool, not a replacement for professional care")
    print("🚨 Crisis Support: National Suicide Prevention Lifeline 988")
    print()

    if not use_openai:
        print("💡 To enable OpenAI responses:")
        print("   1. Get an API key from https://platform.openai.com/")
        print("   2. Add OPENAI_API_KEY=your-key-here to your .env file")
        print("   3. Restart the server")

    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
