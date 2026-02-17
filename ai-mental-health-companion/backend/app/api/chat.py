from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from app.database.database import get_db
from app.models.models import User, ChatHistory
from app.ai.emotion_detection import emotion_service
from app.ai.response_generator import response_generator
from app.ai.coping_tools import coping_service
from app.core.exceptions import ChatSessionError, EmotionDetectionError, AIServiceError
from app.core.logging import get_security_logger, get_audit_logger

router = APIRouter()
logger = logging.getLogger(__name__)
security_logger = get_security_logger()
audit_logger = get_audit_logger()


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat messages"""
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "I'm feeling really stressed about work today",
                "session_id": "session_123",
                "context": {"time_of_day": "morning"}
            }
        }


class EmotionResponse(BaseModel):
    """Emotion detection response model"""
    primary_emotion: str
    confidence: float
    secondary_emotions: List[Dict[str, float]]
    sentiment_score: float
    intensity: str
    keywords_matched: List[str]
    processing_time_ms: float


class CopingToolSuggestion(BaseModel):
    """Coping tool suggestion model"""
    id: str
    name: str
    type: str
    description: str
    duration_minutes: int
    difficulty: str
    interactive: bool


class SafetyInfo(BaseModel):
    """Safety information model"""
    intervention_triggered: bool
    safety_level: str
    crisis_resources: List[Dict[str, str]]
    professional_help_suggested: bool


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    chat_id: str
    message: str
    response_type: str
    emotion_detected: EmotionResponse
    coping_suggestions: List[CopingToolSuggestion]
    follow_up_questions: List[str]
    resources: List[Dict[str, str]]
    safety_info: SafetyInfo
    processing_time_ms: float
    session_id: str
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "chat_id": "chat_123",
                "message": "I understand you're feeling stressed. That's completely valid given what you're going through.",
                "response_type": "supportive",
                "emotion_detected": {
                    "primary_emotion": "stressed",
                    "confidence": 0.85,
                    "secondary_emotions": [{"anxious": 0.6}],
                    "sentiment_score": -0.4,
                    "intensity": "medium",
                    "keywords_matched": ["stressed", "work"],
                    "processing_time_ms": 150.5
                },
                "coping_suggestions": [
                    {
                        "id": "breathing_478",
                        "name": "4-7-8 Breathing",
                        "type": "breathing",
                        "description": "A calming breathing technique",
                        "duration_minutes": 5,
                        "difficulty": "easy",
                        "interactive": True
                    }
                ],
                "follow_up_questions": [
                    "What's the main source of your stress right now?"
                ],
                "resources": [],
                "safety_info": {
                    "intervention_triggered": False,
                    "safety_level": "normal",
                    "crisis_resources": [],
                    "professional_help_suggested": False
                },
                "processing_time_ms": 250.0,
                "session_id": "session_123",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""
    conversations: List[Dict[str, Any]]
    total_count: int
    has_more: bool


class EmotionAnalysisRequest(BaseModel):
    """Request model for standalone emotion analysis"""
    text: str = Field(..., min_length=1, max_length=2000, description="Text to analyze")

    class Config:
        schema_extra = {
            "example": {
                "text": "I'm feeling overwhelmed with everything I need to do"
            }
        }


@router.post("/message", response_model=ChatResponse, summary="Send a chat message")
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """
    Send a message to the AI companion and receive a supportive response

    This endpoint:
    1. Detects emotions in the user's message
    2. Checks for safety concerns
    3. Generates an appropriate supportive response
    4. Suggests relevant coping tools
    5. Stores the conversation (if enabled)
    """
    start_time = datetime.now()

    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user's last activity
        user.last_activity = datetime.now()

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Log the interaction (without storing the actual message for privacy)
        audit_logger.log_user_action(
            user_id=request.user_id,
            action="chat_message_sent",
            details={
                "session_id": session_id,
                "message_length": len(request.message),
                "has_context": bool(request.context)
            }
        )

        # Analyze emotion from user message
        try:
            emotion_result = emotion_service.analyze_emotion(request.message)
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            raise EmotionDetectionError("Failed to analyze emotions in message")

        # Check for crisis keywords
        crisis_detected, crisis_keywords = emotion_service.check_crisis_keywords(request.message)

        if crisis_detected:
            security_logger.log_crisis_detection(
                user_id=request.user_id,
                message=request.message,  # Note: In production, consider not logging the actual message
                keywords=crisis_keywords
            )

            # Update user's crisis alert count
            user.crisis_alerts_count += 1
            user.last_crisis_alert = datetime.now()

        # Generate supportive response
        try:
            response_result = response_generator.generate_response(
                user_input=request.message,
                emotion_result=emotion_result,
                user_context=request.context
            )
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise AIServiceError("Failed to generate response")

        # Get coping tool suggestions
        coping_tools = coping_service.get_tools_for_emotion(
            emotion=emotion_result.primary_emotion,
            difficulty="easy",
            max_duration=10
        )

        # Convert coping tools to response format
        coping_suggestions = [
            CopingToolSuggestion(
                id=tool.id,
                name=tool.name,
                type=tool.type.value,
                description=tool.description,
                duration_minutes=tool.duration_minutes,
                difficulty=tool.difficulty,
                interactive=tool.interactive
            )
            for tool in coping_tools[:3]  # Limit to 3 suggestions
        ]

        # Create chat history record
        chat_record = ChatHistory(
            user_id=request.user_id,
            user_message=request.message,
            ai_response=response_result.message,
            emotion_detected=emotion_result.primary_emotion,
            emotion_confidence=emotion_result.confidence,
            sentiment_score=emotion_result.sentiment_score,
            crisis_keywords_detected=crisis_keywords if crisis_detected else None,
            safety_intervention=response_result.safety_intervention,
            session_id=session_id,
            conversation_turn=1,  # TODO: Implement proper turn counting
            response_time_ms=int(response_result.generation_time_ms),
            coping_tools_suggested=[tool.id for tool in coping_tools[:3]]
        )

        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)

        # Calculate total processing time
        total_processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Prepare safety information
        safety_info = SafetyInfo(
            intervention_triggered=response_result.safety_intervention,
            safety_level="crisis" if crisis_detected else "normal",
            crisis_resources=response_result.resources if crisis_detected else [],
            professional_help_suggested=response_result.safety_intervention
        )

        # Create emotion response
        emotion_response = EmotionResponse(
            primary_emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence,
            secondary_emotions=[
                {emotion: confidence} for emotion, confidence in emotion_result.secondary_emotions
            ],
            sentiment_score=emotion_result.sentiment_score,
            intensity=emotion_result.intensity,
            keywords_matched=emotion_result.keywords_matched,
            processing_time_ms=emotion_result.processing_time_ms
        )

        # Create response
        chat_response = ChatResponse(
            chat_id=chat_record.chat_id,
            message=response_result.message,
            response_type=response_result.response_type,
            emotion_detected=emotion_response,
            coping_suggestions=coping_suggestions,
            follow_up_questions=response_result.follow_up_questions,
            resources=response_result.resources,
            safety_info=safety_info,
            processing_time_ms=total_processing_time,
            session_id=session_id,
            timestamp=datetime.now()
        )

        return chat_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message. Please try again."
        )


@router.get("/history/{user_id}", response_model=ChatHistoryResponse, summary="Get chat history")
async def get_chat_history(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve chat history for a user

    Args:
        user_id: User ID to get history for
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        session_id: Optional filter by session ID
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build query
        query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)

        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)

        # Get total count
        total_count = query.count()

        # Get conversations with pagination
        conversations = query.order_by(
            ChatHistory.timestamp.desc()
        ).offset(offset).limit(limit).all()

        # Convert to response format (excluding sensitive data)
        conversation_data = []
        for chat in conversations:
            conversation_data.append({
                "chat_id": chat.chat_id,
                "session_id": chat.session_id,
                "emotion_detected": chat.emotion_detected,
                "emotion_confidence": chat.emotion_confidence,
                "sentiment_score": chat.sentiment_score,
                "safety_intervention": chat.safety_intervention,
                "timestamp": chat.timestamp.isoformat(),
                "response_time_ms": chat.response_time_ms,
                "coping_tools_suggested": chat.coping_tools_suggested
            })

        audit_logger.log_user_action(
            user_id=user_id,
            action="chat_history_accessed",
            details={"limit": limit, "offset": offset}
        )

        return ChatHistoryResponse(
            conversations=conversation_data,
            total_count=total_count,
            has_more=offset + len(conversations) < total_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat history"
        )


@router.post("/analyze-emotion", response_model=EmotionResponse, summary="Analyze emotion in text")
async def analyze_emotion(request: EmotionAnalysisRequest):
    """
    Analyze emotion in text without generating a response

    This is useful for standalone emotion detection without the full chat flow
    """
    try:
        # Analyze emotion
        emotion_result = emotion_service.analyze_emotion(request.text)

        # Convert to response format
        return EmotionResponse(
            primary_emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence,
            secondary_emotions=[
                {emotion: confidence} for emotion, confidence in emotion_result.secondary_emotions
            ],
            sentiment_score=emotion_result.sentiment_score,
            intensity=emotion_result.intensity,
            keywords_matched=emotion_result.keywords_matched,
            processing_time_ms=emotion_result.processing_time_ms
        )

    except Exception as e:
        logger.error(f"Emotion analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze emotion in text"
        )


@router.delete("/history/{user_id}", summary="Delete chat history")
async def delete_chat_history(
    user_id: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Delete chat history for a user

    Args:
        user_id: User ID to delete history for
        session_id: Optional - delete only specific session
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Build delete query
        query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)

        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)

        # Count records to be deleted
        count = query.count()

        # Delete records
        query.delete()
        db.commit()

        audit_logger.log_user_action(
            user_id=user_id,
            action="chat_history_deleted",
            details={"records_deleted": count, "session_id": session_id}
        )

        return {"message": f"Deleted {count} chat records", "deleted_count": count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete chat history error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete chat history"
        )


@router.get("/sessions/{user_id}", summary="Get user's chat sessions")
async def get_chat_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get list of chat sessions for a user"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get unique session IDs with metadata
        sessions = db.query(
            ChatHistory.session_id,
            db.func.min(ChatHistory.timestamp).label('started_at'),
            db.func.max(ChatHistory.timestamp).label('last_activity'),
            db.func.count(ChatHistory.chat_id).label('message_count')
        ).filter(
            ChatHistory.user_id == user_id
        ).group_by(
            ChatHistory.session_id
        ).order_by(
            db.func.max(ChatHistory.timestamp).desc()
        ).all()

        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": session.session_id,
                "started_at": session.started_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "message_count": session.message_count
            })

        return {"sessions": session_data, "total_sessions": len(session_data)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve chat sessions"
        )
