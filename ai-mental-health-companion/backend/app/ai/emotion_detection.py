import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import get_settings
from app.core.exceptions import AIServiceError, EmotionDetectionError

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class EmotionResult:
    """Data class for emotion detection results"""

    primary_emotion: str
    confidence: float
    secondary_emotions: List[Tuple[str, float]]
    sentiment_score: float
    intensity: str
    keywords_matched: List[str]
    processing_time_ms: float
    source: str = "rule_based"  # 'rule_based', 'gemini', 'hybrid'
    crisis_indicators: bool = False
    safety_flags: List[str] = None

    def __post_init__(self):
        if self.safety_flags is None:
            self.safety_flags = []


class EmotionKeywords:
    """Emotion keyword patterns and rules"""

    # Primary emotion keywords with weights
    EMOTION_PATTERNS = {
        "stressed": {
            "keywords": [
                "stressed",
                "pressure",
                "overwhelmed",
                "burden",
                "deadline",
                "anxiety",
                "panic",
                "worried",
                "tense",
                "exhausted",
                "can't handle",
                "too much",
                "breaking point",
                "falling behind",
            ],
            "phrases": [
                r"feel\s+stressed",
                r"under\s+pressure",
                r"so\s+much\s+work",
                r"can't\s+cope",
                r"burning\s+out",
                r"at\s+my\s+limit",
            ],
            "intensifiers": ["extremely", "really", "so", "very", "incredibly"],
            "weight": 1.0,
        },
        "anxious": {
            "keywords": [
                "anxious",
                "nervous",
                "worry",
                "fear",
                "scared",
                "afraid",
                "panic",
                "restless",
                "uneasy",
                "apprehensive",
                "jittery",
                "what if",
                "catastrophic",
                "worst case",
                "can't stop thinking",
            ],
            "phrases": [
                r"feel\s+anxious",
                r"can't\s+stop\s+worrying",
                r"panic\s+attack",
                r"racing\s+thoughts",
                r"heart\s+racing",
                r"sweaty\s+palms",
            ],
            "intensifiers": ["extremely", "really", "so", "very", "incredibly"],
            "weight": 1.0,
        },
        "sad": {
            "keywords": [
                "sad",
                "depressed",
                "down",
                "blue",
                "melancholy",
                "gloomy",
                "unhappy",
                "miserable",
                "heartbroken",
                "disappointed",
                "crying",
                "tears",
                "empty",
                "lonely",
                "hopeless",
            ],
            "phrases": [
                r"feel\s+sad",
                r"feeling\s+down",
                r"can't\s+stop\s+crying",
                r"feel\s+empty",
                r"so\s+alone",
                r"lost\s+hope",
            ],
            "intensifiers": ["extremely", "really", "so", "very", "deeply"],
            "weight": 1.0,
        },
        "overwhelmed": {
            "keywords": [
                "overwhelmed",
                "too much",
                "can't handle",
                "drowning",
                "swamped",
                "buried",
                "crushed",
                "suffocated",
                "flooded",
                "overloaded",
                "breaking point",
                "at capacity",
            ],
            "phrases": [
                r"feel\s+overwhelmed",
                r"too\s+much\s+to\s+handle",
                r"drowning\s+in",
                r"can't\s+keep\s+up",
                r"falling\s+behind",
            ],
            "intensifiers": ["completely", "totally", "absolutely", "utterly"],
            "weight": 1.0,
        },
        "angry": {
            "keywords": [
                "angry",
                "mad",
                "furious",
                "rage",
                "irritated",
                "annoyed",
                "frustrated",
                "pissed",
                "livid",
                "outraged",
                "fed up",
                "hate",
                "disgusted",
                "resentful",
            ],
            "phrases": [
                r"so\s+angry",
                r"fed\s+up",
                r"can't\s+stand",
                r"makes\s+me\s+mad",
                r"losing\s+my\s+temper",
                r"want\s+to\s+scream",
            ],
            "intensifiers": ["extremely", "really", "so", "very", "incredibly"],
            "weight": 0.9,
        },
        "excited": {
            "keywords": [
                "excited",
                "thrilled",
                "ecstatic",
                "elated",
                "overjoyed",
                "amazing",
                "awesome",
                "fantastic",
                "wonderful",
                "great",
                "love",
                "happy",
                "joy",
                "delighted",
                "pumped",
            ],
            "phrases": [
                r"so\s+excited",
                r"can't\s+wait",
                r"over\s+the\s+moon",
                r"feel\s+amazing",
                r"best\s+day\s+ever",
            ],
            "intensifiers": ["extremely", "really", "so", "very", "incredibly"],
            "weight": 0.8,
        },
        "positive": {
            "keywords": [
                "good",
                "fine",
                "okay",
                "alright",
                "decent",
                "content",
                "satisfied",
                "peaceful",
                "calm",
                "grateful",
                "thankful",
                "blessed",
                "optimistic",
                "hopeful",
            ],
            "phrases": [
                r"feel\s+good",
                r"doing\s+well",
                r"things\s+are\s+okay",
                r"feeling\s+better",
                r"grateful\s+for",
            ],
            "intensifiers": ["really", "pretty", "quite", "fairly"],
            "weight": 0.7,
        },
        "neutral": {
            "keywords": [
                "neutral",
                "normal",
                "average",
                "routine",
                "typical",
                "nothing special",
                "same as usual",
                "meh",
                "whatever",
            ],
            "phrases": [
                r"nothing\s+special",
                r"same\s+as\s+usual",
                r"pretty\s+normal",
                r"just\s+okay",
                r"not\s+much\s+happening",
            ],
            "intensifiers": [],
            "weight": 0.5,
        },
        "confused": {
            "keywords": [
                "confused",
                "lost",
                "uncertain",
                "unclear",
                "puzzled",
                "bewildered",
                "mixed up",
                "don't understand",
                "not sure",
                "complicated",
                "conflicted",
            ],
            "phrases": [
                r"don't\s+understand",
                r"not\s+sure\s+what",
                r"feel\s+lost",
                r"mixed\s+feelings",
                r"don't\s+know\s+what",
            ],
            "intensifiers": ["really", "completely", "totally", "so"],
            "weight": 0.6,
        },
        "grateful": {
            "keywords": [
                "grateful",
                "thankful",
                "blessed",
                "appreciate",
                "lucky",
                "fortunate",
                "thank you",
                "thanks",
                "bless",
                "appreciate",
            ],
            "phrases": [
                r"feel\s+grateful",
                r"so\s+thankful",
                r"feel\s+blessed",
                r"appreciate\s+that",
                r"lucky\s+to\s+have",
            ],
            "intensifiers": ["really", "so", "very", "deeply"],
            "weight": 0.8,
        },
    }

    # Crisis detection keywords (higher priority)
    CRISIS_KEYWORDS = [
        "suicide",
        "kill myself",
        "end my life",
        "hurt myself",
        "self harm",
        "cutting",
        "overdose",
        "die",
        "death wish",
        "worthless",
        "hopeless",
        "can't go on",
        "no point in living",
        "want to disappear",
        "better off dead",
        "end it all",
        "can't take it anymore",
    ]

    # Intensity modifiers
    INTENSITY_MODIFIERS = {
        "extreme": ["extremely", "incredibly", "utterly", "completely", "totally"],
        "high": ["very", "really", "so", "quite", "pretty"],
        "medium": ["somewhat", "kind of", "sort of", "a bit", "slightly"],
        "low": ["barely", "hardly", "just", "only", "merely"],
    }


class RuleBasedEmotionDetector:
    """Rule-based emotion detection using keywords and patterns"""

    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.emotion_keywords = EmotionKeywords()

    def detect_emotion(self, text: str) -> EmotionResult:
        """
        Detect emotion from text using rule-based approach

        Args:
            text: Input text to analyze

        Returns:
            EmotionResult with detected emotions and confidence
        """
        start_time = datetime.now()

        try:
            # Preprocess text
            text_lower = text.lower().strip()
            text_clean = re.sub(r"[^\w\s]", " ", text_lower)

            # Get sentiment analysis
            sentiment_scores = self._analyze_sentiment(text_lower)

            # Detect emotions using keywords
            emotion_scores = self._calculate_emotion_scores(text_clean, text_lower)

            # Apply sentiment weighting
            emotion_scores = self._apply_sentiment_weighting(
                emotion_scores, sentiment_scores
            )

            # Determine primary emotion
            primary_emotion = self._get_primary_emotion(emotion_scores)

            # Calculate confidence
            confidence = self._calculate_confidence(emotion_scores, text_clean)

            # Get secondary emotions
            secondary_emotions = self._get_secondary_emotions(
                emotion_scores, primary_emotion
            )

            # Get intensity
            intensity = self._determine_intensity(text_lower, primary_emotion)

            # Get matched keywords
            keywords_matched = self._get_matched_keywords(text_clean, primary_emotion)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return EmotionResult(
                primary_emotion=primary_emotion,
                confidence=confidence,
                secondary_emotions=secondary_emotions,
                sentiment_score=sentiment_scores["compound"],
                intensity=intensity,
                keywords_matched=keywords_matched,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            raise EmotionDetectionError(f"Failed to analyze emotion: {str(e)}")

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            vader_scores = self.vader_analyzer.polarity_scores(text)

            return {
                "compound": vader_scores["compound"],
                "positive": vader_scores["pos"],
                "negative": vader_scores["neg"],
                "neutral": vader_scores["neu"],
                "polarity": polarity,
                "subjectivity": subjectivity,
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {
                "compound": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "polarity": 0.0,
                "subjectivity": 0.0,
            }

    def _calculate_emotion_scores(
        self, text_clean: str, text_lower: str
    ) -> Dict[str, float]:
        """Calculate scores for each emotion category"""
        emotion_scores = {}

        for emotion, data in self.emotion_keywords.EMOTION_PATTERNS.items():
            score = 0.0

            # Check keywords
            for keyword in data["keywords"]:
                if keyword in text_clean:
                    score += data["weight"]

            # Check phrases using regex
            for phrase_pattern in data.get("phrases", []):
                if re.search(phrase_pattern, text_lower):
                    score += data["weight"] * 1.5  # Phrases get higher weight

            # Apply intensifier bonus
            for intensifier in data.get("intensifiers", []):
                if intensifier in text_lower:
                    score *= 1.3  # Boost score by 30%

            emotion_scores[emotion] = score

        return emotion_scores

    def _apply_sentiment_weighting(
        self, emotion_scores: Dict[str, float], sentiment: Dict[str, float]
    ) -> Dict[str, float]:
        """Apply sentiment analysis to weight emotions"""
        compound_score = sentiment["compound"]

        # Boost negative emotions if sentiment is negative
        if compound_score < -0.1:
            negative_emotions = ["sad", "anxious", "stressed", "overwhelmed", "angry"]
            for emotion in negative_emotions:
                if emotion in emotion_scores:
                    emotion_scores[emotion] *= 1 + abs(compound_score)

        # Boost positive emotions if sentiment is positive
        elif compound_score > 0.1:
            positive_emotions = ["excited", "positive", "grateful"]
            for emotion in positive_emotions:
                if emotion in emotion_scores:
                    emotion_scores[emotion] *= 1 + compound_score

        return emotion_scores

    def _get_primary_emotion(self, emotion_scores: Dict[str, float]) -> str:
        """Determine primary emotion from scores"""
        if not emotion_scores or all(score == 0 for score in emotion_scores.values()):
            return "neutral"

        # Get emotion with highest score
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])

        # If score is too low, default to neutral
        if primary_emotion[1] < 0.3:
            return "neutral"

        return primary_emotion[0]

    def _calculate_confidence(
        self, emotion_scores: Dict[str, float], text: str
    ) -> float:
        """Calculate confidence in emotion detection"""
        if not emotion_scores:
            return 0.0

        max_score = max(emotion_scores.values()) if emotion_scores else 0
        total_score = sum(emotion_scores.values())

        # Base confidence from score ratio
        if total_score == 0:
            confidence = 0.0
        else:
            confidence = max_score / total_score

        # Boost confidence for longer text
        text_length_factor = min(1.0, len(text.split()) / 10)
        confidence *= 0.5 + 0.5 * text_length_factor

        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))

    def _get_secondary_emotions(
        self, emotion_scores: Dict[str, float], primary_emotion: str
    ) -> List[Tuple[str, float]]:
        """Get secondary emotions with scores"""
        secondary = []

        for emotion, score in emotion_scores.items():
            if emotion != primary_emotion and score > 0.2:
                # Normalize score relative to primary emotion
                normalized_score = min(0.9, score / max(emotion_scores.values()))
                secondary.append((emotion, normalized_score))

        # Sort by score and return top 3
        secondary.sort(key=lambda x: x[1], reverse=True)
        return secondary[:3]

    def _determine_intensity(self, text: str, emotion: str) -> str:
        """Determine intensity of detected emotion"""
        intensity_scores = {"low": 0, "medium": 0, "high": 0, "extreme": 0}

        for level, modifiers in self.emotion_keywords.INTENSITY_MODIFIERS.items():
            for modifier in modifiers:
                if modifier in text:
                    intensity_scores[level] += 1

        # Determine intensity level
        max_intensity = max(intensity_scores.items(), key=lambda x: x[1])

        if max_intensity[1] == 0:
            return "medium"  # Default intensity

        return max_intensity[0]

    def _get_matched_keywords(self, text: str, emotion: str) -> List[str]:
        """Get list of keywords that matched for the primary emotion"""
        matched = []

        if emotion in self.emotion_keywords.EMOTION_PATTERNS:
            emotion_data = self.emotion_keywords.EMOTION_PATTERNS[emotion]

            for keyword in emotion_data["keywords"]:
                if keyword in text:
                    matched.append(keyword)

        return matched[:5]  # Return top 5 matches

    def detect_crisis_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect crisis-related keywords in text

        Args:
            text: Input text to check

        Returns:
            Tuple of (crisis_detected, matched_keywords)
        """
        text_lower = text.lower()
        matched_keywords = []

        for keyword in self.emotion_keywords.CRISIS_KEYWORDS:
            if keyword in text_lower:
                matched_keywords.append(keyword)

        return len(matched_keywords) > 0, matched_keywords


class MLEmotionDetector:
    """Machine learning-based emotion detection (placeholder for future implementation)"""

    def __init__(self):
        self.model = None  # Placeholder for ML model
        self.is_available = False

    def detect_emotion(self, text: str) -> EmotionResult:
        """
        Detect emotion using ML model (not implemented yet)
        Falls back to rule-based detection
        """
        if not self.is_available:
            logger.warning(
                "ML emotion detection not available, falling back to rule-based"
            )
            rule_detector = RuleBasedEmotionDetector()
            return rule_detector.detect_emotion(text)

        # TODO: Implement ML-based emotion detection
        # This would involve:
        # 1. Loading a pre-trained model (e.g., from HuggingFace)
        # 2. Preprocessing text for the model
        # 3. Running inference
        # 4. Post-processing results
        raise NotImplementedError("ML emotion detection not yet implemented")


class EmotionDetectionService:
    """Main service for emotion detection with multiple approaches"""

    def __init__(self):
        self.rule_detector = RuleBasedEmotionDetector()
        self.ml_detector = MLEmotionDetector()
        self.settings = get_settings()
        self._gemini_service = None

    @property
    def gemini_service(self):
        """Lazy loading of Gemini service to avoid circular imports"""
        if self._gemini_service is None:
            try:
                from app.ai.gemini_service import gemini_service

                self._gemini_service = gemini_service
            except ImportError as e:
                logger.warning(f"Failed to import Gemini service: {e}")
                self._gemini_service = None
        return self._gemini_service

    def analyze_emotion(self, text: str, method: str = None) -> EmotionResult:
        """
        Analyze emotion from text using specified method

        Args:
            text: Input text to analyze
            method: Detection method ('rule_based', 'ml', 'gemini', 'hybrid', 'auto')

        Returns:
            EmotionResult with detected emotions
        """
        if not text or not text.strip():
            return EmotionResult(
                primary_emotion="neutral",
                confidence=0.0,
                secondary_emotions=[],
                sentiment_score=0.0,
                intensity="low",
                keywords_matched=[],
                processing_time_ms=0.0,
                source="default",
            )

        # Determine detection method
        if method is None:
            method = self.settings.AI_MODEL_TYPE

        try:
            if method == "gemini" and self.settings.USE_GEMINI_FOR_EMOTIONS:
                return asyncio.run(self._analyze_with_gemini(text))
            elif method == "hybrid":
                return asyncio.run(self._analyze_hybrid(text))
            elif method == "ml" and self.ml_detector.is_available:
                return self.ml_detector.detect_emotion(text)
            else:
                return self.rule_detector.detect_emotion(text)

        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            # Fallback to rule-based detection
            if method != "rule_based":
                logger.info("Falling back to rule-based emotion detection")
                try:
                    return self.rule_detector.detect_emotion(text)
                except Exception as fallback_e:
                    logger.error(f"Fallback detection also failed: {fallback_e}")

            # Return neutral result as last resort
            return EmotionResult(
                primary_emotion="neutral",
                confidence=0.0,
                secondary_emotions=[],
                sentiment_score=0.0,
                intensity="low",
                keywords_matched=[],
                processing_time_ms=0.0,
                source="fallback",
            )

    async def _analyze_with_gemini(self, text: str) -> EmotionResult:
        """Analyze emotion using Gemini AI"""
        if not self.gemini_service or not self.gemini_service.is_available():
            logger.warning("Gemini service not available, falling back to rule-based")
            return self.rule_detector.detect_emotion(text)

        try:
            gemini_result = await self.gemini_service.analyze_emotion_with_gemini(text)

            # Convert Gemini result to EmotionResult format
            secondary_emotions = []
            if gemini_result.get("secondary_emotions"):
                secondary_emotions = [
                    (emotion, 0.5) for emotion in gemini_result["secondary_emotions"]
                ]

            # Check for crisis keywords using rule-based approach as backup
            crisis_detected, crisis_keywords = self.check_crisis_keywords(text)

            return EmotionResult(
                primary_emotion=gemini_result.get("primary_emotion", "neutral"),
                confidence=gemini_result.get("confidence", 0.5),
                secondary_emotions=secondary_emotions,
                sentiment_score=self._calculate_sentiment_score(text),
                intensity=self._map_intensity(gemini_result.get("intensity", 0.5)),
                keywords_matched=[],
                processing_time_ms=gemini_result.get("processing_time_ms", 0.0),
                source="gemini",
                crisis_indicators=gemini_result.get("crisis_indicators", False)
                or crisis_detected,
                safety_flags=crisis_keywords if crisis_detected else [],
            )

        except Exception as e:
            logger.error(f"Gemini emotion analysis failed: {e}")
            if self.settings.GEMINI_FALLBACK_ENABLED:
                logger.info("Falling back to rule-based detection")
                return self.rule_detector.detect_emotion(text)
            else:
                raise AIServiceError(f"Gemini emotion analysis failed: {str(e)}")

    async def _analyze_hybrid(self, text: str) -> EmotionResult:
        """Analyze emotion using hybrid approach (Gemini + rule-based)"""
        try:
            # Get both results
            rule_result = self.rule_detector.detect_emotion(text)

            if self.gemini_service and self.gemini_service.is_available():
                gemini_result = await self._analyze_with_gemini(text)

                # Combine results intelligently
                return self._combine_emotion_results(rule_result, gemini_result)
            else:
                # Fallback to rule-based only
                rule_result.source = "hybrid_fallback"
                return rule_result

        except Exception as e:
            logger.error(f"Hybrid emotion analysis failed: {e}")
            # Fallback to rule-based
            rule_result = self.rule_detector.detect_emotion(text)
            rule_result.source = "hybrid_fallback"
            return rule_result

    def _combine_emotion_results(
        self, rule_result: EmotionResult, gemini_result: EmotionResult
    ) -> EmotionResult:
        """Combine rule-based and Gemini results intelligently"""
        # Use higher confidence result as primary
        if gemini_result.confidence > rule_result.confidence:
            primary_emotion = gemini_result.primary_emotion
            confidence = gemini_result.confidence
            source_primary = "gemini"
        else:
            primary_emotion = rule_result.primary_emotion
            confidence = rule_result.confidence
            source_primary = "rule_based"

        # Combine secondary emotions
        combined_secondary = list(rule_result.secondary_emotions)
        for emotion, score in gemini_result.secondary_emotions:
            if not any(e[0] == emotion for e in combined_secondary):
                combined_secondary.append((emotion, score))

        # Use rule-based sentiment score (more reliable)
        sentiment_score = rule_result.sentiment_score

        # Combine crisis indicators (OR operation for safety)
        crisis_indicators = (
            rule_result.crisis_indicators or gemini_result.crisis_indicators
        )
        safety_flags = list(set(rule_result.safety_flags + gemini_result.safety_flags))

        return EmotionResult(
            primary_emotion=primary_emotion,
            confidence=confidence,
            secondary_emotions=combined_secondary[:3],  # Limit to top 3
            sentiment_score=sentiment_score,
            intensity=rule_result.intensity,  # Use rule-based intensity
            keywords_matched=rule_result.keywords_matched,
            processing_time_ms=rule_result.processing_time_ms
            + gemini_result.processing_time_ms,
            source=f"hybrid_{source_primary}",
            crisis_indicators=crisis_indicators,
            safety_flags=safety_flags,
        )

    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using VADER"""
        try:
            return self.rule_detector.vader_analyzer.polarity_scores(text)["compound"]
        except Exception:
            return 0.0

    def _map_intensity(self, intensity_value: float) -> str:
        """Map numeric intensity to string"""
        if intensity_value >= 0.8:
            return "high"
        elif intensity_value >= 0.6:
            return "medium"
        elif intensity_value >= 0.3:
            return "low"
        else:
            return "minimal"

    def check_crisis_keywords(self, text: str) -> Tuple[bool, List[str]]:
        """Check for crisis-related keywords in text"""
        return self.rule_detector.detect_crisis_keywords(text)

    def get_emotion_insights(self, emotion_result: EmotionResult) -> Dict[str, Any]:
        """
        Get additional insights about detected emotion

        Args:
            emotion_result: Result from emotion detection

        Returns:
            Dictionary with emotion insights
        """
        emotion = emotion_result.primary_emotion
        confidence = emotion_result.confidence
        intensity = emotion_result.intensity

        # Define emotion categories
        negative_emotions = {"stressed", "anxious", "sad", "overwhelmed", "angry"}
        positive_emotions = {"excited", "positive", "grateful"}
        neutral_emotions = {"neutral", "confused"}

        # Determine emotion category
        if emotion in negative_emotions:
            category = "negative"
            support_level = "high" if intensity in ["high", "extreme"] else "medium"
        elif emotion in positive_emotions:
            category = "positive"
            support_level = "low"
        else:
            category = "neutral"
            support_level = "low"

        # Generate insights
        insights = {
            "category": category,
            "support_level": support_level,
            "confidence_level": "high"
            if confidence > 0.7
            else "medium"
            if confidence > 0.4
            else "low",
            "intensity_level": intensity,
            "needs_intervention": category == "negative"
            and intensity in ["high", "extreme"],
            "suggested_coping_tools": self._get_suggested_tools(emotion),
            "followup_questions": self._get_followup_questions(emotion),
        }

        return insights

    def _get_suggested_tools(self, emotion: str) -> List[str]:
        """Get suggested coping tools for detected emotion"""
        tool_mapping = {
            "stressed": [
                "breathing_exercise",
                "grounding_technique",
                "progressive_relaxation",
            ],
            "anxious": ["breathing_exercise", "mindfulness", "grounding_technique"],
            "sad": ["journaling", "gratitude_practice", "gentle_movement"],
            "overwhelmed": [
                "priority_setting",
                "breathing_exercise",
                "break_down_tasks",
            ],
            "angry": ["cooling_down", "physical_exercise", "journaling"],
            "excited": ["goal_setting", "celebration_ritual", "energy_channeling"],
            "positive": ["gratitude_practice", "goal_setting", "sharing_joy"],
            "neutral": ["mood_check", "gentle_activity", "reflection"],
            "confused": ["journaling", "pros_cons_list", "talk_to_someone"],
            "grateful": ["gratitude_practice", "sharing_joy", "pay_it_forward"],
        }

        return tool_mapping.get(emotion, ["mindfulness", "self_care"])

    def _get_followup_questions(self, emotion: str) -> List[str]:
        """Get followup questions for detected emotion"""
        question_mapping = {
            "stressed": [
                "What's the main source of your stress right now?",
                "Have you been able to take any breaks today?",
                "What usually helps you feel less stressed?",
            ],
            "anxious": [
                "What thoughts are going through your mind?",
                "Is there something specific you're worried about?",
                "What has helped with your anxiety before?",
            ],
            "sad": [
                "What's been weighing on your heart?",
                "Is there someone you can talk to about this?",
                "What small thing might bring you a bit of comfort?",
            ],
            "overwhelmed": [
                "What's on your plate right now?",
                "What's the most urgent thing you need to handle?",
                "Can any of these tasks wait or be delegated?",
            ],
        }

        return question_mapping.get(
            emotion,
            [
                "How are you taking care of yourself today?",
                "What's one thing that might help you feel better?",
            ],
        )


# Global emotion detection service instance
emotion_service = EmotionDetectionService()
