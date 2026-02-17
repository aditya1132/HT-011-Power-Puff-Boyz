import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CopingToolType(str, Enum):
    """Types of coping tools available"""
    BREATHING = "breathing"
    GROUNDING = "grounding"
    MINDFULNESS = "mindfulness"
    JOURNALING = "journaling"
    PHYSICAL = "physical"
    COGNITIVE = "cognitive"
    RELAXATION = "relaxation"
    CREATIVITY = "creativity"
    SOCIAL = "social"


class EmotionTarget(str, Enum):
    """Target emotions for coping tools"""
    STRESS = "stressed"
    ANXIETY = "anxious"
    SADNESS = "sad"
    OVERWHELM = "overwhelmed"
    ANGER = "angry"
    CONFUSION = "confused"
    GENERAL = "general"


@dataclass
class CopingTool:
    """Data class representing a coping tool"""
    id: str
    name: str
    type: CopingToolType
    description: str
    target_emotions: List[EmotionTarget]
    duration_minutes: int
    difficulty: str  # easy, medium, hard
    instructions: List[str]
    benefits: List[str]
    requirements: List[str]  # What user needs (quiet space, paper, etc.)
    interactive: bool
    guided_steps: Optional[List[Dict[str, Any]]] = None


class BreathingExercises:
    """Collection of breathing-based coping tools"""

    @staticmethod
    def get_478_breathing() -> CopingTool:
        return CopingTool(
            id="breathing_478",
            name="4-7-8 Breathing",
            type=CopingToolType.BREATHING,
            description="A calming breathing technique to reduce anxiety and stress",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY],
            duration_minutes=5,
            difficulty="easy",
            instructions=[
                "Find a comfortable seated position with your back straight",
                "Place the tip of your tongue against the tissue behind your upper front teeth",
                "Exhale completely through your mouth, making a whoosh sound",
                "Close your mouth and inhale through your nose for 4 counts",
                "Hold your breath for 7 counts",
                "Exhale through your mouth for 8 counts, making a whoosh sound",
                "Repeat this cycle 3-4 times"
            ],
            benefits=[
                "Activates the body's relaxation response",
                "Reduces anxiety and stress",
                "Helps with falling asleep",
                "Lowers heart rate and blood pressure"
            ],
            requirements=["Comfortable seating", "Quiet environment"],
            interactive=True,
            guided_steps=[
                {"step": 1, "action": "prepare", "duration": 30, "instruction": "Get comfortable and prepare to begin"},
                {"step": 2, "action": "inhale", "duration": 4, "instruction": "Breathe in through your nose"},
                {"step": 3, "action": "hold", "duration": 7, "instruction": "Hold your breath"},
                {"step": 4, "action": "exhale", "duration": 8, "instruction": "Exhale slowly through your mouth"},
                {"step": 5, "action": "pause", "duration": 2, "instruction": "Rest before the next cycle"}
            ]
        )

    @staticmethod
    def get_box_breathing() -> CopingTool:
        return CopingTool(
            id="breathing_box",
            name="Box Breathing",
            type=CopingToolType.BREATHING,
            description="A structured breathing pattern that promotes calm and focus",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY, EmotionTarget.OVERWHELM],
            duration_minutes=5,
            difficulty="easy",
            instructions=[
                "Sit comfortably with your feet flat on the floor",
                "Exhale completely to empty your lungs",
                "Inhale through your nose for 4 counts",
                "Hold your breath for 4 counts",
                "Exhale through your mouth for 4 counts",
                "Hold empty for 4 counts",
                "Repeat for 5-10 cycles"
            ],
            benefits=[
                "Increases focus and concentration",
                "Reduces stress and anxiety",
                "Regulates the nervous system",
                "Can be done anywhere"
            ],
            requirements=["No special requirements"],
            interactive=True,
            guided_steps=[
                {"step": 1, "action": "inhale", "duration": 4, "instruction": "Breathe in slowly and deeply"},
                {"step": 2, "action": "hold", "duration": 4, "instruction": "Hold your breath gently"},
                {"step": 3, "action": "exhale", "duration": 4, "instruction": "Breathe out slowly and completely"},
                {"step": 4, "action": "hold", "duration": 4, "instruction": "Hold empty, don't force it"}
            ]
        )

    @staticmethod
    def get_belly_breathing() -> CopingTool:
        return CopingTool(
            id="breathing_belly",
            name="Belly Breathing",
            type=CopingToolType.BREATHING,
            description="Deep diaphragmatic breathing to activate relaxation",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY, EmotionTarget.ANGER],
            duration_minutes=7,
            difficulty="easy",
            instructions=[
                "Lie down or sit comfortably with one hand on your chest, one on your belly",
                "Breathe normally and notice which hand moves more",
                "Now breathe in slowly through your nose, letting your belly rise",
                "Your chest should stay relatively still",
                "Exhale slowly through your mouth, letting your belly fall",
                "Continue for 5-10 minutes, focusing on deep belly breaths"
            ],
            benefits=[
                "Activates the parasympathetic nervous system",
                "Reduces physical tension",
                "Improves oxygen flow",
                "Calms racing thoughts"
            ],
            requirements=["Comfortable position", "Quiet space"],
            interactive=True
        )


class GroundingTechniques:
    """Collection of grounding-based coping tools"""

    @staticmethod
    def get_54321_technique() -> CopingTool:
        return CopingTool(
            id="grounding_54321",
            name="5-4-3-2-1 Grounding",
            type=CopingToolType.GROUNDING,
            description="Use your senses to ground yourself in the present moment",
            target_emotions=[EmotionTarget.ANXIETY, EmotionTarget.OVERWHELM, EmotionTarget.STRESS],
            duration_minutes=5,
            difficulty="easy",
            instructions=[
                "Take a deep breath and look around you",
                "Name 5 things you can see (look for details, colors, textures)",
                "Name 4 things you can touch (feel textures, temperatures)",
                "Name 3 things you can hear (near and far sounds)",
                "Name 2 things you can smell (or remember favorite scents)",
                "Name 1 thing you can taste (or think of a favorite flavor)",
                "Take another deep breath and notice how you feel now"
            ],
            benefits=[
                "Brings awareness to the present moment",
                "Interrupts anxious thoughts",
                "Uses all five senses",
                "Can be done anywhere"
            ],
            requirements=["No special requirements"],
            interactive=True
        )

    @staticmethod
    def get_body_scan() -> CopingTool:
        return CopingTool(
            id="grounding_body_scan",
            name="Body Scan Grounding",
            type=CopingToolType.GROUNDING,
            description="Systematically focus on different parts of your body",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY, EmotionTarget.OVERWHELM],
            duration_minutes=10,
            difficulty="medium",
            instructions=[
                "Sit or lie down comfortably",
                "Close your eyes or soften your gaze",
                "Start by noticing your breathing",
                "Focus on the top of your head - notice any sensations",
                "Slowly move your attention down: forehead, eyes, jaw",
                "Continue down your neck, shoulders, arms, hands",
                "Move to your chest, back, stomach",
                "Focus on your hips, thighs, knees, calves, feet",
                "Notice your whole body as one connected unit",
                "Take a few deep breaths before opening your eyes"
            ],
            benefits=[
                "Increases body awareness",
                "Releases physical tension",
                "Promotes relaxation",
                "Grounds you in your physical self"
            ],
            requirements=["Comfortable position", "10 minutes of quiet time"],
            interactive=True
        )


class MindfulnessExercises:
    """Collection of mindfulness-based coping tools"""

    @staticmethod
    def get_mindful_observation() -> CopingTool:
        return CopingTool(
            id="mindfulness_observation",
            name="Mindful Observation",
            type=CopingToolType.MINDFULNESS,
            description="Focus completely on observing one object or element",
            target_emotions=[EmotionTarget.ANXIETY, EmotionTarget.STRESS, EmotionTarget.OVERWHELM],
            duration_minutes=5,
            difficulty="easy",
            instructions=[
                "Choose an object near you (plant, pen, cup, etc.)",
                "Look at it as if you've never seen it before",
                "Notice its color, shape, texture, size",
                "Observe shadows, reflections, imperfections",
                "If your mind wanders, gently return to the object",
                "Spend 3-5 minutes in complete observation",
                "Notice how this focused attention affects your mental state"
            ],
            benefits=[
                "Improves focus and concentration",
                "Breaks rumination cycles",
                "Cultivates present-moment awareness",
                "Reduces mental chatter"
            ],
            requirements=["Any small object", "Quiet environment"],
            interactive=False
        )

    @staticmethod
    def get_mindful_walking() -> CopingTool:
        return CopingTool(
            id="mindfulness_walking",
            name="Mindful Walking",
            type=CopingToolType.MINDFULNESS,
            description="Walk slowly with complete awareness of each step",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY, EmotionTarget.SADNESS],
            duration_minutes=10,
            difficulty="easy",
            instructions=[
                "Find a quiet space where you can walk 10-20 steps",
                "Begin walking very slowly, much slower than normal",
                "Feel your feet lifting, moving, and touching the ground",
                "Notice the shifting of weight from foot to foot",
                "Pay attention to the movement of your legs and arms",
                "When you reach the end, pause and turn around mindfully",
                "Continue for 5-10 minutes, staying present with each step"
            ],
            benefits=[
                "Combines gentle exercise with mindfulness",
                "Grounds you through physical sensation",
                "Can be calming and meditative",
                "Accessible to most people"
            ],
            requirements=["Small walking space", "Comfortable shoes"],
            interactive=False
        )


class JournalingPrompts:
    """Collection of journaling-based coping tools"""

    @staticmethod
    def get_emotion_journaling() -> CopingTool:
        return CopingTool(
            id="journaling_emotions",
            name="Emotion Check-In Journal",
            type=CopingToolType.JOURNALING,
            description="Write about your current emotions to process and understand them",
            target_emotions=[EmotionTarget.SADNESS, EmotionTarget.CONFUSION, EmotionTarget.ANGER, EmotionTarget.GENERAL],
            duration_minutes=10,
            difficulty="easy",
            instructions=[
                "Get a piece of paper or open a document",
                "Write today's date at the top",
                "Complete this sentence: 'Right now I am feeling...'",
                "Describe the emotion in detail - where do you feel it in your body?",
                "Write about what might have triggered this emotion",
                "Ask yourself: 'What does this emotion need from me?'",
                "Write about one small thing you can do to care for yourself",
                "End with: 'I acknowledge my feelings and treat myself with compassion'"
            ],
            benefits=[
                "Increases emotional awareness",
                "Helps process difficult feelings",
                "Provides emotional release",
                "Creates a record of your emotional journey"
            ],
            requirements=["Paper and pen or digital device", "Private space"],
            interactive=False
        )

    @staticmethod
    def get_gratitude_journaling() -> CopingTool:
        return CopingTool(
            id="journaling_gratitude",
            name="Gratitude Practice",
            type=CopingToolType.JOURNALING,
            description="Focus on positive aspects of your life through gratitude",
            target_emotions=[EmotionTarget.SADNESS, EmotionTarget.STRESS, EmotionTarget.GENERAL],
            duration_minutes=5,
            difficulty="easy",
            instructions=[
                "Write down 3 things you're grateful for today",
                "For each item, explain why you're grateful for it",
                "Include at least one small, simple thing (like a warm cup of coffee)",
                "Include one thing about yourself that you appreciate",
                "Write about a person you're thankful for and why",
                "Describe how focusing on gratitude affects your mood"
            ],
            benefits=[
                "Shifts focus to positive aspects of life",
                "Improves mood and outlook",
                "Increases life satisfaction",
                "Builds resilience over time"
            ],
            requirements=["Paper and pen or digital device"],
            interactive=False
        )


class PhysicalTechniques:
    """Collection of physical movement-based coping tools"""

    @staticmethod
    def get_progressive_relaxation() -> CopingTool:
        return CopingTool(
            id="physical_progressive_relaxation",
            name="Progressive Muscle Relaxation",
            type=CopingToolType.PHYSICAL,
            description="Systematically tense and relax muscle groups to release physical stress",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.ANXIETY, EmotionTarget.ANGER],
            duration_minutes=15,
            difficulty="medium",
            instructions=[
                "Lie down or sit comfortably",
                "Start with your toes - curl them tightly for 5 seconds, then relax",
                "Move to your calves - tense for 5 seconds, then release",
                "Continue with thighs, buttocks, stomach, hands, arms, shoulders",
                "Tense your facial muscles, then relax",
                "Finally, tense your whole body for 5 seconds, then completely relax",
                "Notice the contrast between tension and relaxation",
                "Rest in the relaxed state for a few minutes"
            ],
            benefits=[
                "Reduces physical tension and stress",
                "Teaches the difference between tense and relaxed states",
                "Promotes overall relaxation",
                "Can help with sleep"
            ],
            requirements=["Comfortable position", "Quiet space", "15 minutes"],
            interactive=True
        )

    @staticmethod
    def get_gentle_stretching() -> CopingTool:
        return CopingTool(
            id="physical_stretching",
            name="Gentle Stretching",
            type=CopingToolType.PHYSICAL,
            description="Simple stretches to release tension and connect with your body",
            target_emotions=[EmotionTarget.STRESS, EmotionTarget.OVERWHELM, EmotionTarget.SADNESS],
            duration_minutes=7,
            difficulty="easy",
            instructions=[
                "Stand with feet shoulder-width apart",
                "Slowly roll your shoulders back 5 times, then forward 5 times",
                "Gently turn your head left, hold for 10 seconds, then right",
                "Reach your arms overhead and stretch toward the ceiling",
                "Slowly bend to touch your toes (go as far as comfortable)",
                "Place hands on your hips and gently arch your back",
                "End by taking 3 deep breaths with your arms at your sides"
            ],
            benefits=[
                "Releases physical tension",
                "Improves circulation",
                "Connects mind and body",
                "Can be energizing or calming"
            ],
            requirements=["Comfortable clothing", "Small space to move"],
            interactive=False
        )


class CognitiveTechniques:
    """Collection of cognitive-based coping tools"""

    @staticmethod
    def get_thought_challenging() -> CopingTool:
        return CopingTool(
            id="cognitive_thought_challenging",
            name="Thought Challenging",
            type=CopingToolType.COGNITIVE,
            description="Examine and challenge negative or unhelpful thoughts",
            target_emotions=[EmotionTarget.ANXIETY, EmotionTarget.STRESS, EmotionTarget.SADNESS],
            duration_minutes=10,
            difficulty="medium",
            instructions=[
                "Identify the specific thought that's bothering you",
                "Write it down exactly as it appears in your mind",
                "Ask: 'Is this thought completely true?'",
                "Ask: 'What evidence supports this thought?'",
                "Ask: 'What evidence contradicts this thought?'",
                "Ask: 'How would I respond if a friend had this thought?'",
                "Rewrite the thought in a more balanced, realistic way",
                "Notice how this affects your emotional state"
            ],
            benefits=[
                "Reduces impact of negative thinking",
                "Increases rational perspective",
                "Builds cognitive flexibility",
                "Reduces anxiety and depression symptoms"
            ],
            requirements=["Paper and pen", "Quiet time for reflection"],
            interactive=False
        )

    @staticmethod
    def get_worry_time() -> CopingTool:
        return CopingTool(
            id="cognitive_worry_time",
            name="Designated Worry Time",
            type=CopingToolType.COGNITIVE,
            description="Set aside specific time for worries to prevent all-day rumination",
            target_emotions=[EmotionTarget.ANXIETY, EmotionTarget.OVERWHELM, EmotionTarget.STRESS],
            duration_minutes=15,
            difficulty="medium",
            instructions=[
                "Choose a specific 15-minute time slot each day for worrying",
                "When worries come up throughout the day, tell yourself 'I'll think about this during worry time'",
                "During your designated worry time, write down all your concerns",
                "For each worry, ask: 'Can I do something about this?'",
                "If yes, write down one action step you can take",
                "If no, practice accepting uncertainty with phrases like 'I don't know what will happen, and that's okay'",
                "When worry time is over, return to your daily activities",
                "If worries intrude, remind yourself: 'Not now, I have designated time for this'"
            ],
            benefits=[
                "Reduces constant rumination",
                "Creates boundaries around worry",
                "Helps distinguish between productive and unproductive concern",
                "Increases present-moment awareness"
            ],
            requirements=["Paper and pen", "Consistent daily schedule"],
            interactive=False
        )


class CopingToolsService:
    """Main service for managing and delivering coping tools"""

    def __init__(self):
        self._tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all available coping tools"""

        # Breathing exercises
        self._tools["breathing_478"] = BreathingExercises.get_478_breathing()
        self._tools["breathing_box"] = BreathingExercises.get_box_breathing()
        self._tools["breathing_belly"] = BreathingExercises.get_belly_breathing()

        # Grounding techniques
        self._tools["grounding_54321"] = GroundingTechniques.get_54321_technique()
        self._tools["grounding_body_scan"] = GroundingTechniques.get_body_scan()

        # Mindfulness exercises
        self._tools["mindfulness_observation"] = MindfulnessExercises.get_mindful_observation()
        self._tools["mindfulness_walking"] = MindfulnessExercises.get_mindful_walking()

        # Journaling prompts
        self._tools["journaling_emotions"] = JournalingPrompts.get_emotion_journaling()
        self._tools["journaling_gratitude"] = JournalingPrompts.get_gratitude_journaling()

        # Physical techniques
        self._tools["physical_progressive_relaxation"] = PhysicalTechniques.get_progressive_relaxation()
        self._tools["physical_stretching"] = PhysicalTechniques.get_gentle_stretching()

        # Cognitive techniques
        self._tools["cognitive_thought_challenging"] = CognitiveTechniques.get_thought_challenging()
        self._tools["cognitive_worry_time"] = CognitiveTechniques.get_worry_time()

    def get_tools_for_emotion(self, emotion: str, difficulty: str = None, max_duration: int = None) -> List[CopingTool]:
        """
        Get coping tools appropriate for a specific emotion

        Args:
            emotion: Target emotion (stressed, anxious, etc.)
            difficulty: Filter by difficulty (easy, medium, hard)
            max_duration: Maximum duration in minutes

        Returns:
            List of appropriate coping tools
        """
        matching_tools = []

        for tool in self._tools.values():
            # Check if tool targets this emotion
            if emotion in [e.value for e in tool.target_emotions] or EmotionTarget.GENERAL in tool.target_emotions:
                # Apply filters
                if difficulty and tool.difficulty != difficulty:
                    continue
                if max_duration and tool.duration_minutes > max_duration:
                    continue

                matching_tools.append(tool)

        # Sort by relevance (tools specifically targeting the emotion first)
        matching_tools.sort(key=lambda t: 0 if emotion in [e.value for e in t.target_emotions] else 1)

        return matching_tools

    def get_tool_by_id(self, tool_id: str) -> Optional[CopingTool]:
        """Get a specific tool by ID"""
        return self._tools.get(tool_id)

    def get_random_tool_for_emotion(self, emotion: str, difficulty: str = "easy") -> Optional[CopingTool]:
        """Get a random tool appropriate for an emotion"""
        tools = self.get_tools_for_emotion(emotion, difficulty=difficulty)
        if tools:
            return random.choice(tools)
        return None

    def get_tool_recommendations(self, emotion: str, user_preferences: Dict[str, Any] = None) -> List[CopingTool]:
        """
        Get personalized tool recommendations

        Args:
            emotion: Target emotion
            user_preferences: User preferences (e.g., preferred types, time constraints)

        Returns:
            List of recommended tools
        """
        # Get base tools for emotion
        tools = self.get_tools_for_emotion(emotion)

        if not user_preferences:
            return tools[:3]  # Return top 3

        # Apply user preferences
        preferred_types = user_preferences.get("preferred_types", [])
        max_duration = user_preferences.get("max_duration")
        difficulty = user_preferences.get("difficulty")

        filtered_tools = []
        for tool in tools:
            if preferred_types and tool.type.value not in preferred_types:
                continue
            if max_duration and tool.duration_minutes > max_duration:
                continue
            if difficulty and tool.difficulty != difficulty:
                continue
            filtered_tools.append(tool)

        return filtered_tools[:5]  # Return top 5 personalized recommendations

    def get_all_tools(self) -> List[CopingTool]:
        """Get all available coping tools"""
        return list(self._tools.values())

    def get_tools_by_type(self, tool_type: CopingToolType) -> List[CopingTool]:
        """Get all tools of a specific type"""
        return [tool for tool in self._tools.values() if tool.type == tool_type]

    def get_quick_tools(self, max_duration: int = 5) -> List[CopingTool]:
        """Get tools that can be completed quickly"""
        return [tool for tool in self._tools.values() if tool.duration_minutes <= max_duration]

    def create_guided_session(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a guided session for an interactive tool

        Args:
            tool_id: ID of the tool to create session for

        Returns:
            Session data for interactive tools, None for non-interactive tools
        """
        tool = self.get_tool_by_id(tool_id)
        if not tool or not tool.interactive or not tool.guided_steps:
            return None

        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

        return {
            "session_id": session_id,
            "tool_id": tool_id,
            "tool_name": tool.name,
            "total_steps": len(tool.guided_steps),
            "estimated_duration": tool.duration_minutes,
            "steps": tool.guided_steps,
            "created_at": datetime.now().isoformat()
        }

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get statistics about available tools"""
        tools = list(self._tools.values())

        type_counts = {}
        difficulty_counts = {}
        duration_stats = []

        for tool in tools:
            # Count by type
            type_counts[tool.type.value] = type_counts.get(tool.type.value, 0) + 1

            # Count by difficulty
            difficulty_counts[tool.difficulty] = difficulty_counts.get(tool.difficulty, 0) + 1

            # Duration stats
            duration_stats.append(tool.duration_minutes)

        return {
            "total_tools": len(tools),
            "by_type": type_counts,
            "by_difficulty": difficulty_counts,
            "interactive_tools": len([t for t in tools if t.interactive]),
            "average_duration": sum(duration_stats) / len(duration_stats) if duration_stats else 0,
            "duration_range": {
                "min": min(duration_stats) if duration_stats else 0,
                "max": max(duration_stats) if duration_stats else 0
            }
        }


# Global coping tools service instance
coping_service = CopingToolsService()
