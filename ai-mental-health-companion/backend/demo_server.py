#!/usr/bin/env python3
"""
AI Mental Health Companion - Demo Server
A simplified FastAPI server for demonstration purposes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uuid
import datetime
import random
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="AI Mental Health Companion Demo",
    description="A supportive, privacy-first API for emotional well-being",
    version="1.0.0-demo"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# In-memory storage for demo (replace with database in production)
demo_data = {
    "users": {},
    "mood_logs": {},
    "chat_history": {},
    "coping_sessions": {}
}

# Pydantic models
class UserCreateRequest(BaseModel):
    preferred_coping_tools: Optional[List[str]] = []
    notification_preferences: Optional[Dict[str, bool]] = {}
    privacy_settings: Optional[Dict[str, bool]] = {}

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class MoodLogRequest(BaseModel):
    user_id: str
    mood_score: int
    emotion_category: str
    notes: Optional[str] = None
    triggers: Optional[List[str]] = []
    time_of_day: Optional[str] = None

class CheckInRequest(BaseModel):
    user_id: str
    mood_score: Optional[int] = None
    quick_note: Optional[str] = None

# Emotion detection simulation
def analyze_emotion(text: str) -> Dict[str, Any]:
    """Simple rule-based emotion detection for demo"""
    text_lower = text.lower()

    # Emotion keywords
    emotions = {
        "stressed": ["stressed", "pressure", "overwhelmed", "burden", "deadlines"],
        "anxious": ["anxious", "nervous", "worry", "fear", "scared"],
        "sad": ["sad", "depressed", "down", "blue", "crying"],
        "overwhelmed": ["overwhelmed", "too much", "can't handle"],
        "angry": ["angry", "mad", "furious", "frustrated"],
        "excited": ["excited", "thrilled", "amazing", "awesome"],
        "positive": ["good", "happy", "great", "wonderful"],
        "grateful": ["grateful", "thankful", "blessed"],
        "confused": ["confused", "lost", "uncertain"],
        "neutral": ["okay", "fine", "normal"]
    }

    detected_emotion = "neutral"
    confidence = 0.5
    keywords_matched = []

    for emotion, keywords in emotions.items():
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            detected_emotion = emotion
            confidence = min(0.95, 0.6 + len(matched) * 0.1)
            keywords_matched = matched
            break

    return {
        "primary_emotion": detected_emotion,
        "confidence": confidence,
        "sentiment_score": -0.3 if detected_emotion in ["stressed", "anxious", "sad"] else 0.5,
        "intensity": "high" if confidence > 0.8 else "medium",
        "keywords_matched": keywords_matched,
        "processing_time_ms": 120.5
    }

# Response templates
RESPONSE_TEMPLATES = {
    "stressed": [
        "It sounds like you're carrying a lot right now. That feeling of stress is completely valid.",
        "I can hear that you're feeling overwhelmed, and that's understandable given what you're dealing with.",
        "Feeling stressed is your body's way of telling you that something needs attention. You're not alone in this."
    ],
    "anxious": [
        "Anxiety can feel really overwhelming, and I want you to know that's okay.",
        "It's understandable that you're feeling anxious. These feelings are valid and you're not alone.",
        "I hear that you're feeling worried, and those feelings make complete sense."
    ],
    "sad": [
        "I'm sorry you're feeling this way right now. Your sadness is valid and it's okay to feel this.",
        "It takes courage to share these feelings. I can hear the pain in what you're experiencing.",
        "Feeling sad is a natural response to difficult situations. You're being brave by reaching out."
    ],
    "neutral": [
        "Thank you for sharing how you're feeling right now.",
        "I appreciate you taking the time to check in with yourself.",
        "I'm here to listen to whatever you're experiencing."
    ]
}

COPING_SUGGESTIONS = {
    "stressed": ["Try the 4-7-8 breathing technique", "Take a 5-minute walk", "Practice progressive muscle relaxation"],
    "anxious": ["Use the 5-4-3-2-1 grounding technique", "Practice box breathing", "Try a brief mindfulness meditation"],
    "sad": ["Write in a journal about your feelings", "Reach out to a trusted friend", "Do one small thing that brings you comfort"],
    "overwhelmed": ["Break tasks into smaller steps", "Take 10 deep breaths", "Ask yourself what one thing you can let go of"],
    "neutral": ["Check in with yourself about your needs", "Practice gratitude", "Do something kind for yourself"]
}

COPING_TOOLS = [
    {
        "id": "breathing_478",
        "name": "4-7-8 Breathing",
        "type": "breathing",
        "description": "A calming breathing technique to reduce anxiety and stress",
        "duration_minutes": 5,
        "difficulty": "easy",
        "interactive": True,
        "instructions": [
            "Find a comfortable seated position",
            "Inhale through your nose for 4 counts",
            "Hold your breath for 7 counts",
            "Exhale through your mouth for 8 counts",
            "Repeat 3-4 times"
        ]
    },
    {
        "id": "grounding_54321",
        "name": "5-4-3-2-1 Grounding",
        "type": "grounding",
        "description": "Use your senses to ground yourself in the present moment",
        "duration_minutes": 5,
        "difficulty": "easy",
        "interactive": True,
        "instructions": [
            "Name 5 things you can see",
            "Name 4 things you can touch",
            "Name 3 things you can hear",
            "Name 2 things you can smell",
            "Name 1 thing you can taste"
        ]
    },
    {
        "id": "journaling_emotions",
        "name": "Emotion Check-In Journal",
        "type": "journaling",
        "description": "Write about your emotions to process and understand them",
        "duration_minutes": 10,
        "difficulty": "easy",
        "interactive": False,
        "instructions": [
            "Write: 'Right now I am feeling...'",
            "Describe the emotion in detail",
            "What might have triggered this emotion?",
            "What does this emotion need from me?",
            "Write one small act of self-care you can do"
        ]
    }
]

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Mental Health Companion Demo",
        "version": "1.0.0-demo",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "register": "POST /api/v1/users/register",
            "chat": "POST /api/v1/chat/message",
            "mood": "POST /api/v1/mood/log",
            "tools": "GET /api/v1/coping/tools"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Mental Health Companion Demo",
        "version": "1.0.0-demo",
        "timestamp": datetime.datetime.now().isoformat()
    }

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

@app.post("/api/v1/users/check-in")
async def daily_check_in(request: CheckInRequest):
    if request.user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    user = demo_data["users"][request.user_id]
    user["streak_count"] += 1
    user["total_check_ins"] += 1
    user["last_check_in"] = datetime.datetime.now().isoformat()

    encouragement = f"Great job! You're building a healthy habit with {user['streak_count']} days in a row."
    if user["streak_count"] == 1:
        encouragement = "Welcome back! Every journey begins with a single step."
    elif user["streak_count"] >= 7:
        encouragement = f"Amazing! {user['streak_count']} days of consistent self-care. You're doing great!"

    return {
        "message": f"Check-in complete! Current streak: {user['streak_count']} days",
        "streak_count": user["streak_count"],
        "total_check_ins": user["total_check_ins"],
        "encouragement": encouragement,
        "suggested_activities": ["Try a breathing exercise", "Log your mood", "Practice gratitude"]
    }

@app.post("/api/v1/chat/message")
async def send_message(request: ChatRequest):
    if request.user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    # Analyze emotion
    emotion_result = analyze_emotion(request.message)

    # Generate response
    emotion = emotion_result["primary_emotion"]
    templates = RESPONSE_TEMPLATES.get(emotion, RESPONSE_TEMPLATES["neutral"])
    response_message = random.choice(templates)

    # Get coping suggestions
    suggestions = COPING_SUGGESTIONS.get(emotion, COPING_SUGGESTIONS["neutral"])
    coping_tools = [tool for tool in COPING_TOOLS if emotion in tool.get("target_emotions", [emotion])][:2]

    chat_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())

    chat_record = {
        "chat_id": chat_id,
        "user_id": request.user_id,
        "user_message": request.message,
        "ai_response": response_message,
        "emotion_detected": emotion_result,
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": session_id
    }

    demo_data["chat_history"][chat_id] = chat_record

    return {
        "chat_id": chat_id,
        "message": response_message,
        "response_type": "supportive",
        "emotion_detected": emotion_result,
        "coping_suggestions": coping_tools,
        "follow_up_questions": [
            f"What's been the most challenging part about feeling {emotion}?",
            "Is there someone you can talk to about this?",
            "What usually helps you feel better?"
        ][:2],
        "resources": [],
        "safety_info": {
            "intervention_triggered": False,
            "safety_level": "normal",
            "crisis_resources": [],
            "professional_help_suggested": False
        },
        "processing_time_ms": 250.0,
        "session_id": session_id,
        "timestamp": datetime.datetime.now().isoformat()
    }

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
        "date_only": datetime.date.today().isoformat(),
        "time_of_day": request.time_of_day,
        "ai_confidence": 0.85
    }

    demo_data["mood_logs"][log_id] = mood_log
    return mood_log

@app.get("/api/v1/mood/history/{user_id}")
async def get_mood_history(user_id: str, days: int = 30):
    if user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    # Filter mood logs for this user
    user_logs = [log for log in demo_data["mood_logs"].values() if log["user_id"] == user_id]

    # Sort by timestamp, most recent first
    user_logs.sort(key=lambda x: x["timestamp"], reverse=True)

    return user_logs[:days]

@app.get("/api/v1/coping/tools")
async def get_coping_tools(emotion: Optional[str] = None):
    tools = COPING_TOOLS.copy()

    if emotion:
        # Filter tools suitable for the emotion
        suitable_tools = []
        for tool in tools:
            # Add target_emotions field if not present
            if "target_emotions" not in tool:
                if tool["type"] == "breathing":
                    tool["target_emotions"] = ["stressed", "anxious"]
                elif tool["type"] == "grounding":
                    tool["target_emotions"] = ["anxious", "overwhelmed"]
                elif tool["type"] == "journaling":
                    tool["target_emotions"] = ["sad", "confused", "neutral"]
                else:
                    tool["target_emotions"] = ["neutral"]

            if emotion in tool["target_emotions"]:
                suitable_tools.append(tool)

        tools = suitable_tools

    return tools

@app.get("/api/v1/dashboard/quick-stats/{user_id}")
async def get_quick_stats(user_id: str):
    if user_id not in demo_data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    user = demo_data["users"][user_id]
    user_logs = [log for log in demo_data["mood_logs"].values() if log["user_id"] == user_id]

    # Calculate this week's average
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_logs = [log for log in user_logs if log["date_only"] >= week_start.isoformat()]

    this_week_average = None
    if week_logs:
        this_week_average = sum(log["mood_score"] for log in week_logs) / len(week_logs)

    return {
        "current_mood": user_logs[0]["mood_score"] if user_logs else None,
        "streak_count": user["streak_count"],
        "this_week_average": round(this_week_average, 1) if this_week_average else None,
        "total_coping_sessions": len([s for s in demo_data["coping_sessions"].values() if s["user_id"] == user_id]),
        "mood_trend": "stable",
        "next_milestone": {
            "type": "streak",
            "target": 7 if user["streak_count"] < 7 else user["streak_count"] + 7,
            "progress": user["streak_count"],
            "description": f"Reach {7 if user['streak_count'] < 7 else user['streak_count'] + 7} day check-in streak"
        }
    }

@app.get("/demo")
async def get_demo():
    """Serve the demo interface"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    demo_path = os.path.join(root_dir, "demo.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return JSONResponse(status_code=404, content={"error": "demo.html not found"})

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": True, "message": "Resource not found", "type": "not_found"}
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error", "type": "server_error"}
    )

if __name__ == "__main__":
    import uvicorn
    print("🌱 Starting AI Mental Health Companion Demo Server...")
    print("📡 API Documentation: http://localhost:8000/docs")
    print("❤️  Remember: This is a supportive tool, not a replacement for professional care")
    print("🚨 Crisis Support: National Suicide Prevention Lifeline 988")

    uvicorn.run(
        "demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
