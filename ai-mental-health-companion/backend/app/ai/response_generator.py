import asyncio
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.ai.emotion_detection import EmotionResult
from app.core.config import get_settings
from app.core.exceptions import AIServiceError

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ResponseResult:
    """Data class for response generation results"""

    message: str
    response_type: str
    coping_suggestions: List[str]
    resources: List[Dict[str, str]]
    follow_up_questions: List[str]
    safety_intervention: bool
    generation_time_ms: float
    source: str = "rule_based"  # 'rule_based', 'gemini', 'hybrid'
    safety_ratings: Optional[Dict[str, str]] = None


class ResponseTemplates:
    """Templates for generating supportive responses"""

    # Validation and acknowledgment phrases
    VALIDATION_PHRASES = {
        "stressed": [
            "It sounds like you're carrying a lot right now.",
            "Feeling stressed is completely understandable given what you're going through.",
            "I can hear that you're feeling overwhelmed, and that's valid.",
            "It's natural to feel stressed when you have so much on your mind.",
            "Your feelings of stress are completely legitimate.",
        ],
        "anxious": [
            "Anxiety can feel really overwhelming, and I want you to know that's okay.",
            "It's understandable that you're feeling anxious about this.",
            "Feeling anxious is your mind's way of trying to protect you.",
            "I hear that you're feeling worried, and those feelings are valid.",
            "Anxiety is difficult to deal with, and you're not alone in feeling this way.",
        ],
        "sad": [
            "I'm sorry you're feeling this way right now.",
            "It's okay to feel sad - these emotions are part of being human.",
            "Your sadness is valid, and it's important to acknowledge these feelings.",
            "I can hear the pain in what you're sharing, and that takes courage.",
            "Feeling sad is a natural response to difficult situations.",
        ],
        "overwhelmed": [
            "It sounds like you have a lot on your plate right now.",
            "Feeling overwhelmed is a sign that you're dealing with a lot.",
            "It's completely normal to feel this way when facing so much at once.",
            "I can understand why you'd feel overwhelmed - that's a lot to handle.",
            "When everything feels like too much, those feelings are completely valid.",
        ],
        "angry": [
            "It sounds like something has really upset you, and that's understandable.",
            "Your anger is telling you that something important to you has been affected.",
            "Feeling angry can be really intense, and it's okay to feel this way.",
            "It makes sense that you'd feel frustrated about this situation.",
            "Your feelings of anger are valid and deserve to be acknowledged.",
        ],
        "excited": [
            "I can feel your excitement, and that's wonderful!",
            "It's great to hear such positive energy in your message.",
            "Your excitement is contagious - thank you for sharing this joy!",
            "It sounds like something really good is happening for you.",
            "I love hearing when things are going well for you!",
        ],
        "positive": [
            "I'm so glad to hear you're feeling good.",
            "It's wonderful that you're in a positive headspace.",
            "Thank you for sharing these good feelings with me.",
            "It sounds like things are going well for you right now.",
            "Your positive energy is really uplifting.",
        ],
        "neutral": [
            "Thank you for sharing how you're feeling right now.",
            "I appreciate you taking the time to check in.",
            "It's perfectly okay to feel neutral sometimes.",
            "Thanks for letting me know where you're at today.",
            "I'm here to listen to whatever you're experiencing.",
        ],
        "confused": [
            "It's okay to feel uncertain - confusion is a natural part of processing things.",
            "Not knowing how to feel or what to think is completely normal.",
            "It sounds like you're working through some complex feelings.",
            "Confusion often means we're in a period of growth and change.",
            "It's alright to not have everything figured out right now.",
        ],
        "grateful": [
            "It's beautiful to hear you expressing gratitude.",
            "Gratitude is such a powerful and positive emotion.",
            "I'm glad you're able to recognize the good things in your life.",
            "Thank you for sharing your appreciation - it's inspiring.",
            "Your gratitude is a lovely reminder of life's positive moments.",
        ],
    }

    # Supportive continuation phrases
    SUPPORT_PHRASES = {
        "stressed": [
            "You're stronger than you know, even when stress feels overwhelming.",
            "Remember, it's okay to take things one step at a time.",
            "You don't have to handle everything perfectly - just doing your best is enough.",
            "Stress is temporary, even when it doesn't feel like it.",
            "You've handled difficult situations before, and you can get through this too.",
        ],
        "anxious": [
            "You're not alone in feeling this way - anxiety affects many people.",
            "Remember that anxious thoughts are just thoughts, not facts.",
            "You have the strength to get through this anxious moment.",
            "Anxiety is uncomfortable, but it won't last forever.",
            "Taking things moment by moment can help when anxiety feels overwhelming.",
        ],
        "sad": [
            "It's okay to sit with these feelings for a while - they're part of healing.",
            "Even in sadness, you're showing strength by reaching out.",
            "This difficult time will pass, even though it's hard to see right now.",
            "Your feelings matter, and so do you.",
            "Healing isn't linear - be patient and gentle with yourself.",
        ],
        "overwhelmed": [
            "Remember, you don't have to solve everything at once.",
            "Breaking things down into smaller steps can make them more manageable.",
            "It's okay to ask for help when you're feeling overwhelmed.",
            "You're doing the best you can with what you have right now.",
            "Taking a step back and breathing can help clear your perspective.",
        ],
        "angry": [
            "Your anger is valid, and it's important to process these feelings safely.",
            "Sometimes anger is trying to tell us something important about our boundaries.",
            "It's okay to feel angry - the key is finding healthy ways to express it.",
            "Your feelings are legitimate, even if the situation is complicated.",
            "Taking time to cool down can help you think more clearly.",
        ],
        "excited": [
            "Your excitement is wonderful to witness!",
            "It's great to see you feeling so positive about something.",
            "Enjoy this feeling - you deserve to feel excited and happy.",
            "Your enthusiasm is inspiring and contagious.",
            "These positive moments are so important to celebrate.",
        ],
        "positive": [
            "I'm so happy to hear you're feeling good.",
            "These positive feelings are worth celebrating and holding onto.",
            "It's wonderful when life feels good and balanced.",
            "You deserve to feel this way - soak it in!",
            "Positive moments like these can carry us through tougher times.",
        ],
        "neutral": [
            "Sometimes neutral is exactly where we need to be.",
            "There's peace in feeling balanced and steady.",
            "Neutral feelings can be a sign of stability and grounding.",
            "It's okay to just be where you are right now.",
            "Not every day needs to be intense - calm is valuable too.",
        ],
        "confused": [
            "Confusion often precedes clarity - you're in a process of figuring things out.",
            "It's okay to sit with uncertainty while you process your thoughts.",
            "Sometimes the best thing to do is give yourself time to think.",
            "Your confusion shows that you're thoughtfully considering your situation.",
            "Not having all the answers right now is perfectly human.",
        ],
        "grateful": [
            "Gratitude has such a positive impact on our overall wellbeing.",
            "It's wonderful that you can see the good even during challenging times.",
            "Your appreciation for life's moments is truly special.",
            "Gratitude can be a powerful tool for maintaining perspective.",
            "Thank you for sharing your positive outlook - it's uplifting.",
        ],
    }

    # Coping tool suggestions by emotion
    COPING_SUGGESTIONS = {
        "stressed": [
            "Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8.",
            "Take a 5-minute walk, even if it's just around your room or outside.",
            "Write down your top 3 priorities and focus on just one at a time.",
            "Practice progressive muscle relaxation starting from your toes up to your head.",
            "Listen to calming music or nature sounds for a few minutes.",
        ],
        "anxious": [
            "Use the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.",
            "Practice box breathing: breathe in for 4, hold for 4, out for 4, hold for 4.",
            "Try a brief mindfulness meditation focusing on your breath.",
            "Remind yourself: 'This feeling will pass, I am safe right now.'",
            "Engage in gentle movement like stretching or walking.",
        ],
        "sad": [
            "Write in a journal about what you're feeling - let it all out on paper.",
            "Reach out to a trusted friend or family member for connection.",
            "Do one small thing that usually brings you comfort, like making tea or listening to favorite music.",
            "Practice self-compassion - speak to yourself like you would a good friend.",
            "Consider watching something uplifting or looking at photos that make you smile.",
        ],
        "overwhelmed": [
            "Make a list of everything on your mind, then identify what's most urgent.",
            "Use the 'two-minute rule': if something takes less than two minutes, do it now.",
            "Break larger tasks into smaller, more manageable steps.",
            "Take 10 deep breaths and focus only on your breathing.",
            "Ask yourself: 'What's one thing I can let go of or delegate?'",
        ],
        "angry": [
            "Take 10 deep breaths before responding to whatever triggered your anger.",
            "Try physical exercise like jumping jacks or a quick walk to release tension.",
            "Write down your feelings without censoring yourself - then decide if you want to keep it.",
            "Count to 10 (or 100) before saying anything you might regret.",
            "Consider what boundary might need to be set or what you need to communicate.",
        ],
        "excited": [
            "Channel your excitement into planning your next steps toward your goal.",
            "Share your excitement with someone who will celebrate with you.",
            "Write down what's making you excited so you can remember this feeling later.",
            "Use this positive energy to tackle something you've been putting off.",
            "Take a moment to really savor and appreciate this wonderful feeling.",
        ],
        "positive": [
            "Take a moment to practice gratitude for what's going well.",
            "Consider how you can maintain this positive momentum.",
            "Share your good feelings with someone you care about.",
            "Use this positive energy to do something kind for yourself or others.",
            "Write down what's contributing to your positive mood.",
        ],
        "neutral": [
            "Check in with yourself: are there any needs that aren't being met?",
            "Consider doing a small activity that usually brings you joy.",
            "Practice mindfulness by noticing your surroundings without judgment.",
            "Take this calm moment to do some gentle self-reflection.",
            "Use this stable feeling to plan something you're looking forward to.",
        ],
        "confused": [
            "Write down your thoughts to help organize and clarify them.",
            "Talk through your confusion with someone you trust.",
            "Make a pros and cons list if you're trying to make a decision.",
            "Take some time away from the confusing situation to get perspective.",
            "Remember that it's okay not to have all the answers right now.",
        ],
        "grateful": [
            "Write down three specific things you're grateful for today.",
            "Consider expressing your gratitude to someone who has helped you.",
            "Use this grateful feeling to do something kind for someone else.",
            "Take a moment to really appreciate and savor what you're thankful for.",
            "Reflect on how gratitude affects your overall mood and perspective.",
        ],
    }

    # Crisis intervention messages
    CRISIS_RESPONSES = [
        "I'm really concerned about what you've shared. Your life has value, and there are people who want to help you through this difficult time.",
        "It sounds like you're going through something really difficult right now. Please know that you don't have to face this alone.",
        "I can hear that you're in a lot of pain. These feelings are temporary, even when they don't feel like it. Please reach out for support.",
        "What you're feeling right now is intense and overwhelming, but there are people trained to help you through this.",
        "I'm worried about you based on what you've shared. Your feelings are valid, and there are resources available to help you right now.",
    ]

    # Professional help encouragement
    PROFESSIONAL_HELP_ENCOURAGEMENT = {
        "high_distress": [
            "While I'm here to support you, it might be really helpful to talk to a counselor or therapist who can provide more personalized guidance.",
            "Consider reaching out to a mental health professional who can work with you on strategies tailored to your specific situation.",
            "A trained counselor might be able to offer additional tools and perspectives that could be really beneficial for you.",
            "You deserve professional support that can provide more comprehensive help than I can offer.",
        ],
        "persistent_issues": [
            "If you've been feeling this way for a while, talking to a professional could provide valuable insights and coping strategies.",
            "Sometimes it helps to have a neutral professional perspective when we're working through ongoing challenges.",
            "A therapist can offer personalized strategies and support that might be really helpful for your specific situation.",
        ],
        "general": [
            "Remember that seeking professional help is a sign of strength, not weakness.",
            "Mental health professionals are trained to help with exactly what you're experiencing.",
            "There's no shame in getting additional support from someone who specializes in mental health.",
        ],
    }

    # Resource suggestions
    RESOURCES = {
        "crisis": [
            {
                "name": "National Suicide Prevention Lifeline",
                "contact": "988",
                "description": "24/7 crisis support",
            },
            {
                "name": "Crisis Text Line",
                "contact": "Text HOME to 741741",
                "description": "24/7 crisis support via text",
            },
            {
                "name": "SAMHSA National Helpline",
                "contact": "1-800-662-4357",
                "description": "Treatment referral service",
            },
        ],
        "anxiety": [
            {
                "name": "Anxiety and Depression Association of America",
                "contact": "adaa.org",
                "description": "Resources and support for anxiety",
            },
            {
                "name": "Calm App",
                "contact": "calm.com",
                "description": "Meditation and relaxation exercises",
            },
            {
                "name": "Headspace",
                "contact": "headspace.com",
                "description": "Mindfulness and meditation",
            },
        ],
        "depression": [
            {
                "name": "National Alliance on Mental Illness",
                "contact": "nami.org",
                "description": "Mental health resources and support",
            },
            {
                "name": "Depression and Bipolar Support Alliance",
                "contact": "dbsalliance.org",
                "description": "Peer support and resources",
            },
            {
                "name": "Mental Health America",
                "contact": "mhanational.org",
                "description": "Mental health screening and resources",
            },
        ],
        "stress": [
            {
                "name": "American Psychological Association",
                "contact": "apa.org/topics/stress",
                "description": "Stress management resources",
            },
            {
                "name": "Mindfulness-Based Stress Reduction",
                "contact": "palousemindfulness.com",
                "description": "Free MBSR course",
            },
            {
                "name": "StressStop App",
                "contact": "stressstop.com",
                "description": "Quick stress relief techniques",
            },
        ],
        "general": [
            {
                "name": "Psychology Today",
                "contact": "psychologytoday.com",
                "description": "Find therapists and mental health professionals",
            },
            {
                "name": "BetterHelp",
                "contact": "betterhelp.com",
                "description": "Online counseling services",
            },
            {
                "name": "NAMI Support Groups",
                "contact": "nami.org/Support-Education",
                "description": "Local support groups",
            },
        ],
    }


class SafetyChecker:
    """Safety checking and crisis intervention"""

    def __init__(self):
        self.crisis_keywords = [
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

    def check_safety(self, text: str, emotion_result: EmotionResult) -> Dict[str, Any]:
        """
        Check for safety concerns in user input

        Args:
            text: User input text
            emotion_result: Detected emotion data

        Returns:
            Safety check results
        """
        text_lower = text.lower()

        # Check for crisis keywords
        crisis_keywords_found = []
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                crisis_keywords_found.append(keyword)

        # Determine safety level
        has_crisis_keywords = len(crisis_keywords_found) > 0
        high_distress = emotion_result.intensity in [
            "high",
            "extreme",
        ] and emotion_result.primary_emotion in ["sad", "overwhelmed", "hopeless"]
        very_negative_sentiment = emotion_result.sentiment_score < -0.8

        safety_level = (
            "crisis"
            if has_crisis_keywords
            else "high"
            if (high_distress or very_negative_sentiment)
            else "normal"
        )

        return {
            "safety_level": safety_level,
            "crisis_keywords_found": crisis_keywords_found,
            "needs_intervention": safety_level in ["crisis", "high"],
            "high_distress": high_distress,
            "very_negative_sentiment": very_negative_sentiment,
        }


class ResponseGenerator:
    """Main response generation service"""

    def __init__(self):
        self.templates = ResponseTemplates()
        self.safety_checker = SafetyChecker()
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

    def generate_response(
        self,
        user_input: str,
        emotion_result: EmotionResult,
        user_context: Dict[str, Any] = None,
    ) -> ResponseResult:
        """
        Generate supportive response based on detected emotion

        Args:
            user_input: User's input text
            emotion_result: Detected emotion and analysis
            user_context: Additional user context (optional)

        Returns:
            ResponseResult with generated response
        """
        # Determine response generation method
        if (
            settings.USE_GEMINI_FOR_RESPONSES
            and self.gemini_service
            and self.gemini_service.is_available()
        ):
            if settings.AI_MODEL_TYPE == "hybrid":
                return asyncio.run(
                    self._generate_hybrid_response(
                        user_input, emotion_result, user_context
                    )
                )
            else:
                return asyncio.run(
                    self._generate_gemini_response(
                        user_input, emotion_result, user_context
                    )
                )
        else:
            return self._generate_rule_based_response(
                user_input, emotion_result, user_context
            )

    def _generate_rule_based_response(
        self,
        user_input: str,
        emotion_result: EmotionResult,
        user_context: Dict[str, Any] = None,
    ) -> ResponseResult:
        """Generate response using rule-based approach"""
        start_time = datetime.now()

        try:
            # Safety check
            safety_check = self.safety_checker.check_safety(user_input, emotion_result)

            # Handle crisis situations
            if safety_check["safety_level"] == "crisis":
                return self._generate_crisis_response(
                    emotion_result, safety_check, start_time
                )

            # Generate normal supportive response
            emotion = emotion_result.primary_emotion
            intensity = emotion_result.intensity

            # Build response components
            validation = self._get_validation_phrase(emotion)
            support = self._get_support_phrase(emotion)
            coping_suggestions = self._get_coping_suggestions(emotion, intensity)
            resources = self._get_resources(emotion, safety_check)
            follow_up_questions = self._get_follow_up_questions(emotion)

            # Combine into full response
            response_parts = [validation, support]

            # Add professional help suggestion for high distress
            if safety_check["high_distress"]:
                response_parts.append(
                    random.choice(
                        self.templates.PROFESSIONAL_HELP_ENCOURAGEMENT["high_distress"]
                    )
                )

            # Add coping suggestion
            if coping_suggestions:
                response_parts.append(
                    f"Here's something that might help: {coping_suggestions[0]}"
                )

            full_response = " ".join(response_parts)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return ResponseResult(
                message=full_response,
                response_type="supportive",
                coping_suggestions=coping_suggestions,
                resources=resources,
                follow_up_questions=follow_up_questions,
                safety_intervention=safety_check["needs_intervention"],
                generation_time_ms=processing_time,
                source="rule_based",
            )

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise AIServiceError(f"Failed to generate response: {str(e)}")

    async def _generate_gemini_response(
        self,
        user_input: str,
        emotion_result: EmotionResult,
        user_context: Dict[str, Any] = None,
    ) -> ResponseResult:
        """Generate response using Gemini AI"""
        start_time = datetime.now()

        try:
            # Safety check first
            safety_check = self.safety_checker.check_safety(user_input, emotion_result)

            # Handle crisis situations with rule-based approach
            if safety_check["safety_level"] == "crisis":
                return self._generate_crisis_response(
                    emotion_result, safety_check, start_time, source="gemini_crisis"
                )

            # Generate empathetic response with Gemini
            gemini_result = await self.gemini_service.generate_empathetic_response(
                user_message=user_input,
                detected_emotion=emotion_result.primary_emotion,
                emotion_intensity=emotion_result.confidence,
                context=user_context,
            )

            # Get additional components using rule-based approach
            coping_suggestions = self._get_coping_suggestions(
                emotion_result.primary_emotion, emotion_result.intensity
            )
            resources = self._get_resources(
                emotion_result.primary_emotion, safety_check
            )
            follow_up_questions = self._get_follow_up_questions(
                emotion_result.primary_emotion
            )

            # Try to get Gemini coping suggestions as well
            try:
                gemini_coping = await self.gemini_service.get_coping_suggestions(
                    emotion_result.primary_emotion,
                    emotion_result.confidence,
                    user_context,
                )
                if gemini_coping:
                    coping_suggestions = (
                        gemini_coping + coping_suggestions[:1]
                    )  # Combine with one rule-based
            except Exception as e:
                logger.warning(f"Failed to get Gemini coping suggestions: {e}")

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return ResponseResult(
                message=gemini_result["message"],
                response_type="empathetic_ai",
                coping_suggestions=coping_suggestions,
                resources=resources,
                follow_up_questions=follow_up_questions,
                safety_intervention=safety_check["needs_intervention"],
                generation_time_ms=processing_time,
                source="gemini",
                safety_ratings=gemini_result.get("safety_ratings"),
            )

        except Exception as e:
            logger.error(f"Gemini response generation failed: {e}")

            # Fallback to rule-based if enabled
            if settings.GEMINI_FALLBACK_ENABLED:
                logger.info("Falling back to rule-based response generation")
                return self._generate_rule_based_response(
                    user_input, emotion_result, user_context
                )
            else:
                raise AIServiceError(f"Failed to generate Gemini response: {str(e)}")

    async def _generate_hybrid_response(
        self,
        user_input: str,
        emotion_result: EmotionResult,
        user_context: Dict[str, Any] = None,
    ) -> ResponseResult:
        """Generate response using hybrid approach (Gemini + rule-based)"""
        start_time = datetime.now()

        try:
            # Safety check
            safety_check = self.safety_checker.check_safety(user_input, emotion_result)

            # Handle crisis situations
            if safety_check["safety_level"] == "crisis":
                return self._generate_crisis_response(
                    emotion_result, safety_check, start_time, source="hybrid_crisis"
                )

            # Get rule-based response as baseline
            rule_response = self._generate_rule_based_response(
                user_input, emotion_result, user_context
            )

            # Try to enhance with Gemini
            try:
                gemini_result = await self.gemini_service.generate_empathetic_response(
                    user_message=user_input,
                    detected_emotion=emotion_result.primary_emotion,
                    emotion_intensity=emotion_result.confidence,
                    context=user_context,
                )

                # Use Gemini message if it passes validation, otherwise use rule-based
                final_message = self._validate_and_choose_response(
                    gemini_result["message"], rule_response.message, user_input
                )

                # Get enhanced coping suggestions
                gemini_coping = await self.gemini_service.get_coping_suggestions(
                    emotion_result.primary_emotion,
                    emotion_result.confidence,
                    user_context,
                )

                combined_coping = (
                    gemini_coping[:2] + rule_response.coping_suggestions[:2]
                    if gemini_coping
                    else rule_response.coping_suggestions
                )

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                return ResponseResult(
                    message=final_message,
                    response_type="hybrid_empathetic",
                    coping_suggestions=combined_coping[:3],  # Limit to 3
                    resources=rule_response.resources,
                    follow_up_questions=rule_response.follow_up_questions,
                    safety_intervention=safety_check["needs_intervention"],
                    generation_time_ms=processing_time,
                    source="hybrid",
                    safety_ratings=gemini_result.get("safety_ratings"),
                )

            except Exception as e:
                logger.warning(f"Gemini enhancement failed in hybrid mode: {e}")
                # Return rule-based response with hybrid source
                rule_response.source = "hybrid_fallback"
                return rule_response

        except Exception as e:
            logger.error(f"Hybrid response generation failed: {e}")
            raise AIServiceError(f"Failed to generate hybrid response: {str(e)}")

    def _validate_and_choose_response(
        self, gemini_message: str, rule_message: str, user_input: str
    ) -> str:
        """Validate and choose between Gemini and rule-based response"""

        # Basic validation checks for Gemini response
        if not gemini_message or len(gemini_message.strip()) < 20:
            return rule_message

        # Check for inappropriate content
        inappropriate_phrases = [
            "just think positive",
            "get over it",
            "it could be worse",
            "just relax",
            "stop being dramatic",
            "snap out of it",
        ]

        gemini_lower = gemini_message.lower()
        for phrase in inappropriate_phrases:
            if phrase in gemini_lower:
                logger.warning(
                    f"Gemini response contains inappropriate phrase: {phrase}"
                )
                return rule_message

        # If Gemini response passes validation, use it
        return gemini_message

    def _generate_crisis_response(
        self,
        emotion_result: EmotionResult,
        safety_check: Dict[str, Any],
        start_time: datetime,
        source: str = "rule_based",
    ) -> ResponseResult:
        """Generate crisis intervention response"""

        crisis_response = random.choice(self.templates.CRISIS_RESPONSES)

        # Add professional help resources
        crisis_response += " " + random.choice(
            self.templates.PROFESSIONAL_HELP_ENCOURAGEMENT["general"]
        )

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return ResponseResult(
            message=crisis_response,
            response_type="crisis_intervention",
            coping_suggestions=[
                "reach_out_immediately",
                "call_crisis_line",
                "go_to_emergency_room",
            ],
            resources=self.templates.RESOURCES["crisis"],
            follow_up_questions=[
                "Is there someone you can call right now?",
                "Are you in a safe place?",
                "Would you like me to help you find local crisis resources?",
            ],
            safety_intervention=True,
            generation_time_ms=processing_time,
        )

    def _get_validation_phrase(self, emotion: str) -> str:
        """Get validation phrase for emotion"""
        phrases = self.templates.VALIDATION_PHRASES.get(
            emotion, self.templates.VALIDATION_PHRASES["neutral"]
        )
        return random.choice(phrases)

    def _get_support_phrase(self, emotion: str) -> str:
        """Get support phrase for emotion"""
        phrases = self.templates.SUPPORT_PHRASES.get(
            emotion, self.templates.SUPPORT_PHRASES["neutral"]
        )
        return random.choice(phrases)

    def _get_coping_suggestions(self, emotion: str, intensity: str) -> List[str]:
        """Get coping suggestions for emotion"""
        suggestions = self.templates.COPING_SUGGESTIONS.get(
            emotion, self.templates.COPING_SUGGESTIONS["neutral"]
        )

        # For high intensity emotions, provide more suggestions
        num_suggestions = 3 if intensity in ["high", "extreme"] else 2
        return random.sample(suggestions, min(num_suggestions, len(suggestions)))

    def _get_resources(
        self, emotion: str, safety_check: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Get appropriate resources based on emotion and safety level"""
        if safety_check["safety_level"] == "crisis":
            return self.templates.RESOURCES["crisis"]

        # Map emotions to resource categories
        resource_mapping = {
            "anxious": "anxiety",
            "stressed": "stress",
            "sad": "depression",
            "overwhelmed": "stress",
        }

        resource_key = resource_mapping.get(emotion, "general")
        return self.templates.RESOURCES.get(
            resource_key, self.templates.RESOURCES["general"]
        )

    def _get_follow_up_questions(self, emotion: str) -> List[str]:
        """Get follow-up questions for emotion"""
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
                "What feels like the most urgent thing on your plate?",
                "What's one task you could potentially let go of or ask for help with?",
                "How have you been taking care of yourself lately?",
            ],
            "angry": [
                "What triggered these feelings for you?",
                "How do you usually handle anger in healthy ways?",
                "What boundary might need to be set here?",
            ],
            "excited": [
                "What's got you feeling so excited?",
                "How do you want to celebrate or channel this energy?",
                "What are you looking forward to most?",
            ],
            "positive": [
                "What's contributing to your positive mood today?",
                "How can you maintain this good feeling?",
                "What are you most grateful for right now?",
            ],
        }

        return question_mapping.get(
            emotion,
            [
                "How are you taking care of yourself today?",
                "What's one thing that might help you feel better?",
                "Is there anything specific you'd like to talk about?",
            ],
        )

    def personalize_response(
        self, base_response: ResponseResult, user_context: Dict[str, Any]
    ) -> ResponseResult:
        """
        Personalize response based on user context like history, preferences, etc.

        Args:
            base_response: Base generated response
            user_context: User history and preferences

        Returns:
            Personalized ResponseResult
        """
        # For now, return the base response
        # In the future, this could incorporate:
        # - User's preferred coping tools
        # - Previous successful interventions
        # - Time of day preferences
        # - Personal triggers and patterns

        return base_response


# Global response generator instance
response_generator = ResponseGenerator()
