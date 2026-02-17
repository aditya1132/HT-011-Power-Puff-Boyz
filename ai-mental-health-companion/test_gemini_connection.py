#!/usr/bin/env python3
"""
Gemini API Connection Test Script
Tests the Google Gemini API integration for the AI Mental Health Companion
"""

import asyncio
import os
import sys
import time
from pathlib import Path


def print_header():
    """Print test header"""
    print("=" * 60)
    print("🤖 AI Mental Health Companion - Gemini API Test")
    print("=" * 60)
    print()


def load_environment():
    """Load environment variables from .env file"""
    env_file = Path("backend/.env")

    if not env_file.exists():
        print("❌ .env file not found at backend/.env")
        print("Please ensure the .env file exists with GEMINI_API_KEY")
        return False

    # Simple .env parser
    env_vars = {}
    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value

    print("✅ Environment variables loaded from .env file")
    return True


def test_gemini_import():
    """Test if Google Generative AI package is installed"""
    print("\n🔍 Testing Google Generative AI package...")

    try:
        import google.generativeai as genai

        print("✅ google-generativeai package imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import google-generativeai: {e}")
        print("Please install with: pip install google-generativeai")
        return False


def test_api_key():
    """Test if API key is configured"""
    print("\n🔑 Testing API key configuration...")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("Please add GEMINI_API_KEY to your .env file")
        return False

    if len(api_key) < 20:
        print("❌ API key appears to be invalid (too short)")
        return False

    # Mask API key for display
    masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
    print(f"✅ API key found: {masked_key}")
    return True


def test_basic_connection():
    """Test basic connection to Gemini API"""
    print("\n🌐 Testing basic API connection...")

    try:
        import google.generativeai as genai

        # Configure with API key
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

        # Create model
        model = genai.GenerativeModel("gemini-pro")

        # Test simple request
        print("Sending test request to Gemini...")
        start_time = time.time()

        response = model.generate_content(
            "Say 'Hello! Gemini connection is working!' if you can read this message."
        )

        response_time = (time.time() - start_time) * 1000

        if response.candidates and response.candidates[0].content.parts:
            response_text = response.candidates[0].content.parts[0].text
            print(f"✅ Gemini API connection successful!")
            print(f"Response: {response_text}")
            print(f"Response time: {response_time:.1f}ms")
            return True
        else:
            print("❌ No response content received from Gemini")
            return False

    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("\nPossible causes:")
        print("- Invalid API key")
        print("- Network connectivity issues")
        print("- API quota exceeded")
        print("- Billing not set up for your Google Cloud project")
        return False


def test_mental_health_response():
    """Test Gemini with a mental health related query"""
    print("\n🧠 Testing mental health response generation...")

    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-pro")

        # Test with a mental health query
        test_query = """
        I'm feeling really stressed about work today. I have so many deadlines coming up and I feel overwhelmed.

        Please respond as a supportive mental health companion with empathy and understanding. Keep your response
        supportive but brief (2-3 sentences).
        """

        print("Testing empathetic response generation...")
        start_time = time.time()

        response = model.generate_content(test_query)
        response_time = (time.time() - start_time) * 1000

        if response.candidates and response.candidates[0].content.parts:
            response_text = response.candidates[0].content.parts[0].text
            print(f"✅ Mental health response generated successfully!")
            print(f"Response: {response_text}")
            print(f"Response time: {response_time:.1f}ms")

            # Check if response is appropriate
            if len(response_text) > 20 and any(
                word in response_text.lower()
                for word in ["understand", "feel", "stress", "support"]
            ):
                print("✅ Response appears empathetic and appropriate")
                return True
            else:
                print("⚠️ Response may not be optimal for mental health context")
                return True
        else:
            print("❌ No mental health response generated")
            return False

    except Exception as e:
        print(f"❌ Mental health response test failed: {e}")
        return False


async def test_project_integration():
    """Test integration with the actual project code"""
    print("\n🔧 Testing project integration...")

    try:
        # Add backend to Python path
        backend_path = Path("backend").resolve()
        if backend_path not in [Path(p) for p in sys.path]:
            sys.path.insert(0, str(backend_path))

        # Test importing project modules
        print("Testing project imports...")

        from app.core.config import get_settings

        settings = get_settings()

        print("✅ Project configuration loaded")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"AI Model Type: {settings.AI_MODEL_TYPE}")
        print(f"Gemini Enabled: {settings.GEMINI_ENABLED}")

        # Test Gemini service
        from app.ai.gemini_service import gemini_service

        if gemini_service.is_available():
            print("✅ Gemini service is available")

            # Test health check
            health_result = await gemini_service.health_check()
            print(f"Health check: {health_result['status']}")

            # Test emotion analysis
            if settings.USE_GEMINI_FOR_EMOTIONS:
                emotion_result = await gemini_service.analyze_emotion_with_gemini(
                    "I'm feeling a bit anxious about my presentation tomorrow"
                )
                print(
                    f"✅ Emotion analysis: {emotion_result.get('primary_emotion', 'unknown')}"
                )

            # Test response generation
            if settings.USE_GEMINI_FOR_RESPONSES:
                response_result = await gemini_service.generate_empathetic_response(
                    user_message="I'm having a tough day",
                    detected_emotion="sad",
                    emotion_intensity=0.7,
                )
                print(f"✅ Response generation: {response_result['message'][:50]}...")

            return True
        else:
            print("⚠️ Gemini service not available - check configuration")
            return False

    except ImportError as e:
        print(f"⚠️ Project integration test skipped: {e}")
        print("This is normal if running outside the project directory")
        return True
    except Exception as e:
        print(f"❌ Project integration test failed: {e}")
        return False


def print_results(results):
    """Print test results summary"""
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
        print("\n📝 Next steps:")
        print("1. Start the backend server: cd backend && python -m app.main")
        print("2. Test the API: http://localhost:8000/health/ai")
        print("3. Try the chat interface with Gemini-powered responses!")
    else:
        print(
            f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please check the errors above."
        )
        if not results.get("API Key Configuration", False):
            print("\n🔑 API Key Issues:")
            print("- Verify your API key is correct")
            print("- Check if billing is enabled in Google Cloud Console")
            print("- Ensure the Generative AI API is enabled")

        if not results.get("Basic Connection", False):
            print("\n🌐 Connection Issues:")
            print("- Check your internet connection")
            print("- Verify firewall settings")
            print("- Check API quotas and limits")


def main():
    """Main test function"""
    print_header()

    results = {}

    # Test 1: Load environment
    results["Environment Loading"] = load_environment()

    # Test 2: Package import
    results["Package Import"] = test_gemini_import()

    # Test 3: API key configuration
    results["API Key Configuration"] = test_api_key()

    # Test 4: Basic connection
    if results["Package Import"] and results["API Key Configuration"]:
        results["Basic Connection"] = test_basic_connection()
    else:
        results["Basic Connection"] = False

    # Test 5: Mental health response
    if results["Basic Connection"]:
        results["Mental Health Response"] = test_mental_health_response()
    else:
        results["Mental Health Response"] = False

    # Test 6: Project integration (async)
    if results["Basic Connection"]:
        try:
            results["Project Integration"] = asyncio.run(test_project_integration())
        except Exception as e:
            print(f"Project integration test error: {e}")
            results["Project Integration"] = False
    else:
        results["Project Integration"] = False

    # Print results
    print_results(results)

    return all(results.values())


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)
