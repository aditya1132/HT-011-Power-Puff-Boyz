from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
from statistics import mean

from app.database.database import get_db
from app.models.models import User, MoodLog, EmotionCategory, MoodScale
from app.ai.emotion_detection import emotion_service
from app.core.exceptions import MoodLogNotFoundError, InvalidMoodDataError, UserNotFoundError
from app.core.logging import get_audit_logger

router = APIRouter()
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


# Request/Response Models
class MoodLogRequest(BaseModel):
    """Request model for logging mood"""
    user_id: str = Field(..., description="User ID")
    mood_score: int = Field(..., ge=1, le=5, description="Mood score on 1-5 scale")
    emotion_category: str = Field(..., description="Primary emotion category")
    notes: Optional[str] = Field(None, max_length=500, description="Optional user notes")
    triggers: Optional[List[str]] = Field(default_factory=list, description="Identified triggers")
    time_of_day: Optional[str] = Field(None, description="Time of day (morning, afternoon, evening, night)")
    social_context: Optional[str] = Field(None, description="Social context")
    weather_impact: Optional[str] = Field(None, description="Weather impact if relevant")

    @validator('emotion_category')
    def validate_emotion_category(cls, v):
        valid_emotions = [e.value for e in EmotionCategory]
        if v not in valid_emotions:
            raise ValueError(f"Invalid emotion category. Must be one of: {valid_emotions}")
        return v

    @validator('time_of_day')
    def validate_time_of_day(cls, v):
        if v is not None:
            valid_times = ['morning', 'afternoon', 'evening', 'night']
            if v not in valid_times:
                raise ValueError(f"Invalid time_of_day. Must be one of: {valid_times}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "mood_score": 3,
                "emotion_category": "stressed",
                "notes": "Work was overwhelming today, but I managed to get through it",
                "triggers": ["work", "deadline"],
                "time_of_day": "evening",
                "social_context": "alone",
                "weather_impact": "rainy"
            }
        }


class MoodLogResponse(BaseModel):
    """Response model for mood log"""
    log_id: str
    user_id: str
    mood_score: int
    emotion_category: str
    secondary_emotions: Optional[List[str]]
    notes: Optional[str]
    triggers: Optional[List[str]]
    timestamp: datetime
    date_only: str
    ai_confidence: Optional[float]
    suggested_activities: Optional[List[str]]
    time_of_day: Optional[str]
    social_context: Optional[str]
    weather_impact: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "log_id": "log_123",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "mood_score": 3,
                "emotion_category": "stressed",
                "secondary_emotions": ["anxious"],
                "notes": "Work was overwhelming today",
                "triggers": ["work", "deadline"],
                "timestamp": "2024-01-01T18:00:00Z",
                "date_only": "2024-01-01",
                "ai_confidence": 0.85,
                "suggested_activities": ["breathing_exercise", "walk"],
                "time_of_day": "evening",
                "social_context": "alone",
                "weather_impact": "rainy"
            }
        }


class MoodTrendResponse(BaseModel):
    """Response model for mood trends"""
    user_id: str
    date_range: Dict[str, str]
    average_mood: float
    mood_trend: str  # improving, declining, stable
    most_common_emotion: str
    mood_logs: List[MoodLogResponse]
    insights: Dict[str, Any]
    recommendations: List[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "date_range": {"start": "2024-01-01", "end": "2024-01-07"},
                "average_mood": 3.2,
                "mood_trend": "stable",
                "most_common_emotion": "stressed",
                "mood_logs": [],
                "insights": {
                    "best_day": {"date": "2024-01-03", "mood_score": 4},
                    "worst_day": {"date": "2024-01-01", "mood_score": 2},
                    "common_triggers": ["work", "sleep"],
                    "mood_by_time": {"morning": 3.5, "evening": 2.8}
                },
                "recommendations": ["Try morning meditation", "Consider evening routine"]
            }
        }


class DailyMoodSummary(BaseModel):
    """Daily mood summary model"""
    date: str
    mood_score: Optional[int]
    emotion_category: Optional[str]
    notes_count: int
    triggers_count: int


class MoodStatsResponse(BaseModel):
    """Response model for mood statistics"""
    user_id: str
    total_logs: int
    logging_streak: int
    average_mood_last_30_days: float
    emotion_distribution: Dict[str, int]
    mood_by_time_of_day: Dict[str, float]
    common_triggers: List[Dict[str, int]]
    daily_summaries: List[DailyMoodSummary]


@router.post("/log", response_model=MoodLogResponse, summary="Log daily mood")
async def log_mood(
    request: MoodLogRequest,
    db: Session = Depends(get_db)
):
    """
    Log a mood entry for a user

    This endpoint:
    1. Validates the user and mood data
    2. Creates a new mood log entry
    3. Updates user's check-in streak if it's their first log today
    4. Provides AI-generated activity suggestions
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise UserNotFoundError(request.user_id)

        # Get today's date
        today = date.today().isoformat()

        # Check if user already logged mood today
        existing_log = db.query(MoodLog).filter(
            and_(
                MoodLog.user_id == request.user_id,
                MoodLog.date_only == today
            )
        ).first()

        # If this is their first log today, update streak
        if not existing_log:
            # Check if they logged yesterday
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            yesterday_log = db.query(MoodLog).filter(
                and_(
                    MoodLog.user_id == request.user_id,
                    MoodLog.date_only == yesterday
                )
            ).first()

            if yesterday_log:
                user.streak_count += 1
            else:
                user.streak_count = 1  # Reset streak if they missed yesterday

            user.total_check_ins += 1
            user.last_check_in = datetime.now()

        # Generate AI suggestions based on mood and emotion
        suggested_activities = []
        ai_confidence = None

        if request.notes:
            try:
                # Analyze the notes for additional insights
                emotion_result = emotion_service.analyze_emotion(request.notes)
                ai_confidence = emotion_result.confidence

                # Get activity suggestions based on detected emotion
                from app.ai.coping_tools import coping_service
                tools = coping_service.get_tools_for_emotion(
                    emotion_result.primary_emotion,
                    difficulty="easy",
                    max_duration=15
                )
                suggested_activities = [tool.name for tool in tools[:3]]

            except Exception as e:
                logger.warning(f"Failed to generate AI suggestions: {e}")

        # Create mood log entry
        mood_log = MoodLog(
            user_id=request.user_id,
            mood_score=request.mood_score,
            emotion_category=request.emotion_category,
            notes=request.notes,
            triggers=request.triggers,
            date_only=today,
            time_of_day=request.time_of_day,
            social_context=request.social_context,
            weather_impact=request.weather_impact,
            ai_confidence=ai_confidence,
            suggested_activities=suggested_activities
        )

        db.add(mood_log)
        db.commit()
        db.refresh(mood_log)

        # Log the action
        audit_logger.log_user_action(
            user_id=request.user_id,
            action="mood_logged",
            details={
                "mood_score": request.mood_score,
                "emotion": request.emotion_category,
                "has_notes": bool(request.notes),
                "triggers_count": len(request.triggers) if request.triggers else 0
            }
        )

        return MoodLogResponse(
            log_id=mood_log.log_id,
            user_id=mood_log.user_id,
            mood_score=mood_log.mood_score,
            emotion_category=mood_log.emotion_category,
            secondary_emotions=mood_log.secondary_emotions,
            notes=mood_log.notes,
            triggers=mood_log.triggers,
            timestamp=mood_log.timestamp,
            date_only=mood_log.date_only,
            ai_confidence=mood_log.ai_confidence,
            suggested_activities=mood_log.suggested_activities,
            time_of_day=mood_log.time_of_day,
            social_context=mood_log.social_context,
            weather_impact=mood_log.weather_impact
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mood logging error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to log mood entry"
        )


@router.get("/history/{user_id}", response_model=List[MoodLogResponse], summary="Get mood history")
async def get_mood_history(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """Get mood history for a user over specified number of days"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get mood logs
        mood_logs = db.query(MoodLog).filter(
            and_(
                MoodLog.user_id == user_id,
                MoodLog.date_only >= start_date.isoformat(),
                MoodLog.date_only <= end_date.isoformat()
            )
        ).order_by(desc(MoodLog.timestamp)).all()

        # Convert to response format
        response_data = []
        for log in mood_logs:
            response_data.append(MoodLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                mood_score=log.mood_score,
                emotion_category=log.emotion_category,
                secondary_emotions=log.secondary_emotions,
                notes=log.notes,
                triggers=log.triggers,
                timestamp=log.timestamp,
                date_only=log.date_only,
                ai_confidence=log.ai_confidence,
                suggested_activities=log.suggested_activities,
                time_of_day=log.time_of_day,
                social_context=log.social_context,
                weather_impact=log.weather_impact
            ))

        audit_logger.log_user_action(
            user_id=user_id,
            action="mood_history_accessed",
            details={"days_requested": days, "logs_found": len(response_data)}
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mood history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve mood history"
        )


@router.get("/trends/{user_id}", response_model=MoodTrendResponse, summary="Get mood trends")
async def get_mood_trends(
    user_id: str,
    days: int = Query(30, ge=7, le=365, description="Number of days for trend analysis"),
    db: Session = Depends(get_db)
):
    """Analyze mood trends over time with insights and recommendations"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get mood logs
        mood_logs = db.query(MoodLog).filter(
            and_(
                MoodLog.user_id == user_id,
                MoodLog.date_only >= start_date.isoformat(),
                MoodLog.date_only <= end_date.isoformat()
            )
        ).order_by(MoodLog.timestamp).all()

        if not mood_logs:
            raise HTTPException(
                status_code=404,
                detail="No mood data found for the specified period"
            )

        # Convert mood logs to response format
        mood_log_responses = []
        for log in mood_logs:
            mood_log_responses.append(MoodLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                mood_score=log.mood_score,
                emotion_category=log.emotion_category,
                secondary_emotions=log.secondary_emotions,
                notes=log.notes,
                triggers=log.triggers,
                timestamp=log.timestamp,
                date_only=log.date_only,
                ai_confidence=log.ai_confidence,
                suggested_activities=log.suggested_activities,
                time_of_day=log.time_of_day,
                social_context=log.social_context,
                weather_impact=log.weather_impact
            ))

        # Calculate average mood
        mood_scores = [log.mood_score for log in mood_logs]
        average_mood = round(mean(mood_scores), 2)

        # Determine mood trend
        if len(mood_scores) >= 7:
            first_week_avg = mean(mood_scores[:7])
            last_week_avg = mean(mood_scores[-7:])

            if last_week_avg > first_week_avg + 0.3:
                mood_trend = "improving"
            elif last_week_avg < first_week_avg - 0.3:
                mood_trend = "declining"
            else:
                mood_trend = "stable"
        else:
            mood_trend = "stable"

        # Find most common emotion
        emotions = [log.emotion_category for log in mood_logs]
        most_common_emotion = max(set(emotions), key=emotions.count)

        # Generate insights
        insights = _generate_mood_insights(mood_logs)

        # Generate recommendations
        recommendations = _generate_recommendations(mood_logs, mood_trend, most_common_emotion)

        audit_logger.log_user_action(
            user_id=user_id,
            action="mood_trends_accessed",
            details={"days_analyzed": days, "trend": mood_trend}
        )

        return MoodTrendResponse(
            user_id=user_id,
            date_range={
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            average_mood=average_mood,
            mood_trend=mood_trend,
            most_common_emotion=most_common_emotion,
            mood_logs=mood_log_responses,
            insights=insights,
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mood trends error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze mood trends"
        )


@router.get("/stats/{user_id}", response_model=MoodStatsResponse, summary="Get mood statistics")
async def get_mood_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive mood statistics for a user"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise UserNotFoundError(user_id)

        # Get all mood logs for the user
        total_logs = db.query(MoodLog).filter(MoodLog.user_id == user_id).count()

        # Get last 30 days mood data
        thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
        recent_logs = db.query(MoodLog).filter(
            and_(
                MoodLog.user_id == user_id,
                MoodLog.date_only >= thirty_days_ago
            )
        ).all()

        # Calculate average mood for last 30 days
        if recent_logs:
            avg_mood_30_days = round(mean([log.mood_score for log in recent_logs]), 2)
        else:
            avg_mood_30_days = 0.0

        # Emotion distribution
        all_logs = db.query(MoodLog).filter(MoodLog.user_id == user_id).all()
        emotion_dist = {}
        for log in all_logs:
            emotion_dist[log.emotion_category] = emotion_dist.get(log.emotion_category, 0) + 1

        # Mood by time of day
        mood_by_time = {}
        time_counts = {}
        for log in all_logs:
            if log.time_of_day:
                if log.time_of_day not in mood_by_time:
                    mood_by_time[log.time_of_day] = 0
                    time_counts[log.time_of_day] = 0
                mood_by_time[log.time_of_day] += log.mood_score
                time_counts[log.time_of_day] += 1

        # Calculate averages
        for time_period in mood_by_time:
            mood_by_time[time_period] = round(mood_by_time[time_period] / time_counts[time_period], 2)

        # Common triggers
        trigger_counts = {}
        for log in all_logs:
            if log.triggers:
                for trigger in log.triggers:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        common_triggers = [
            {"trigger": trigger, "count": count}
            for trigger, count in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Daily summaries for last 30 days
        daily_summaries = []
        for i in range(30):
            check_date = (date.today() - timedelta(days=i)).isoformat()
            day_log = next((log for log in recent_logs if log.date_only == check_date), None)

            daily_summaries.append(DailyMoodSummary(
                date=check_date,
                mood_score=day_log.mood_score if day_log else None,
                emotion_category=day_log.emotion_category if day_log else None,
                notes_count=1 if day_log and day_log.notes else 0,
                triggers_count=len(day_log.triggers) if day_log and day_log.triggers else 0
            ))

        return MoodStatsResponse(
            user_id=user_id,
            total_logs=total_logs,
            logging_streak=user.streak_count,
            average_mood_last_30_days=avg_mood_30_days,
            emotion_distribution=emotion_dist,
            mood_by_time_of_day=mood_by_time,
            common_triggers=common_triggers,
            daily_summaries=daily_summaries
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mood stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve mood statistics"
        )


@router.put("/log/{log_id}", response_model=MoodLogResponse, summary="Update mood log")
async def update_mood_log(
    log_id: str,
    request: MoodLogRequest,
    db: Session = Depends(get_db)
):
    """Update an existing mood log entry"""
    try:
        # Find the mood log
        mood_log = db.query(MoodLog).filter(MoodLog.log_id == log_id).first()
        if not mood_log:
            raise MoodLogNotFoundError(log_id)

        # Verify user owns this log
        if mood_log.user_id != request.user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update the mood log
        mood_log.mood_score = request.mood_score
        mood_log.emotion_category = request.emotion_category
        mood_log.notes = request.notes
        mood_log.triggers = request.triggers
        mood_log.time_of_day = request.time_of_day
        mood_log.social_context = request.social_context
        mood_log.weather_impact = request.weather_impact

        db.commit()
        db.refresh(mood_log)

        audit_logger.log_user_action(
            user_id=request.user_id,
            action="mood_log_updated",
            details={"log_id": log_id}
        )

        return MoodLogResponse(
            log_id=mood_log.log_id,
            user_id=mood_log.user_id,
            mood_score=mood_log.mood_score,
            emotion_category=mood_log.emotion_category,
            secondary_emotions=mood_log.secondary_emotions,
            notes=mood_log.notes,
            triggers=mood_log.triggers,
            timestamp=mood_log.timestamp,
            date_only=mood_log.date_only,
            ai_confidence=mood_log.ai_confidence,
            suggested_activities=mood_log.suggested_activities,
            time_of_day=mood_log.time_of_day,
            social_context=mood_log.social_context,
            weather_impact=mood_log.weather_impact
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update mood log error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update mood log"
        )


@router.delete("/log/{log_id}", summary="Delete mood log")
async def delete_mood_log(
    log_id: str,
    user_id: str = Query(..., description="User ID for verification"),
    db: Session = Depends(get_db)
):
    """Delete a mood log entry"""
    try:
        # Find the mood log
        mood_log = db.query(MoodLog).filter(MoodLog.log_id == log_id).first()
        if not mood_log:
            raise MoodLogNotFoundError(log_id)

        # Verify user owns this log
        if mood_log.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete the mood log
        db.delete(mood_log)
        db.commit()

        audit_logger.log_user_action(
            user_id=user_id,
            action="mood_log_deleted",
            details={"log_id": log_id}
        )

        return {"message": "Mood log deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete mood log error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete mood log"
        )


def _generate_mood_insights(mood_logs: List[MoodLog]) -> Dict[str, Any]:
    """Generate insights from mood data"""
    if not mood_logs:
        return {}

    # Find best and worst days
    best_day = max(mood_logs, key=lambda x: x.mood_score)
    worst_day = min(mood_logs, key=lambda x: x.mood_score)

    # Analyze triggers
    all_triggers = []
    for log in mood_logs:
        if log.triggers:
            all_triggers.extend(log.triggers)

    trigger_counts = {}
    for trigger in all_triggers:
        trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

    common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]

    # Mood by time of day
    mood_by_time = {}
    time_counts = {}
    for log in mood_logs:
        if log.time_of_day:
            if log.time_of_day not in mood_by_time:
                mood_by_time[log.time_of_day] = 0
                time_counts[log.time_of_day] = 0
            mood_by_time[log.time_of_day] += log.mood_score
            time_counts[log.time_of_day] += 1

    for time_period in mood_by_time:
        mood_by_time[time_period] = round(mood_by_time[time_period] / time_counts[time_period], 2)

    return {
        "best_day": {
            "date": best_day.date_only,
            "mood_score": best_day.mood_score,
            "emotion": best_day.emotion_category
        },
        "worst_day": {
            "date": worst_day.date_only,
            "mood_score": worst_day.mood_score,
            "emotion": worst_day.emotion_category
        },
        "common_triggers": [{"trigger": t[0], "count": t[1]} for t in common_triggers],
        "mood_by_time": mood_by_time,
        "total_entries": len(mood_logs),
        "days_with_notes": len([log for log in mood_logs if log.notes])
    }


def _generate_recommendations(mood_logs: List[MoodLog], trend: str, common_emotion: str) -> List[str]:
    """Generate personalized recommendations based on mood data"""
    recommendations = []

    # Trend-based recommendations
    if trend == "declining":
        recommendations.append("Consider talking to a mental health professional about your recent mood patterns")
        recommendations.append("Try incorporating more self-care activities into your daily routine")
    elif trend == "improving":
        recommendations.append("Great job maintaining positive habits - keep up what's working!")

    # Emotion-based recommendations
    emotion_recommendations = {
        "stressed": [
            "Try scheduling regular relaxation breaks throughout your day",
            "Consider stress management techniques like deep breathing or meditation"
        ],
        "anxious": [
            "Practice grounding techniques when you feel anxious",
            "Consider limiting caffeine intake which can worsen anxiety"
        ],
        "sad": [
            "Engage in activities that typically bring you joy",
            "Reach out to supportive friends or family members"
        ],
        "overwhelmed": [
            "Break large tasks into smaller, manageable steps",
            "Practice saying no to additional commitments when needed"
        ]
    }

    if common_emotion in emotion_recommendations:
        recommendations.extend(emotion_recommendations[common_emotion])

    # Data pattern recommendations
    if len(mood_logs) < 7:
        recommendations.append("Try to log your mood daily for better insights into your patterns")

    # Time-based recommendations
    time_moods = {}
    for log in mood_logs:
        if log.time_of_day:
            if log.time_of_day not in time_moods:
                time_moods[log.time_of_day] = []
            time_moods[log.time_of_day].append(log.mood_score)

    for time_period, scores in time_moods.items():
        if mean(scores) < 2.5:
            recommendations.append(f"Your mood tends to be lower in the {time_period} - consider planning supportive activities during this time")

    return recommendations[:5]  # Limit to 5 recommendations
