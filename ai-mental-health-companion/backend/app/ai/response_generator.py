import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import asyncio
import os

from app.ai.emotion_detection import EmotionResult
from app.core.config import get_settings
from app.core.exceptions import AIServiceError

# OpenAI integration
import openai
from openai import AsyncOpenAI

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


class ResponseTemplates:
    """Templates for generating supportive responses"""

    # Validation and acknowledgment phrases
    VALIDATION_PHRASES = {
        "stressed": [
            "It sounds like you're carrying a lot right now.",
            "Feeling stressed is completely understandable given what you're going through.",
            "I can hear that you're feeling overwhelmed, and that's valid.",
            "It's natural to feel stressed when you have so much on your mind.",
            "Your feelings of stress are completely legitimate."
        ],
        "anxious": [
            "Anxiety can feel really overwhelming, and I want you to know that's okay.",
            "It's understandable that you're feeling anxious about this.",
            "Feeling anxious is your mind's way of trying to protect you.",
            "I hear that you're feeling worried, and those feelings are valid.",
            "Anxiety is difficult to deal with, and you're not alone in feeling this way."
        ],
        "sad": [
            "I'm sorry you're feeling this way right now.",
            "It's okay to feel sad - these emotions are part of being human.",
            "Your sadness is valid, and it's important to acknowledge these feelings.",
            "I can hear the pain in what you're sharing, and that takes courage.",
            "Feeling sad is a natural response to difficult situations."
        ],
        "overwhelmed": [
            "It sounds like you have a lot on your plate right now.",
            "Feeling overwhelmed is a sign that you're dealing with a lot.",
            "It's completely normal to feel this way when facing so much at once.",
            "I can understand why you'd feel overwhelmed - that's a lot to handle.",
            "When everything feels like too much, those feelings are completely valid."
        ],
        "angry": [
            "It sounds like something has really upset you, and that's understandable.",
            "Your anger is telling you that something important to you has been affected.",
            "Feeling angry can be really intense, and it's okay to feel this way.",
            "It makes sense that you'd feel frustrated about this situation.",
            "Your feelings of anger are valid and deserve to be acknowledged."
        ],
        "excited": [
            "I can feel your excitement, and that's wonderful!",
            "It's great to hear such positive energy in your message.",
            "Your excitement is contagious - thank you for sharing this joy!",
            "It sounds like something really good is happening for you.",
            "I love hearing when things are going well for you!"
        ],
        "positive": [
            "I'm so glad to hear you're feeling good.",
            "It's wonderful that you're in a positive headspace.",
            "Thank you for sharing these good feelings with me.",
            "It sounds like things are going well for you right now.",
            "Your positive energy is really uplifting."
        ],
        "neutral": [
            "Thank you for sharing how you're feeling right now.",
            "I appreciate you taking the time to check in.",
            "It's perfectly okay to feel neutral sometimes.",
            "Thanks for letting me know where you're at today.",
            "I'm here to listen to whatever you're experiencing."
        ],
        "confused": [
            "It's okay to feel uncertain - confusion is a natural part of processing things.",
            "Not knowing how to feel or what to think is completely normal.",
            "It sounds like you're working through some complex feelings.",
            "Confusion often means we're in a period of growth and change.",
            "It's alright to not have everything figured out right now."
        ],
        "grateful": [
            "It's beautiful to hear you expressing gratitude.",
            "Gratitude is such a powerful and positive emotion.",
            "I'm glad you're able to recognize the good things in your life.",
            "Thank you for sharing your appreciation - it's inspiring.",
            "Your gratitude is a lovely reminder of life's positive moments."
        ]
    }

    # Support phrases
    SUPPORT_PHRASES = {
        "stressed": [
            "Remember that it's okay to take things one step at a time.",
            "You don't have to handle everything at once.",
            "Taking breaks isn't giving up - it's taking care of yourself.",
            "You're stronger than you know, even when it doesn't feel like it.",
            "It's important to be gentle with yourself during stressful times."
        ],
        "anxious": [
            "Try to focus on what you can control right now.",
            "Remember that most of our worries never actually happen.",
            "You've gotten through difficult times before, and you can do it again.",
            "Breathing deeply can help calm your nervous system.",
            "It's okay to take things slowly when you're feeling anxious."
        ],
        "sad": [
            "Your feelings are temporary, even though they feel overwhelming right now.",
            "It's okay to sit with these feelings for a while.",
            "Healing isn't linear, and that's perfectly normal.",
            "You're not alone in feeling this way.",
            "Be patient with yourself as you work through this."
        ],
        "overwhelmed": [
            "Try breaking things down into smaller, manageable pieces.",
            "You don't have to figure everything out right now.",
            "It's okay to ask for help when you need it.",
            "Focus on what's most important and let the rest go for now.",
            "Taking care of yourself isn't selfish - it's necessary."
        ],
        "angry": [
            "Your anger is information about what matters to you.",
            "It's okay to feel angry, but try to express it in healthy ways.",
            "Take some time to cool down before making any big decisions.",
            "Consider what boundaries might need to be set.",
            "Channel this energy into positive action when you're ready."
        ],
        "excited": [
            "It's wonderful to see you feeling so positive!",
            "Enjoy this moment of joy and celebration.",
            "Your enthusiasm is inspiring and uplifting.",
            "Make sure to savor these good feelings.",
            "Share your excitement with people who care about you."
        ],
        "positive": [
            "It's great that you're in such a good headspace.",
            "Keep doing whatever is working for you right now.",
            "Your positive outlook can be a source of strength.",
            "Enjoy this peaceful moment in your life.",
            "You deserve to feel happy and content."
        ],
        "neutral": [
            "It's perfectly fine to feel steady and calm.",
            "Sometimes neutral is exactly where we need to be.",
            "Take this time to check in with yourself.",
            "Stability can be its own form of wellness.",
            "Use this balanced time to practice self-care."
        ]
    }

    # Coping suggestions
    COPING_SUGGESTIONS = {
        "stressed": [
            "Take 5 deep breaths, focusing on making your exhale longer than your inhale",
            "Try a 10-minute walk outside to clear your head",
            "Write down your top 3 priorities for today and focus only on those",
            "Practice progressive muscle relaxation starting from your toes",
            "Listen to calming music or nature sounds for a few minutes"
        ],
        "anxious": [
            "Try the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you hear, 3 you feel, 2 you smell, 1 you taste",
            "Practice box breathing: inhale for 4, hold for 4, exhale for 4, hold for 4",
            "Challenge anxious thoughts by asking 'Is this thought helpful? Is it realistic?'",
            "Use a worry journal to write down your concerns and potential solutions",
            "Try gentle stretching or yoga to release physical tension"
        ],
        "sad": [
            "Allow yourself to feel the sadness without judgment",
            "Reach out to a trusted friend or family member",
            "Do one small thing that usually brings you comfort",
            "Spend time in nature, even if it's just looking out a window",
            "Practice self-compassion - treat yourself like you would a good friend"
        ],
        "overwhelmed": [
            "Make a list and prioritize just the top 3 most important tasks",
            "Break large tasks into smaller, more manageable steps",
            "Take a 15-minute break to do something you enjoy",
            "Delegate or ask for help with one thing on your list",
            "Focus on completing just one thing at a time"
        ],
        "angry": [
            "Take a timeout and count to 10 (or 100) before responding",
            "Try physical exercise to release the energy constructively",
            "Write about your feelings without censoring yourself",
            "Practice deep breathing to calm your nervous system",
            "Consider the situation from different perspectives"
        ],
        "neutral": [
            "Use this stable time to practice mindfulness or meditation",
            "Reflect on what you're grateful for today",
            "Set intentions for how you want to spend your energy",
            "Check in with your physical needs - rest, nutrition, movement",
            "Connect with someone you care about"
        ]
    }

    # Crisis intervention responses
    CRISIS_RESPONSES = [
        "I'm really concerned about you right now. Your life has value and meaning, and I want to help you get through this difficult time.",
        "I can hear that you're in tremendous pain right now. Please know that you don't have to face this alone - there are people who want to help.",
        "Thank you for sharing something so difficult with me. Right now, the most important thing is getting you connected with someone who can provide immediate support.",
        "I'm worried about your safety right now. These feelings can be overwhelming, but they are temporary. Please reach out for help immediately."
    ]

    # Professional help encouragement
    PROFESSIONAL_HELP_ENCOURAGEMENT = {
        "general": [
            "Consider reaching out to a mental health professional who can provide personalized support.",
            "A therapist or counselor can offer strategies specifically tailored to your situation.",
            "Professional help can make a real difference in how you're feeling.",
            "There's no shame in seeking professional support - it's a sign of strength and self-care."
        ],
        "high_distress": [
            "Given how much distress you're experiencing, I'd strongly encourage you to speak with a mental health professional.",
            "When feelings are this intense, professional support can be incredibly helpful.",
            "A therapist can provide you with additional tools and strategies to manage these difficult emotions.",
            "You deserve professional support to help you work through this challenging time."
        ]
    }

    # Resources
    RESOURCES = {
        "crisis": [
            {"name": "National Suicide Prevention Lifeline", "contact": "988", "type": "phone"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "type": "text"},
            {"name": "Emergency Services", "contact": "911", "type": "phone"},
            {"name": "International Association for Suicide Prevention", "contact": "https://www.iasp.info/resources/Crisis_Centres/", "type": "website"}
        ],
        "anxiety": [
            {"name": "Anxiety and Depression Association of America", "contact": "https://adaa.org", "type": "website"},
            {"name": "Psychology Today Therapist Finder", "contact": "https://www.psychologytoday.com", "type": "website"},
            {"name": "Calm App", "contact": "Meditation and mindfulness app", "type": "app"},
            {"name": "Headspace", "contact": "Guided meditation app", "type": "app"}
        ],
        "depression": [
            {"name": "National Institute of Mental Health", "contact": "https://www.nimh.nih.gov", "type": "website"},
            {"name": "Depression and Bipolar Support Alliance", "contact": "https://www.dbsalliance.org", "type": "website"},
            {"name": "Psychology Today Therapist Finder", "contact": "https://www.psychologytoday.com", "type": "website"}
        ],
        "stress": [
            {"name": "American Psychological Association Stress Resources", "contact": "https://www.apa.org/topics/stress", "type": "website"},
            {"name": "Mindfulness-Based Stress Reduction", "contact": "Local MBSR programs", "type": "program"},
            {"name": "Employee Assistance Program", "contact": "Check with your employer", "type": "program"}
        ],
        "general": [
            {"name": "Mental Health America", "contact": "https://www.mhanational.org", "type": "website"},
            {"name": "SAMHSA National Helpline", "contact": "1-800-662-HELP", "type": "phone"},
            {"name": "Psychology Today Therapist Finder", "contact": "https://www.psychologytoday.com", "type": "website"}
        ]
    }


class SafetyChecker:
    """Safety checking and crisis intervention"""

    def __init__(self):
        self.crisis_keywords = [
            "suicide", "kill myself", "end my life", "hurt myself", "self harm",
            "cutting", "overdose", "die", "death wish", "worthless", "hopeless",
            "can't go on", "no point in living", "want to disappear",
            "better off dead", "end it all", "can't take it anymore"
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
        high_distress = emotion_result.intensity in ["high", "extreme"] and emotion_result.primary_emotion in ["sad", "overwhelmed", "hopeless"]
        very_negative_sentiment = emotion_result.sentiment_score < -0.8

        safety_level = "crisis" if has_crisis_keywords else "high" if (high_distress or very_negative_sentiment) else "normal"

        return {
            "safety_level": safety_level,
            "crisis_keywords_found": crisis_keywords_found,
            "needs_intervention": safety_level in ["crisis", "high"],
            "high_distress": high_distress,
            "very_negative_sentiment": very_negative_sentiment
        }


class ResponseGenerator:
    """Main response generation service with OpenAI integration"""

    def __init__(self):
        self.templates = ResponseTemplates()
        self.safety_checker = SafetyChecker()

        # Initialize OpenAI client if API key is available
        self.openai_client = None
        self.use_openai = False

        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.use_openai = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Falling back to template-based responses.")
                self.use_openai = False
        else:
            logger.info("No OpenAI API key found. Using template-based responses.")

    async def generate_response(self, user_input: str, emotion_result: EmotionResult, user_context: Dict[str, Any] = None) -> ResponseResult:
        """
        Generate supportive response based on detected emotion

        Args:
            user_input: User's input text
            emotion_result: Detected emotion and analysis
            user_context: Additional user context (optional)

        Returns:
            ResponseResult with generated response
        """
        start_time = datetime.now()

        try:
            # Safety check - this always takes precedence
            safety_check = self.safety_checker.check_safety(user_input, emotion_result)

            # Handle crisis situations with immediate intervention
            if safety_check["safety_level"] == "crisis":
                return self._generate_crisis_response(emotion_result, safety_check, start_time)

            # Generate response using OpenAI or fallback to templates
            if self.use_openai and self.openai_client:
                try:
                    response_result = await self._generate_openai_response(
                        user_input, emotion_result, safety_check, user_context, start_time
                    )
                    return response_result
                except Exception as e:
                    logger.error(f"OpenAI response generation failed: {e}. Falling back to template response.")
                    # Fall through to template-based response

            # Template-based response generation (fallback)
            return self._generate_template_response(user_input, emotion_result, safety_check, start_time)

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise AIServiceError(f"Failed to generate response: {str(e)}")

    async def _generate_openai_response(self, user_input: str, emotion_result: EmotionResult,
                                      safety_check: Dict[str, Any], user_context: Dict[str, Any],
                                      start_time: datetime) -> ResponseResult:
        """
        Generate response using OpenAI's chat completion API

        Args:
            user_input: User's input text
            emotion_result: Detected emotion and analysis
            safety_check: Safety assessment results
            user_context: Additional user context
            start_time: Generation start time

        Returns:
            ResponseResult with OpenAI-generated response
        """
        try:
            # Construct system prompt for mental health companion
            system_prompt = self._build_system_prompt(emotion_result, safety_check)

            # Construct user prompt with context
            user_prompt = self._build_user_prompt(user_input, emotion_result, user_context)

            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,  # Keep under 200 words typically
                temperature=0.7,
                timeout=10.0  # 10 second timeout
            )

            # Extract the response content
            ai_message = response.choices[0].message.content.strip()

            # Ensure response stays under 200 words
            words = ai_message.split()
            if len(words) > 200:
                ai_message = ' '.join(words[:200]) + "..."

            # Generate complementary components using templates
            coping_suggestions = self._get_coping_suggestions(emotion_result.primary_emotion, emotion_result.intensity)
            resources = self._get_resources(emotion_result.primary_emotion, safety_check)
            follow_up_questions = self._get_follow_up_questions(emotion_result.primary_emotion)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return ResponseResult(
                message=ai_message,
                response_type="ai_supportive",
                coping_suggestions=coping_suggestions,
                resources=resources,
                follow_up_questions=follow_up_questions,
                safety_intervention=safety_check["needs_intervention"],
                generation_time_ms=processing_time
            )

        except asyncio.TimeoutError:
            logger.error("OpenAI API request timed out")
            raise AIServiceError("AI service timeout - please try again")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"AI service error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI response generation: {e}")
            raise AIServiceError(f"AI service error: {str(e)}")

    def _build_system_prompt(self, emotion_result: EmotionResult, safety_check: Dict[str, Any]) -> str:
        """Build system prompt for OpenAI based on emotion and safety context"""
        base_prompt = """You are a compassionate AI mental health companion. Your role is to provide empathetic, supportive responses that validate emotions and offer gentle guidance.

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
        }

        if emotion_result.primary_emotion in emotion_guidance:
            base_prompt += f"\n\nSPECIFIC GUIDANCE: The user is feeling {emotion_result.primary_emotion}. {emotion_guidance[emotion_result.primary_emotion]}"

        # Add safety context
        if safety_check["needs_intervention"]:
            base_prompt += "\n\nIMPORTANT: The user may be experiencing high distress. Be extra gentle and consider mentioning professional support resources."

        return base_prompt

    def _build_user_prompt(self, user_input: str, emotion_result: EmotionResult, user_context: Dict[str, Any]) -> str:
        """Build user prompt with context for OpenAI"""
        prompt = f"User's message: \"{user_input}\"\n\n"
        prompt += f"Detected emotion: {emotion_result.primary_emotion} (intensity: {emotion_result.intensity})\n"
        prompt += f"Sentiment score: {emotion_result.sentiment_score:.2f}\n"

        if user_context:
            prompt += f"Additional context: {user_context}\n"

        prompt += "\nPlease provide a supportive, empathetic response that validates their feelings and offers gentle guidance."

        return prompt

    def _generate_template_response(self, user_input: str, emotion_result: EmotionResult,
                                  safety_check: Dict[str, Any], start_time: datetime) -> ResponseResult:
        """
        Generate response using template-based system (fallback method)

        Args:
            user_input: User's input text
            emotion_result: Detected emotion and analysis
            safety_check: Safety assessment results
            start_time: Generation start time

        Returns:
            ResponseResult with template-generated response
        """
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
            response_parts.append(random.choice(self.templates.PROFESSIONAL_HELP_ENCOURAGEMENT["high_distress"]))

        # Add coping suggestion
        if coping_suggestions:
            response_parts.append(f"Here's something that might help: {coping_suggestions[0]}")

        full_response = " ".join(response_parts)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return ResponseResult(
            message=full_response,
            response_type="template_supportive",
            coping_suggestions=coping_suggestions,
            resources=resources,
            follow_up_questions=follow_up_questions,
            safety_intervention=safety_check["needs_intervention"],
            generation_time_ms=processing_time
        )

    def _generate_crisis_response(self, emotion_result: EmotionResult, safety_check: Dict[str, Any], start_time: datetime) -> ResponseResult:
        """Generate crisis intervention response"""

        crisis_response = random.choice(self.templates.CRISIS_RESPONSES)

        # Add professional help resources
        crisis_response += " " + random.choice(self.templates.PROFESSIONAL_HELP_ENCOURAGEMENT["general"])

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return ResponseResult(
            message=crisis_response,
            response_type="crisis_intervention",
            coping_suggestions=["reach_out_immediately", "call_crisis_line", "go_to_emergency_room"],
            resources=self.templates.RESOURCES["crisis"],
            follow_up_questions=[
                "Is there someone you can call right now?",
                "Are you in a safe place?",
                "Would you like me to help you find local crisis resources?"
            ],
            safety_intervention=True,
            generation_time_ms=processing_time
        )

    def _get_validation_phrase(self, emotion: str) -> str:
        """Get validation phrase for emotion"""
        phrases = self.templates.VALIDATION_PHRASES.get(emotion, self.templates.VALIDATION_PHRASES["neutral"])
        return random.choice(phrases)

    def _get_support_phrase(self, emotion: str) -> str:
        """Get support phrase for emotion"""
        phrases = self.templates.SUPPORT_PHRASES.get(emotion, self.templates.SUPPORT_PHRASES["neutral"])
        return random.choice(phrases)

    def _get_coping_suggestions(self, emotion: str, intensity: str) -> List[str]:
        """Get coping suggestions for emotion"""
        suggestions = self.templates.COPING_SUGGESTIONS.get(emotion, self.templates.COPING_SUGGESTIONS["neutral"])

        # For high intensity emotions, provide more suggestions
        num_suggestions = 3 if intensity in ["high", "extreme"] else 2
        return random.sample(suggestions, min(num_suggestions, len(suggestions)))

    def _get_resources(self, emotion: str, safety_check: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get appropriate resources based on emotion and safety level"""
        if safety_check["safety_level"] == "crisis":
            return self.templates.RESOURCES["crisis"]

        # Map emotions to resource categories
        resource_mapping = {
            "anxious": "anxiety",
            "stressed": "stress",
            "sad": "depression",
            "overwhelmed": "stress"
        }

        resource_key = resource_mapping.get(emotion, "general")
        return self.templates.RESOURCES.get(resource_key, self.templates.RESOURCES["general"])

    def _get_follow_up_questions(self, emotion: str) -> List[str]:
        """Get follow-up questions for emotion"""
        question_mapping = {
            "stressed": [
                "What's the main source of your stress right now?",
                "Have you been able to take any breaks today?",
                "What usually helps you feel less stressed?"
            ],
            "anxious": [
                "What thoughts are going through your mind?",
                "Is there something specific you're worried about?",
                "What has helped with your anxiety before?"
            ],
            "sad": [
                "What's been weighing on your heart?",
                "Is there someone you can talk to about this?",
                "What small thing might bring you a bit of comfort?"
            ],
            "overwhelmed": [
                "What feels like the most urgent thing on your plate?",
                "What's one task you could potentially let go of or ask for help with?",
                "How have you been taking care of yourself lately?"
            ],
            "angry": [
                "What triggered these feelings for you?",
                "How do you usually handle anger in healthy ways?",
                "What boundary might need to be set here?"
            ],
            "excited": [
                "What's got you feeling so excited?",
                "How do you want to celebrate or channel this energy?",
                "What are you looking forward to most?"
            ],
            "positive": [
                "What's contributing to your positive mood today?",
                "How can you maintain this good feeling?",
                "What are you most grateful for right now?"
            ]
        }

        return question_mapping.get(emotion, [
            "How are you taking care of yourself today?",
            "What's one thing that might help you feel better?",
            "Is there anything specific you'd like to talk about?"
        ])

    def personalize_response(self, base_response: ResponseResult, user_context: Dict[str, Any]) -> ResponseResult:
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
