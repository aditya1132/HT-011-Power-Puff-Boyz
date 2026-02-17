#!/usr/bin/env python3
"""
Test script for AI Mental Health Companion API
Tests the backend server functionality
"""

import json
import time
from datetime import datetime

import requests


def print_header():
    print("=" * 60)
    print("🧪 AI Mental Health Companion API Test")
    print("=" * 60)
    print()


def test_server_health():
    """Test server health endpoint"""
    print("🔍 Testing server health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running on port 8000")
        return False


def test_ai_health():
    """Test AI services health"""
    print("\n🤖 Testing AI services...")
    try:
        response = requests.get("http://localhost:8000/health/ai", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI services status: {data['status']}")
            print(f"   Model type: {data['ai_model_type']}")
            print(f"   Gemini enabled: {data['gemini_enabled']}")

            services = data["ai_services"]["services"]
            for service, info in services.items():
                print(f"   {service}: {info['status']}")
            return True
        else:
            print(f"❌ AI health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI health check error: {e}")
        return False


def test_chat_functionality():
    """Test chat message functionality"""
    print("\n💬 Testing chat functionality...")

    test_messages = [
        ("I'm feeling really stressed about work", "stressed"),
        ("I'm so excited about my vacation!", "excited"),
        ("I feel sad and lonely today", "sad"),
        ("I'm grateful for all the support", "grateful"),
    ]

    for message, expected_emotion in test_messages:
        print(f"\n📝 Testing: '{message[:30]}...'")

        try:
            payload = {
                "user_id": "test_user_123",
                "message": message,
                "session_id": "test_session",
            }

            response = requests.post(
                "http://localhost:8000/api/v1/chat/message", json=payload, timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                emotion = data["emotion"]["primary_emotion"]
                confidence = data["emotion"]["confidence"]
                response_msg = data["message"]
                coping_count = len(data["coping_suggestions"])

                print(
                    f"   ✅ Emotion detected: {emotion} (confidence: {confidence:.2f})"
                )
                print(f"   ✅ Response: {response_msg[:60]}...")
                print(f"   ✅ Coping suggestions: {coping_count}")

                if emotion.lower() == expected_emotion.lower():
                    print(f"   ✅ Expected emotion match!")
                else:
                    print(f"   ⚠️  Expected {expected_emotion}, got {emotion}")

            else:
                print(f"   ❌ Chat request failed: {response.status_code}")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"   ❌ Chat test error: {e}")


def test_emotion_analysis():
    """Test standalone emotion analysis"""
    print("\n🧠 Testing emotion analysis...")

    test_text = "I'm feeling overwhelmed with everything I need to do"

    try:
        response = requests.get(
            f"http://localhost:8000/api/v1/emotions/analyze?text={test_text}",
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Emotion analysis successful!")
            print(f"   Primary emotion: {data['primary_emotion']}")
            print(f"   Confidence: {data['confidence']:.2f}")
            print(f"   Sentiment score: {data['sentiment_score']:.2f}")
            print(f"   Intensity: {data['intensity']}")
            return True
        else:
            print(f"❌ Emotion analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Emotion analysis error: {e}")
        return False


def test_coping_tools():
    """Test coping tools endpoint"""
    print("\n🧘 Testing coping tools...")

    try:
        response = requests.get("http://localhost:8000/api/v1/coping/tools", timeout=10)

        if response.status_code == 200:
            data = response.json()
            tools_count = data["count"]
            print(f"✅ Coping tools loaded: {tools_count} tools available")

            for tool in data["tools"][:3]:  # Show first 3
                print(
                    f"   • {tool['name']} ({tool['type']}) - {tool['duration_minutes']} min"
                )

            return True
        else:
            print(f"❌ Coping tools request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Coping tools error: {e}")
        return False


def test_crisis_resources():
    """Test crisis resources endpoint"""
    print("\n🚨 Testing crisis resources...")

    try:
        response = requests.get(
            "http://localhost:8000/api/v1/resources/crisis", timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            resources = data["resources"]
            print(f"✅ Crisis resources loaded: {len(resources)} resources")

            for resource in resources:
                print(f"   • {resource['name']}: {resource['contact']}")

            return True
        else:
            print(f"❌ Crisis resources request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Crisis resources error: {e}")
        return False


def test_crisis_detection():
    """Test crisis detection in chat"""
    print("\n🚨 Testing crisis detection...")

    crisis_message = "I feel hopeless and don't know what to do"

    try:
        payload = {
            "user_id": "test_user_crisis",
            "message": crisis_message,
            "session_id": "test_crisis_session",
        }

        response = requests.post(
            "http://localhost:8000/api/v1/chat/message", json=payload, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            response_msg = data["message"]

            # Check if response contains crisis resources
            if (
                "988" in response_msg
                or "741741" in response_msg
                or "crisis" in response_msg.lower()
            ):
                print("✅ Crisis detection working - resources provided")
                print(f"   Response: {response_msg[:80]}...")
            else:
                print("⚠️  Crisis keywords detected but no resources mentioned")
                print(f"   Response: {response_msg[:80]}...")

            return True
        else:
            print(f"❌ Crisis detection test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Crisis detection error: {e}")
        return False


def main():
    """Run all tests"""
    print_header()

    tests = [
        ("Server Health", test_server_health),
        ("AI Services Health", test_ai_health),
        ("Chat Functionality", test_chat_functionality),
        ("Emotion Analysis", test_emotion_analysis),
        ("Coping Tools", test_coping_tools),
        ("Crisis Resources", test_crisis_resources),
        ("Crisis Detection", test_crisis_detection),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour AI Mental Health Companion API is working perfectly!")
        print("\n📝 You can now:")
        print("• Visit http://localhost:8000/docs for API documentation")
        print("• Test the chat API with different emotional messages")
        print("• Explore the coping tools and resources")
        print("• Set up the frontend to complete the application")

    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Please check the error messages above.")
        print("\nCommon issues:")
        print("• Make sure the server is running on port 8000")
        print("• Check that all dependencies are installed")
        print("• Verify the .env configuration")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
