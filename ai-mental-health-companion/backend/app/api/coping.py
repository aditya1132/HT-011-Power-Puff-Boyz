from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from app.database.database import get_db
from app.models.models import User, CopingSession
from app.ai.coping_tools import coping_service, CopingTool, CopingToolType
from app.core.exceptions import UserNotFoundError, CopingToolError
from app.core.logging import get_audit_logger

router = APIRouter()
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


# Request/Response Models
class CopingToolRequest(BaseModel):
    """Request model for getting coping tools"""
    emotion: str = Field(..., description="Target emotion for coping tools")
    difficulty: Optional[str] = Field(None, description="Preferred difficulty level")
    max_duration: Optional[int] = Field(None, ge=1, le=60, description="Maximum duration in minutes")
    tool_type: Optional[str] = Field(None, description="Preferred tool type")

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v is not None:
            valid_difficulties = ['easy', 'medium', 'hard']
            if v not in valid_difficulties:
                raise ValueError(f"Invalid difficulty. Must be one of: {valid_difficulties}")
        return v

    @validator('tool_type')
    def validate_tool_type(cls, v):
        if v is not None:
            valid_types = [t.value for t in CopingToolType]
            if v not in valid_types:
                raise ValueError(f"Invalid tool type. Must be one of: {valid_types}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "emotion": "stressed",
                "difficulty": "easy",
                "max_duration": 10,
                "tool_type": "breathing"
            }
        }


class CopingToolResponse(BaseModel):
    """Response model for coping tools"""
    id: str
    name: str
    type: str
    description: str
    target_emotions: List[str]
    duration_minutes: int
    difficulty: str
    instructions: List[str]
    benefits: List[str]
    requirements: List[str]
    interactive: bool
    guided_steps: Optional[List[Dict[str, Any]]]

    class Config:
        schema_extra = {
            "example": {
                "id": "breathing_478",
                "name": "4-7-8 Breathing",
                "type": "breathing",
                "description": "A calming breathing technique to reduce anxiety and stress",
                "target_emotions": ["stressed", "anxious"],
                "duration_minutes": 5,
                "difficulty": "easy",
                "instructions": [
                    "Find a comfortable seated position",
                    "Inhale for 4 counts",
                    "Hold for 7 counts",
                    "Exhale for 8 counts"
                ],
                "benefits": ["Reduces anxiety", "Promotes relaxation"],
                "requirements": ["Comfortable seating", "Quiet environment"],
                "interactive": True,
                "guided_steps": []
            }
        }


class StartSessionRequest(BaseModel):
    """Request model for starting a coping session"""
    user_id: str = Field(..., description="User ID")
    tool_id: str = Field(..., description="Coping tool ID")
    trigger_emotion: Optional[str] = Field(None, description="Emotion that triggered this session")
    pre_mood_score: Optional[int] = Field(None, ge=1, le=5, description="Mood score before session")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "tool_id": "breathing_478",
                "trigger_emotion": "stressed",
                "pre_mood_score": 2
            }
        }


class SessionResponse(BaseModel):
    """Response model for coping sessions"""
    session_id: str
    user_id: str
    tool_id: str
    tool_name: str
    started_at: datetime
    completed: bool
    guided_session_data: Optional[Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "tool_id": "breathing_478",
                "tool_name": "4-7-8 Breathing",
                "started_at": "2024-01-01T12:00:00Z",
                "completed": False,
                "guided_session_data": {
                    "total_steps": 5,
                    "current_step": 0,
                    "estimated_duration": 5
                }
            }
        }


class CompleteSessionRequest(BaseModel):
    """Request model for completing a coping session"""
    session_id: str = Field(..., description="Session ID")
    completed: bool = Field(True, description="Whether the session was completed")
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=1.0, description="Completion percentage")
    post_mood_score: Optional[int] = Field(None, ge=1, le=5, description="Mood score after session")
    helpfulness_rating: Optional[int] = Field(None, ge=1, le=5, description="How helpful was this tool")
    user_notes: Optional[str] = Field(None, max_length=500, description="User's notes about the session")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "completed": True,
                "completion_percentage": 1.0,
                "post_mood_score": 4,
                "helpfulness_rating": 4,
                "user_notes": "This breathing exercise really helped me calm down"
            }
        }


class SessionHistoryResponse(BaseModel):
    """Response model for session history"""
    sessions: List[Dict[str, Any]]
    total_sessions: int
    favorite_tools: List[Dict[str, Any]]
    effectiveness_stats: Dict[str, float]


class RecommendationRequest(BaseModel):
    """Request model for personalized recommendations"""
    user_id: str = Field(..., description="User ID")
    current_emotion: str = Field(..., description="Current emotional state")
    available_time: Optional[int] = Field(None, ge=1, le=60, description="Available time in minutes")
    preferred_types: Optional[List[str]] = Field(default_factory=list, description="Preferred tool types")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_emotion": "anxious",
                "available_time": 10,
                "preferred_types": ["breathing", "grounding"]
            }
        }


@router.get("/tools", response_model=List[CopingToolResponse], summary="Get available coping tools")
async def get_coping_tools(
    emotion: Optional[str] = Query(None, description="Filter by target emotion"),
    tool_type: Optional[str] = Query(None, description="Filter by tool type"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in minutes"),
    interactive_only: bool = Query(False, description="Return only interactive tools")
):
    """
    Get available coping tools with optional filters

    This endpoint returns a list of coping tools that can be filtered by:
    - Target emotion
    - Tool type (breathing, grounding, etc.)
    - Difficulty level
    - Maximum duration
    - Interactive vs non-interactive
    """
    try:
        # Get all tools or filter by emotion
        if emotion:
            tools = coping_service.get_tools_for_emotion(
                emotion=emotion,
                difficulty=difficulty,
                max_duration=max_duration
            )
        else:
            tools = coping_service.get_all_tools()

        # Apply additional filters
        if tool_type:
            tools = [tool for tool in tools if tool.type.value == tool_type]

        if difficulty and not emotion:  # emotion filter already applies difficulty
            tools = [tool for tool in tools if tool.difficulty == difficulty]

        if max_duration and not emotion:  # emotion filter already applies max_duration
            tools = [tool for tool in tools if tool.duration_minutes <= max_duration]

        if interactive_only:
            tools = [tool for tool in tools if tool.interactive]

        # Convert to response format
        tool_responses = []
        for tool in tools:
            tool_responses.append(CopingToolResponse(
                id=tool.id,
                name=tool.name,
                type=tool.type.value,
                description=tool.description,
                target_emotions=[emotion.value for emotion in tool.target_emotions],
                duration_minutes=tool.duration_minutes,
                difficulty=tool.difficulty,
                instructions=tool.instructions,
                benefits=tool.benefits,
                requirements=tool.requirements,
                interactive=tool.interactive,
                guided_steps=tool.guided_steps
            ))

        return tool_responses

    except Exception as e:
        logger.error(f"Get coping tools error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve coping tools"
        )


@router.get("/tools/{tool_id}", response_model=CopingToolResponse, summary="Get specific coping tool")
async def get_coping_tool(tool_id: str):
    """Get details for a specific coping tool"""
    try:
        tool = coping_service.get_tool_by_id(tool_id)
        if not tool:
            raise CopingToolError(f"Tool with ID {tool_id} not found")

        return CopingToolResponse(
            id=tool.id,
            name=tool.name,
            type=tool.type.value,
            description=tool.description,
            target_emotions=[emotion.value for emotion in tool.target_emotions],
            duration_minutes=tool.duration_minutes,
            difficulty=tool.difficulty,
            instructions=tool.instructions,
            benefits=tool.benefits,
            requirements=tool.requirements,
            interactive=tool.interactive,
            guided_steps=tool.guided_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get coping tool error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve coping tool"
        )


@router.post("/recommendations", response_model=List[CopingToolResponse], summary="Get personalized tool recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized coping tool recommendations based on user history and preferences
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise UserNotFoundError(request.user_id)

        # Build user preferences from request and history
        user_preferences = {
            "preferred_types": request.preferred_types,
            "max_duration": request.available_time,
            "difficulty": "easy"  # Default to easy for recommendations
        }

        # Get user's session history to improve recommendations
        recent_sessions = db.query(CopingSession).filter(
            CopingSession.user_id == request.user_id
        ).order_by(CopingSession.started_at.desc()).limit(20).all()

        # Analyze user's preferred tools based on effectiveness
        preferred_tools = {}
        for session in recent_sessions:
            if session.completed and session.helpfulness_rating:
                if session.tool_type not in preferred_tools:
                    preferred_tools[session.tool_type] = []
                preferred_tools[session.tool_type].append(session.helpfulness_rating)

        # Add user's most effective tool types to preferences
        if preferred_tools:
            avg_ratings = {
                tool_type: sum(ratings) / len(ratings)
                for tool_type, ratings in preferred_tools.items()
            }
            best_types = sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)
            if not request.preferred_types:
                user_preferences["preferred_types"] = [t[0] for t in best_types[:3]]

        # Get recommendations
        recommended_tools = coping_service.get_tool_recommendations(
            emotion=request.current_emotion,
            user_preferences=user_preferences
        )

        # Convert to response format
        tool_responses = []
        for tool in recommended_tools:
            tool_responses.append(CopingToolResponse(
                id=tool.id,
                name=tool.name,
                type=tool.type.value,
                description=tool.description,
                target_emotions=[emotion.value for emotion in tool.target_emotions],
                duration_minutes=tool.duration_minutes,
                difficulty=tool.difficulty,
                instructions=tool.instructions,
                benefits=tool.benefits,
                requirements=tool.requirements,
                interactive=tool.interactive,
                guided_steps=tool.guided_steps
            ))

        audit_logger.log_user_action(
            user_id=request.user_id,
            action="coping_recommendations_requested",
            details={
                "emotion": request.current_emotion,
                "available_time": request.available_time,
                "recommendations_count": len(tool_responses)
            }
        )

        return tool_responses

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recommendations error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get personalized recommendations"
        )


@router.post("/session/start", response_model=SessionResponse, summary="Start a coping session")
async def start_coping_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db)
):
    """Start a new coping tool session"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise UserNotFoundError(request.user_id)

        # Validate tool exists
        tool = coping_service.get_tool_by_id(request.tool_id)
        if not tool:
            raise CopingToolError(f"Tool with ID {request.tool_id} not found", tool_type=request.tool_id)

        # Create coping session record
        session = CopingSession(
            user_id=request.user_id,
            tool_type=tool.type.value,
            tool_name=tool.name,
            trigger_emotion=request.trigger_emotion,
            pre_mood_score=request.pre_mood_score,
            completed=False
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Create guided session data for interactive tools
        guided_session_data = None
        if tool.interactive:
            guided_session_data = coping_service.create_guided_session(request.tool_id)

        audit_logger.log_user_action(
            user_id=request.user_id,
            action="coping_session_started",
            details={
                "tool_id": request.tool_id,
                "tool_name": tool.name,
                "trigger_emotion": request.trigger_emotion
            }
        )

        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            tool_id=request.tool_id,
            tool_name=tool.name,
            started_at=session.started_at,
            completed=session.completed,
            guided_session_data=guided_session_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start coping session"
        )


@router.put("/session/complete", summary="Complete a coping session")
async def complete_coping_session(
    request: CompleteSessionRequest,
    db: Session = Depends(get_db)
):
    """Complete a coping session and record feedback"""
    try:
        # Find the session
        session = db.query(CopingSession).filter(
            CopingSession.session_id == request.session_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Coping session not found")

        # Update session with completion data
        session.completed = request.completed
        session.completion_percentage = request.completion_percentage
        session.post_mood_score = request.post_mood_score
        session.helpfulness_rating = request.helpfulness_rating
        session.user_notes = request.user_notes
        session.completed_at = datetime.now()

        # Calculate duration if session was completed
        if request.completed:
            duration = (session.completed_at - session.started_at).total_seconds()
            session.duration_seconds = int(duration)

        db.commit()

        audit_logger.log_user_action(
            user_id=session.user_id,
            action="coping_session_completed",
            details={
                "session_id": request.session_id,
                "tool_type": session.tool_type,
                "completed": request.completed,
                "helpfulness_rating": request.helpfulness_rating,
                "mood_improvement": (
                    request.post_mood_score - session.pre_mood_score
                    if request.post_mood_score and session.pre_mood_score
                    else None
                )
            }
        )

        return {
            "message": "Session completed successfully",
            "session_id": session.session_id,
            "mood_improvement": (
                request.post_mood_score - session.pre_mood_score
                if request.post_mood_score and session.pre_mood_score
                else None
            )
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to complete coping session"
        )


@router.get("/session/history/{user_id}", response_model=SessionHistoryResponse, summary="Get coping session history")
async def get_session_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of sessions to return"),
    db: Session = Depends(get_db)
):
    """Get user's coping session history with analytics"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Get session history
        sessions = db.query(CopingSession).filter(
            CopingSession.user_id == user_id
        ).order_by(
            CopingSession.started_at.desc()
        ).limit(limit).all()

        # Convert sessions to response format
        session_data = []
        for session in sessions:
            session_info = {
                "session_id": session.session_id,
                "tool_type": session.tool_type,
                "tool_name": session.tool_name,
                "started_at": session.started_at.isoformat(),
                "completed": session.completed,
                "duration_seconds": session.duration_seconds,
                "trigger_emotion": session.trigger_emotion,
                "pre_mood_score": session.pre_mood_score,
                "post_mood_score": session.post_mood_score,
                "helpfulness_rating": session.helpfulness_rating,
                "completion_percentage": session.completion_percentage
            }
            session_data.append(session_info)

        # Calculate favorite tools (most used and highest rated)
        tool_usage = {}
        tool_ratings = {}

        for session in sessions:
            # Count usage
            if session.tool_name not in tool_usage:
                tool_usage[session.tool_name] = 0
            tool_usage[session.tool_name] += 1

            # Track ratings
            if session.helpfulness_rating:
                if session.tool_name not in tool_ratings:
                    tool_ratings[session.tool_name] = []
                tool_ratings[session.tool_name].append(session.helpfulness_rating)

        # Calculate average ratings
        avg_ratings = {}
        for tool_name, ratings in tool_ratings.items():
            avg_ratings[tool_name] = sum(ratings) / len(ratings)

        # Create favorite tools list
        favorite_tools = []
        for tool_name in tool_usage:
            favorite_tools.append({
                "tool_name": tool_name,
                "usage_count": tool_usage[tool_name],
                "average_rating": avg_ratings.get(tool_name),
                "total_ratings": len(tool_ratings.get(tool_name, []))
            })

        # Sort by usage and rating
        favorite_tools.sort(key=lambda x: (x["usage_count"], x["average_rating"] or 0), reverse=True)

        # Calculate effectiveness stats
        completed_sessions = [s for s in sessions if s.completed]
        total_sessions = len(sessions)

        effectiveness_stats = {
            "completion_rate": len(completed_sessions) / total_sessions if total_sessions > 0 else 0,
            "average_helpfulness": (
                sum(s.helpfulness_rating for s in completed_sessions if s.helpfulness_rating) /
                len([s for s in completed_sessions if s.helpfulness_rating])
                if any(s.helpfulness_rating for s in completed_sessions) else 0
            ),
            "mood_improvement_rate": 0,
            "most_effective_time": None
        }

        # Calculate mood improvement rate
        mood_improvements = []
        for session in completed_sessions:
            if session.pre_mood_score and session.post_mood_score:
                improvement = session.post_mood_score - session.pre_mood_score
                mood_improvements.append(improvement > 0)

        if mood_improvements:
            effectiveness_stats["mood_improvement_rate"] = sum(mood_improvements) / len(mood_improvements)

        return SessionHistoryResponse(
            sessions=session_data,
            total_sessions=total_sessions,
            favorite_tools=favorite_tools[:5],  # Top 5 favorite tools
            effectiveness_stats=effectiveness_stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve session history"
        )


@router.get("/stats", summary="Get coping tools statistics")
async def get_coping_stats():
    """Get statistics about available coping tools"""
    try:
        stats = coping_service.get_tool_stats()
        return stats

    except Exception as e:
        logger.error(f"Get coping stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve coping statistics"
        )


@router.get("/quick-tools", response_model=List[CopingToolResponse], summary="Get quick coping tools")
async def get_quick_tools(
    max_duration: int = Query(5, ge=1, le=15, description="Maximum duration in minutes")
):
    """Get coping tools that can be completed quickly"""
    try:
        quick_tools = coping_service.get_quick_tools(max_duration=max_duration)

        # Convert to response format
        tool_responses = []
        for tool in quick_tools:
            tool_responses.append(CopingToolResponse(
                id=tool.id,
                name=tool.name,
                type=tool.type.value,
                description=tool.description,
                target_emotions=[emotion.value for emotion in tool.target_emotions],
                duration_minutes=tool.duration_minutes,
                difficulty=tool.difficulty,
                instructions=tool.instructions,
                benefits=tool.benefits,
                requirements=tool.requirements,
                interactive=tool.interactive,
                guided_steps=tool.guided_steps
            ))

        return tool_responses

    except Exception as e:
        logger.error(f"Get quick tools error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve quick tools"
        )
