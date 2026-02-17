from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
import uuid

from app.database.database import get_db
from app.models.models import User, MoodLog, CopingSession, ChatHistory
from app.core.exceptions import UserNotFoundError, ConflictError
from app.core.logging import get_audit_logger, get_privacy_logger

router = APIRouter()
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()
privacy_logger = get_privacy_logger()


# Request/Response Models
class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    preferred_coping_tools: Optional[List[str]] = Field(default_factory=list, description="User's preferred coping tool types")
    notification_preferences: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "daily_checkin_reminder": True,
            "mood_trend_insights": True,
            "coping_tool_suggestions": True,
            "crisis_resources": True
        },
        description="User's notification preferences"
    )
    privacy_settings: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "store_chat_history": True,
            "anonymous_analytics": False,
            "share_mood_trends": False,
            "data_retention_months": 12
        },
        description="User's privacy settings"
    )

    @validator('preferred_coping_tools')
    def validate_coping_tools(cls, v):
        valid_types = ['breathing', 'grounding', 'mindfulness', 'journaling', 'physical', 'cognitive', 'relaxation', 'creativity', 'social']
        if v:
            for tool_type in v:
                if tool_type not in valid_types:
                    raise ValueError(f"Invalid coping tool type: {tool_type}. Must be one of: {valid_types}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "preferred_coping_tools": ["breathing", "mindfulness", "journaling"],
                "notification_preferences": {
                    "daily_checkin_reminder": True,
                    "mood_trend_insights": True,
                    "coping_tool_suggestions": True,
                    "crisis_resources": True
                },
                "privacy_settings": {
                    "store_chat_history": True,
                    "anonymous_analytics": False,
                    "share_mood_trends": False,
                    "data_retention_months": 12
                }
            }
        }


class UserResponse(BaseModel):
    """Response model for user data"""
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    streak_count: int
    last_check_in: Optional[datetime]
    total_check_ins: int
    is_active: bool
    first_login: Optional[datetime]
    last_activity: Optional[datetime]
    preferred_coping_tools: Optional[List[str]]
    notification_preferences: Optional[Dict[str, bool]]
    privacy_settings: Optional[Dict[str, bool]]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "streak_count": 7,
                "last_check_in": "2024-01-01T09:00:00Z",
                "total_check_ins": 25,
                "is_active": True,
                "first_login": "2024-01-01T00:00:00Z",
                "last_activity": "2024-01-01T12:00:00Z",
                "preferred_coping_tools": ["breathing", "mindfulness"],
                "notification_preferences": {
                    "daily_checkin_reminder": True,
                    "mood_trend_insights": True
                },
                "privacy_settings": {
                    "store_chat_history": True,
                    "anonymous_analytics": False
                }
            }
        }


class UserUpdateRequest(BaseModel):
    """Request model for updating user preferences"""
    preferred_coping_tools: Optional[List[str]] = Field(None, description="Updated preferred coping tools")
    notification_preferences: Optional[Dict[str, bool]] = Field(None, description="Updated notification preferences")
    privacy_settings: Optional[Dict[str, bool]] = Field(None, description="Updated privacy settings")

    @validator('preferred_coping_tools')
    def validate_coping_tools(cls, v):
        if v is not None:
            valid_types = ['breathing', 'grounding', 'mindfulness', 'journaling', 'physical', 'cognitive', 'relaxation', 'creativity', 'social']
            for tool_type in v:
                if tool_type not in valid_types:
                    raise ValueError(f"Invalid coping tool type: {tool_type}. Must be one of: {valid_types}")
        return v


class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    user_id: str
    account_age_days: int
    total_check_ins: int
    current_streak: int
    longest_streak: int
    total_mood_logs: int
    total_chat_sessions: int
    total_coping_sessions: int
    completed_coping_sessions: int
    average_mood_last_30_days: Optional[float]
    most_used_coping_tool: Optional[str]
    favorite_emotions: List[Dict[str, int]]
    activity_summary: Dict[str, Any]


class CheckInRequest(BaseModel):
    """Request model for daily check-in"""
    user_id: str = Field(..., description="User ID")
    mood_score: Optional[int] = Field(None, ge=1, le=5, description="Optional mood score")
    quick_note: Optional[str] = Field(None, max_length=200, description="Quick note about their day")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "mood_score": 3,
                "quick_note": "Feeling okay today, work was manageable"
            }
        }


class CheckInResponse(BaseModel):
    """Response model for daily check-in"""
    message: str
    streak_count: int
    total_check_ins: int
    encouragement: str
    suggested_activities: List[str]


@router.post("/register", response_model=UserResponse, summary="Register a new user")
async def register_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user in the system

    This endpoint creates a new user with default settings and preferences.
    The user is assigned a unique ID and default privacy/notification settings.
    """
    try:
        # Create new user with generated ID
        user = User(
            preferred_coping_tools=request.preferred_coping_tools,
            notification_preferences=request.notification_preferences,
            privacy_settings=request.privacy_settings,
            is_active=True,
            first_login=datetime.now()
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Log the registration
        audit_logger.log_user_action(
            user_id=user.user_id,
            action="user_registered",
            details={
                "preferred_tools_count": len(request.preferred_coping_tools) if request.preferred_coping_tools else 0,
                "notifications_enabled": sum(request.notification_preferences.values()) if request.notification_preferences else 0
            }
        )

        return UserResponse(
            user_id=user.user_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            streak_count=user.streak_count,
            last_check_in=user.last_check_in,
            total_check_ins=user.total_check_ins,
            is_active=user.is_active,
            first_login=user.first_login,
            last_activity=user.last_activity,
            preferred_coping_tools=user.preferred_coping_tools,
            notification_preferences=user.notification_preferences,
            privacy_settings=user.privacy_settings
        )

    except Exception as e:
        logger.error(f"User registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to register user"
        )


@router.get("/profile/{user_id}", response_model=UserResponse, summary="Get user profile")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Update last activity
        user.last_activity = datetime.now()
        db.commit()

        audit_logger.log_user_action(
            user_id=user_id,
            action="profile_accessed"
        )

        return UserResponse(
            user_id=user.user_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            streak_count=user.streak_count,
            last_check_in=user.last_check_in,
            total_check_ins=user.total_check_ins,
            is_active=user.is_active,
            first_login=user.first_login,
            last_activity=user.last_activity,
            preferred_coping_tools=user.preferred_coping_tools,
            notification_preferences=user.notification_preferences,
            privacy_settings=user.privacy_settings
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user profile"
        )


@router.put("/profile/{user_id}", response_model=UserResponse, summary="Update user profile")
async def update_user_profile(
    user_id: str,
    request: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update user profile and preferences"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Track what's being updated for logging
        updates = []

        # Update preferred coping tools
        if request.preferred_coping_tools is not None:
            user.preferred_coping_tools = request.preferred_coping_tools
            updates.append("preferred_coping_tools")

        # Update notification preferences
        if request.notification_preferences is not None:
            if user.notification_preferences:
                user.notification_preferences.update(request.notification_preferences)
            else:
                user.notification_preferences = request.notification_preferences
            updates.append("notification_preferences")

        # Update privacy settings
        if request.privacy_settings is not None:
            if user.privacy_settings:
                user.privacy_settings.update(request.privacy_settings)
            else:
                user.privacy_settings = request.privacy_settings
            updates.append("privacy_settings")

            # Log privacy setting changes
            privacy_logger.log_consent_change(
                user_id=user_id,
                consent_type="privacy_settings_updated",
                new_value=True
            )

        user.updated_at = datetime.now()
        user.last_activity = datetime.now()

        db.commit()
        db.refresh(user)

        audit_logger.log_user_action(
            user_id=user_id,
            action="profile_updated",
            details={"updated_fields": updates}
        )

        return UserResponse(
            user_id=user.user_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
            streak_count=user.streak_count,
            last_check_in=user.last_check_in,
            total_check_ins=user.total_check_ins,
            is_active=user.is_active,
            first_login=user.first_login,
            last_activity=user.last_activity,
            preferred_coping_tools=user.preferred_coping_tools,
            notification_preferences=user.notification_preferences,
            privacy_settings=user.privacy_settings
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update user profile"
        )


@router.post("/check-in", response_model=CheckInResponse, summary="Daily check-in")
async def daily_check_in(
    request: CheckInRequest,
    db: Session = Depends(get_db)
):
    """
    Process daily check-in for a user

    Updates the user's check-in streak and provides personalized encouragement
    """
    try:
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise UserNotFoundError(request.user_id)

        # Check if user already checked in today
        today = date.today()
        if user.last_check_in and user.last_check_in.date() == today:
            return CheckInResponse(
                message="You've already checked in today! Thanks for being consistent.",
                streak_count=user.streak_count,
                total_check_ins=user.total_check_ins,
                encouragement="Keep up the great work with your daily check-ins!",
                suggested_activities=["Review your mood trends", "Try a quick breathing exercise"]
            )

        # Update streak logic
        yesterday = today - timedelta(days=1)
        if user.last_check_in and user.last_check_in.date() == yesterday:
            # Continuing streak
            user.streak_count += 1
        elif user.last_check_in and user.last_check_in.date() < yesterday:
            # Streak broken, reset
            user.streak_count = 1
        else:
            # First check-in or same day
            user.streak_count = max(1, user.streak_count)

        # Update check-in data
        user.last_check_in = datetime.now()
        user.total_check_ins += 1
        user.last_activity = datetime.now()

        # If mood score is provided, create a quick mood log
        if request.mood_score:
            mood_log = MoodLog(
                user_id=request.user_id,
                mood_score=request.mood_score,
                emotion_category="neutral",  # Default for quick check-ins
                notes=request.quick_note,
                date_only=today.isoformat()
            )
            db.add(mood_log)

        db.commit()

        # Generate personalized encouragement
        encouragement = _generate_encouragement(user.streak_count, user.total_check_ins)

        # Generate suggested activities based on user preferences and history
        suggested_activities = _generate_suggested_activities(user, db)

        # Generate response message
        if user.streak_count == 1:
            message = "Welcome back! Great to see you checking in today."
        elif user.streak_count < 7:
            message = f"Nice! You're on a {user.streak_count}-day check-in streak."
        elif user.streak_count < 30:
            message = f"Fantastic! You've maintained a {user.streak_count}-day streak. You're building a great habit!"
        else:
            message = f"Incredible! {user.streak_count} days of consistent check-ins. You're a mental health champion!"

        audit_logger.log_user_action(
            user_id=request.user_id,
            action="daily_check_in",
            details={
                "streak_count": user.streak_count,
                "total_check_ins": user.total_check_ins,
                "has_mood_score": bool(request.mood_score),
                "has_note": bool(request.quick_note)
            }
        )

        return CheckInResponse(
            message=message,
            streak_count=user.streak_count,
            total_check_ins=user.total_check_ins,
            encouragement=encouragement,
            suggested_activities=suggested_activities
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily check-in error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process daily check-in"
        )


@router.get("/stats/{user_id}", response_model=UserStatsResponse, summary="Get user statistics")
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics for a user"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Calculate account age
        account_age = (datetime.now() - user.created_at).days

        # Get mood logs count
        mood_logs_count = db.query(MoodLog).filter(MoodLog.user_id == user_id).count()

        # Get chat sessions count (unique sessions)
        chat_sessions_count = db.query(ChatHistory.session_id).filter(
            ChatHistory.user_id == user_id
        ).distinct().count()

        # Get coping sessions stats
        total_coping_sessions = db.query(CopingSession).filter(
            CopingSession.user_id == user_id
        ).count()

        completed_coping_sessions = db.query(CopingSession).filter(
            CopingSession.user_id == user_id,
            CopingSession.completed == True
        ).count()

        # Calculate average mood for last 30 days
        thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
        recent_mood_logs = db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.date_only >= thirty_days_ago
        ).all()

        avg_mood_30_days = None
        if recent_mood_logs:
            mood_scores = [log.mood_score for log in recent_mood_logs]
            avg_mood_30_days = round(sum(mood_scores) / len(mood_scores), 2)

        # Find most used coping tool
        coping_sessions = db.query(CopingSession).filter(
            CopingSession.user_id == user_id
        ).all()

        tool_usage = {}
        for session in coping_sessions:
            tool_usage[session.tool_name] = tool_usage.get(session.tool_name, 0) + 1

        most_used_tool = max(tool_usage.items(), key=lambda x: x[1])[0] if tool_usage else None

        # Find favorite emotions (most logged)
        all_mood_logs = db.query(MoodLog).filter(MoodLog.user_id == user_id).all()
        emotion_counts = {}
        for log in all_mood_logs:
            emotion_counts[log.emotion_category] = emotion_counts.get(log.emotion_category, 0) + 1

        favorite_emotions = [
            {"emotion": emotion, "count": count}
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Calculate longest streak (this would need to be tracked over time)
        # For now, using current streak as approximation
        longest_streak = user.streak_count

        # Activity summary
        activity_summary = {
            "days_since_last_mood_log": (
                (datetime.now().date() - datetime.fromisoformat(recent_mood_logs[-1].date_only).date()).days
                if recent_mood_logs else None
            ),
            "days_since_last_chat": None,  # Would need to calculate from chat history
            "days_since_last_coping_session": (
                (datetime.now() - coping_sessions[-1].started_at).days
                if coping_sessions else None
            ),
            "most_active_time": _calculate_most_active_time(all_mood_logs),
            "engagement_level": _calculate_engagement_level(
                mood_logs_count, chat_sessions_count, total_coping_sessions, account_age
            )
        }

        audit_logger.log_user_action(
            user_id=user_id,
            action="stats_accessed"
        )

        return UserStatsResponse(
            user_id=user_id,
            account_age_days=account_age,
            total_check_ins=user.total_check_ins,
            current_streak=user.streak_count,
            longest_streak=longest_streak,
            total_mood_logs=mood_logs_count,
            total_chat_sessions=chat_sessions_count,
            total_coping_sessions=total_coping_sessions,
            completed_coping_sessions=completed_coping_sessions,
            average_mood_last_30_days=avg_mood_30_days,
            most_used_coping_tool=most_used_tool,
            favorite_emotions=favorite_emotions,
            activity_summary=activity_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user statistics"
        )


@router.delete("/account/{user_id}", summary="Delete user account")
async def delete_user_account(
    user_id: str,
    confirm: bool = Query(..., description="Confirmation that user wants to delete account"),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data

    This is a permanent action that cannot be undone.
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Account deletion requires confirmation"
            )

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Count records to be deleted
        mood_logs_count = db.query(MoodLog).filter(MoodLog.user_id == user_id).count()
        chat_history_count = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).count()
        coping_sessions_count = db.query(CopingSession).filter(CopingSession.user_id == user_id).count()

        # Delete all associated data (cascading delete should handle this)
        db.delete(user)
        db.commit()

        # Log the account deletion
        privacy_logger.log_data_deletion(
            user_id=user_id,
            data_types=["user_profile", "mood_logs", "chat_history", "coping_sessions"],
            reason="user_requested_account_deletion"
        )

        audit_logger.log_user_action(
            user_id=user_id,
            action="account_deleted",
            details={
                "mood_logs_deleted": mood_logs_count,
                "chat_records_deleted": chat_history_count,
                "coping_sessions_deleted": coping_sessions_count
            }
        )

        return {
            "message": "Account and all associated data have been permanently deleted",
            "deleted_data": {
                "user_profile": 1,
                "mood_logs": mood_logs_count,
                "chat_history": chat_history_count,
                "coping_sessions": coping_sessions_count
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user account error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user account"
        )


@router.post("/deactivate/{user_id}", summary="Deactivate user account")
async def deactivate_user_account(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate user account (soft delete - can be reactivated)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        user.is_active = False
        user.updated_at = datetime.now()

        db.commit()

        audit_logger.log_user_action(
            user_id=user_id,
            action="account_deactivated"
        )

        return {"message": "Account has been deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate account error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to deactivate account"
        )


@router.post("/reactivate/{user_id}", summary="Reactivate user account")
async def reactivate_user_account(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Reactivate a deactivated user account"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        user.is_active = True
        user.updated_at = datetime.now()
        user.last_activity = datetime.now()

        db.commit()

        audit_logger.log_user_action(
            user_id=user_id,
            action="account_reactivated"
        )

        return {"message": "Account has been reactivated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reactivate account error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to reactivate account"
        )


def _generate_encouragement(streak_count: int, total_check_ins: int) -> str:
    """Generate personalized encouragement message"""
    if streak_count == 1:
        return "Every journey begins with a single step. You're taking great care of your mental health!"
    elif streak_count < 7:
        return f"You're building momentum with {streak_count} consecutive days. Consistency is key to well-being!"
    elif streak_count < 30:
        return f"{streak_count} days in a row is fantastic! You're developing a powerful self-care habit."
    elif streak_count < 100:
        return f"Wow! {streak_count} days shows incredible dedication to your mental health journey."
    else:
        return f"You're absolutely incredible! {streak_count} days of consistent self-care is truly inspiring."


def _generate_suggested_activities(user: User, db: Session) -> List[str]:
    """Generate suggested activities based on user preferences and history"""
    suggestions = []

    # Base suggestions
    suggestions.append("Take a moment to reflect on your mood today")

    # Add suggestions based on preferred coping tools
    if user.preferred_coping_tools:
        if "breathing" in user.preferred_coping_tools:
            suggestions.append("Try a quick breathing exercise")
        if "mindfulness" in user.preferred_coping_tools:
            suggestions.append("Practice a short mindfulness meditation")
        if "journaling" in user.preferred_coping_tools:
            suggestions.append("Write down your thoughts in a journal")

    # Add time-based suggestions
    current_hour = datetime.now().hour
    if current_hour < 12:
        suggestions.append("Set a positive intention for your day")
    elif current_hour < 17:
        suggestions.append("Take a brief break to recharge")
    else:
        suggestions.append("Reflect on one good thing that happened today")

    return suggestions[:3]  # Return up to 3 suggestions


def _calculate_most_active_time(mood_logs: List[MoodLog]) -> Optional[str]:
    """Calculate the time of day when user is most active"""
    if not mood_logs:
        return None

    time_counts = {}
    for log in mood_logs:
        if log.time_of_day:
            time_counts[log.time_of_day] = time_counts.get(log.time_of_day, 0) + 1

    if time_counts:
        return max(time_counts.items(), key=lambda x: x[1])[0]
    return None


def _calculate_engagement_level(mood_logs: int, chat_sessions: int, coping_sessions: int, account_age: int) -> str:
    """Calculate user engagement level based on activity"""
    if account_age == 0:
        account_age = 1  # Avoid division by zero

    # Calculate activity per day
    daily_activity = (mood_logs + chat_sessions + coping_sessions) / account_age

    if daily_activity >= 2:
        return "high"
    elif daily_activity >= 1:
        return "medium"
    elif daily_activity >= 0.3:
        return "low"
    else:
        return "minimal"
