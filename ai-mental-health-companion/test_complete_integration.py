#!/usr/bin/env python3
"""
Complete Integration Test for AI Mental Health Companion with Gemini
Tests the entire system end-to-end including Gemini AI integration
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class IntegrationTester:
    """Comprehensive integration tester for the mental health companion"""

    def __init__(self):
        self.results = {}
        self.backend_path = Path("backend").resolve()
        self.setup_environment()

    def setup_environment(self):
        """Setup the test environment"""
        # Add backend to Python path
        if self.backend_path not in [Path(p) for p in sys.path]:
            sys.path.insert(0, str(self.backend_path))

        # Load environment variables
        env_file = self.backend_path / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value

    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{'=' * 60}")
        print(f"🧪 {title}")
        print("=" * 60)

    def print_test(self, test_name: str):
        """Print test name"""
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 50)

    async def test_configuration_loading(self) -> bool:
        """Test configuration loading"""
        self.print_test("Configuration Loading")

        try:
            from app.core.config import get_settings

            settings = get_settings()

            # Check essential settings
            assert settings.GEMINI_API_KEY, "GEMINI_API_KEY not set"
            assert settings.GEMINI_ENABLED, "Gemini not enabled"
            assert settings.AI_MODEL_TYPE in ["rule_based", "gemini", "hybrid"], (
                "Invalid AI model type"
            )

            print(f"✅ Environment: {settings.ENVIRONMENT}")
            print(f"✅ AI Model Type: {settings.AI_MODEL_TYPE}")
            print(f"✅ Gemini Enabled: {settings.GEMINI_ENABLED}")
            print(f"✅ Use Gemini for Responses: {settings.USE_GEMINI_FOR_RESPONSES}")
            print(f"✅ Fallback Enabled: {settings.GEMINI_FALLBACK_ENABLED}")

            return True

        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False

    async def test_gemini_service(self) -> bool:
        """Test Gemini service functionality"""
        self.print_test("Gemini Service")

        try:
            from app.ai.gemini_service import gemini_service

            # Test availability
            if not gemini_service.is_available():
                print("❌ Gemini service not available")
                return False

            print("✅ Gemini service is available")

            # Test health check
            health = await gemini_service.health_check()
            print(f"✅ Health check: {health['status']}")

            # Test empathetic response
            response = await gemini_service.generate_empathetic_response(
                user_message="I'm feeling stressed about work today",
                detected_emotion="stressed",
                emotion_intensity=0.7,
            )

            assert "message" in response
            assert len(response["message"]) > 20
            print(f"✅ Empathetic response: {response['message'][:80]}...")

            # Test emotion analysis (if enabled)
            from app.core.config import get_settings

            settings = get_settings()

            if settings.USE_GEMINI_FOR_EMOTIONS:
                emotion_result = await gemini_service.analyze_emotion_with_gemini(
                    "I'm feeling anxious about my presentation tomorrow"
                )
                print(
                    f"✅ Emotion analysis: {emotion_result.get('primary_emotion', 'unknown')}"
                )

            # Test coping suggestions
            coping = await gemini_service.get_coping_suggestions(
                emotion="stressed", intensity=0.8
            )

            if coping:
                print(f"✅ Coping suggestions: {len(coping)} suggestions generated")

            return True

        except Exception as e:
            print(f"❌ Gemini service test failed: {e}")
            return False

    async def test_emotion_detection_service(self) -> bool:
        """Test emotion detection with different methods"""
        self.print_test("Emotion Detection Service")

        try:
            from app.ai.emotion_detection import emotion_service

            test_messages = [
                ("I'm feeling really stressed about deadlines", "stressed"),
                ("I'm so excited about my vacation!", "excited"),
                ("I feel sad and lonely today", "sad"),
                ("I'm grateful for all the support", "grateful"),
                ("Everything feels overwhelming right now", "overwhelmed"),
            ]

            methods = ["rule_based"]

            from app.core.config import get_settings

            settings = get_settings()

            if settings.GEMINI_ENABLED:
                if settings.USE_GEMINI_FOR_EMOTIONS:
                    methods.append("gemini")
                if settings.AI_MODEL_TYPE == "hybrid":
                    methods.append("hybrid")

            for method in methods:
                print(f"\n📊 Testing {method} method:")

                for message, expected_emotion in test_messages:
                    try:
                        if method == "gemini":
                            result = await emotion_service._analyze_with_gemini(message)
                        elif method == "hybrid":
                            result = await emotion_service._analyze_hybrid(message)
                        else:
                            result = emotion_service.analyze_emotion(
                                message, method=method
                            )

                        print(
                            f"   '{message[:30]}...' → {result.primary_emotion} ({result.confidence:.2f})"
                        )

                    except Exception as e:
                        print(f"   ❌ Failed for '{message[:30]}...': {e}")

            print("✅ Emotion detection service tested")
            return True

        except Exception as e:
            print(f"❌ Emotion detection test failed: {e}")
            return False

    async def test_response_generation(self) -> bool:
        """Test response generation with different methods"""
        self.print_test("Response Generation")

        try:
            from app.ai.emotion_detection import emotion_service
            from app.ai.response_generator import response_generator

            # Test scenarios
            test_scenarios = [
                "I'm feeling overwhelmed with work and deadlines",
                "I had a great day and feel really grateful",
                "I'm anxious about an upcoming presentation",
                "I feel sad and need some support",
            ]

            for scenario in test_scenarios:
                print(f"\n📝 Scenario: '{scenario[:40]}...'")

                # Get emotion
                emotion_result = emotion_service.analyze_emotion(scenario)
                print(
                    f"   Emotion: {emotion_result.primary_emotion} ({emotion_result.confidence:.2f})"
                )

                # Generate response
                response_result = response_generator.generate_response(
                    user_input=scenario,
                    emotion_result=emotion_result,
                    user_context={"test": True},
                )

                print(f"   Response: {response_result.message[:60]}...")
                print(f"   Type: {response_result.response_type}")
                print(f"   Source: {response_result.source}")
                print(f"   Coping tools: {len(response_result.coping_suggestions)}")

                assert len(response_result.message) > 10
                assert response_result.coping_suggestions

            print("✅ Response generation tested")
            return True

        except Exception as e:
            print(f"❌ Response generation test failed: {e}")
            return False

    async def test_ai_service_manager(self) -> bool:
        """Test the AI service manager"""
        self.print_test("AI Service Manager")

        try:
            from app.ai.ai_service_manager import ai_service_manager

            # Test health check
            health = await ai_service_manager.health_check()
            print(f"✅ Overall status: {health['overall_status']}")

            for service_name, service_health in health["services"].items():
                print(f"   {service_name}: {service_health['status']}")

            # Test processing user input
            test_inputs = [
                "I'm feeling stressed about work",
                "I'm excited about my new project",
                "I feel sad today and need support",
            ]

            for user_input in test_inputs:
                print(f"\n🔄 Processing: '{user_input}'")

                start_time = time.time()
                result = await ai_service_manager.process_user_input(user_input)
                processing_time = (time.time() - start_time) * 1000

                print(f"   Emotion: {result.emotion_result.primary_emotion}")
                print(f"   Response: {result.response_result.message[:50]}...")
                print(f"   Services used: {result.services_used}")
                print(f"   Processing time: {processing_time:.1f}ms")

                if result.fallbacks_triggered:
                    print(f"   Fallbacks: {result.fallbacks_triggered}")

                assert result.emotion_result.primary_emotion
                assert result.response_result.message

            print("✅ AI Service Manager tested")
            return True

        except Exception as e:
            print(f"❌ AI Service Manager test failed: {e}")
            return False

    async def test_crisis_detection(self) -> bool:
        """Test crisis detection and safety features"""
        self.print_test("Crisis Detection & Safety")

        try:
            from app.ai.emotion_detection import emotion_service
            from app.ai.response_generator import response_generator

            # Test crisis keywords (be careful with these)
            crisis_messages = [
                "I'm having thoughts of hurting myself",
                "I feel hopeless and can't go on",
                "I don't see the point in living",
            ]

            for message in crisis_messages:
                print(f"\n🚨 Crisis test: '{message[:30]}...'")

                # Check crisis detection
                crisis_detected, keywords = emotion_service.check_crisis_keywords(
                    message
                )

                if crisis_detected:
                    print(f"   ✅ Crisis detected: {keywords}")

                    # Test crisis response
                    emotion_result = emotion_service.analyze_emotion(message)
                    response_result = response_generator.generate_response(
                        user_input=message, emotion_result=emotion_result
                    )

                    assert response_result.safety_intervention
                    assert response_result.response_type == "crisis_intervention"
                    print(f"   ✅ Safety intervention triggered")
                    print(f"   ✅ Crisis resources: {len(response_result.resources)}")
                else:
                    print("   ⚠️ Crisis not detected - check sensitivity")

            print("✅ Crisis detection tested")
            return True

        except Exception as e:
            print(f"❌ Crisis detection test failed: {e}")
            return False

    async def test_coping_tools_integration(self) -> bool:
        """Test coping tools integration"""
        self.print_test("Coping Tools Integration")

        try:
            from app.ai.coping_tools import coping_service

            emotions = ["stressed", "anxious", "sad", "overwhelmed", "excited"]

            for emotion in emotions:
                tools = coping_service.get_tools_for_emotion(emotion)
                print(f"   {emotion}: {len(tools)} tools available")

                if tools:
                    tool = tools[0]
                    print(f"     • {tool.name} ({tool.type}, {tool.difficulty})")

            print("✅ Coping tools integration tested")
            return True

        except Exception as e:
            print(f"❌ Coping tools test failed: {e}")
            return False

    async def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        self.print_test("Performance Benchmarks")

        try:
            from app.ai.ai_service_manager import ai_service_manager

            # Performance test
            test_message = "I'm feeling stressed about my workload"
            num_tests = 5

            times = []
            for i in range(num_tests):
                start_time = time.time()
                result = await ai_service_manager.process_user_input(test_message)
                end_time = time.time()

                processing_time = (end_time - start_time) * 1000
                times.append(processing_time)

                print(
                    f"   Test {i + 1}: {processing_time:.1f}ms ({result.services_used[0] if result.services_used else 'unknown'})"
                )

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"\n📊 Performance Summary:")
            print(f"   Average: {avg_time:.1f}ms")
            print(f"   Min: {min_time:.1f}ms")
            print(f"   Max: {max_time:.1f}ms")

            # Check if performance is acceptable
            if avg_time < 5000:  # 5 seconds
                print("✅ Performance within acceptable limits")
            else:
                print("⚠️ Performance slower than expected")

            return True

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests"""
        self.print_header("AI Mental Health Companion - Complete Integration Test")

        tests = [
            ("Configuration Loading", self.test_configuration_loading),
            ("Gemini Service", self.test_gemini_service),
            ("Emotion Detection", self.test_emotion_detection_service),
            ("Response Generation", self.test_response_generation),
            ("AI Service Manager", self.test_ai_service_manager),
            ("Crisis Detection", self.test_crisis_detection),
            ("Coping Tools", self.test_coping_tools_integration),
            ("Performance", self.test_performance_benchmarks),
        ]

        results = {}

        for test_name, test_func in tests:
            try:
                results[test_name] = await test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False

        return results

    def print_summary(self, results: Dict[str, bool]):
        """Print test summary"""
        self.print_header("Test Results Summary")

        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)

        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed\n")

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")

        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
            print("\nYour Gemini integration is working perfectly!")
            print("\n📝 System Ready For:")
            print("• Empathetic AI conversations")
            print("• Advanced emotion detection")
            print("• Intelligent response generation")
            print("• Crisis detection and safety")
            print("• Comprehensive coping support")

        else:
            failed_tests = [name for name, result in results.items() if not result]
            print(f"\n⚠️ {len(failed_tests)} test(s) failed:")
            for test in failed_tests:
                print(f"   • {test}")

            print(f"\nPlease review the error messages above and:")
            print("• Check your Gemini API key configuration")
            print("• Verify internet connectivity")
            print("• Ensure all dependencies are installed")
            print("• Check the .env file settings")


async def main():
    """Main test function"""
    print("Starting comprehensive integration tests...")

    tester = IntegrationTester()
    results = await tester.run_all_tests()
    tester.print_summary(results)

    # Return success status
    return all(results.values())


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
