#!/usr/bin/env python3
"""
Gemini API Integration Setup Script for AI Mental Health Companion

This script helps you set up Google Gemini API integration for your mental health companion.
It will guide you through the configuration process and test the integration.
"""

import os
import secrets
import string
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


def print_header():
    """Print script header"""
    print("=" * 70)
    print("🤖 AI Mental Health Companion - Gemini Integration Setup")
    print("=" * 70)
    print()


def print_step(step: int, title: str):
    """Print step header"""
    print(f"\n📋 Step {step}: {title}")
    print("-" * 50)


def get_user_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()

        if user_input or not required:
            return user_input

        if required:
            print("❌ This field is required. Please enter a value.")


def generate_secret_key() -> str:
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(32))


def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(
            f"❌ Python 3.9+ required. Found: {version.major}.{version.minor}.{version.micro}"
        )
        print("Please upgrade Python and try again.")
        sys.exit(1)

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")


def install_dependencies():
    """Install required dependencies"""
    print_step(2, "Installing Dependencies")

    try:
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        if not in_venv:
            print("⚠️  You're not in a virtual environment.")
            create_venv = get_user_input(
                "Would you like to create one? (y/n)", "y"
            ).lower()

            if create_venv == "y":
                print("Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

                if os.name == "nt":  # Windows
                    activate_script = "venv\\Scripts\\activate.bat"
                else:  # Unix/Linux/Mac
                    activate_script = "source venv/bin/activate"

                print(f"✅ Virtual environment created!")
                print(f"Please activate it with: {activate_script}")
                print("Then run this script again.")
                return False

        print("Installing required packages...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"],
            check=True,
        )
        print("✅ Dependencies installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment_file():
    """Create or update .env file with Gemini configuration"""
    print_step(3, "Setting up Environment Configuration")

    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.gemini.example"

    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists.")
        overwrite = get_user_input(
            "Would you like to update it with Gemini settings? (y/n)", "y"
        ).lower()

        if overwrite != "y":
            print("Skipping environment setup.")
            return load_existing_config(env_file)

    # Get configuration from user
    config = {}

    print("\n🔧 Basic Configuration:")
    config["SECRET_KEY"] = generate_secret_key()
    print(f"Generated secure SECRET_KEY: {config['SECRET_KEY'][:10]}...")

    config["ENVIRONMENT"] = get_user_input(
        "Environment (development/production)", "development"
    )
    config["DATABASE_URL"] = get_user_input(
        "Database URL", "sqlite:///./data/mental_health_companion.db"
    )

    print("\n🤖 Gemini API Configuration:")
    print("Get your API key from: https://makersuite.google.com/app/apikey")

    config["GEMINI_API_KEY"] = get_user_input("Google Gemini API Key")

    if not config["GEMINI_API_KEY"]:
        print("❌ Gemini API key is required for this integration.")
        return None

    config["GEMINI_ENABLED"] = get_user_input(
        "Enable Gemini integration? (True/False)", "True"
    )
    config["AI_MODEL_TYPE"] = get_user_input(
        "AI Model Type (rule_based/gemini/hybrid)", "hybrid"
    )

    advanced = get_user_input("Configure advanced Gemini settings? (y/n)", "n").lower()

    if advanced == "y":
        config["GEMINI_MODEL"] = get_user_input("Gemini Model", "gemini-pro")
        config["GEMINI_TEMPERATURE"] = get_user_input("Temperature (0.0-2.0)", "0.7")
        config["GEMINI_MAX_TOKENS"] = get_user_input("Max Tokens", "512")
        config["USE_GEMINI_FOR_RESPONSES"] = get_user_input(
            "Use Gemini for responses? (True/False)", "True"
        )
        config["USE_GEMINI_FOR_EMOTIONS"] = get_user_input(
            "Use Gemini for emotions? (True/False)", "False"
        )
        config["GEMINI_FALLBACK_ENABLED"] = get_user_input(
            "Enable fallback to rule-based? (True/False)", "True"
        )
    else:
        # Use sensible defaults
        config.update(
            {
                "GEMINI_MODEL": "gemini-pro",
                "GEMINI_TEMPERATURE": "0.7",
                "GEMINI_MAX_TOKENS": "512",
                "USE_GEMINI_FOR_RESPONSES": "True",
                "USE_GEMINI_FOR_EMOTIONS": "False",
                "GEMINI_FALLBACK_ENABLED": "True",
            }
        )

    # Write .env file
    try:
        with open(env_file, "w") as f:
            f.write("# AI Mental Health Companion - Environment Configuration\n")
            f.write(
                f"# Generated by setup_gemini.py on {os.popen('date').read().strip()}\n\n"
            )

            f.write("# Core Settings\n")
            f.write(f"SECRET_KEY={config['SECRET_KEY']}\n")
            f.write(f"ENVIRONMENT={config['ENVIRONMENT']}\n")
            f.write(f"DATABASE_URL={config['DATABASE_URL']}\n\n")

            f.write("# Gemini API Configuration\n")
            f.write(f"GEMINI_API_KEY={config['GEMINI_API_KEY']}\n")
            f.write(f"GEMINI_ENABLED={config['GEMINI_ENABLED']}\n")
            f.write(f"AI_MODEL_TYPE={config['AI_MODEL_TYPE']}\n")
            f.write(f"GEMINI_MODEL={config['GEMINI_MODEL']}\n")
            f.write(f"GEMINI_TEMPERATURE={config['GEMINI_TEMPERATURE']}\n")
            f.write(f"GEMINI_MAX_TOKENS={config['GEMINI_MAX_TOKENS']}\n")
            f.write(f"USE_GEMINI_FOR_RESPONSES={config['USE_GEMINI_FOR_RESPONSES']}\n")
            f.write(f"USE_GEMINI_FOR_EMOTIONS={config['USE_GEMINI_FOR_EMOTIONS']}\n")
            f.write(f"GEMINI_FALLBACK_ENABLED={config['GEMINI_FALLBACK_ENABLED']}\n\n")

            f.write("# CORS Settings\n")
            f.write("ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001\n\n")

            f.write("# Feature Flags\n")
            f.write("CHAT_HISTORY_ENABLED=True\n")
            f.write("MOOD_TRENDS_ENABLED=True\n")
            f.write("DAILY_CHECKIN_ENABLED=True\n")
            f.write("COPING_TOOLS_ENABLED=True\n")

        print(f"✅ Environment file created: {env_file}")
        return config

    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return None


def load_existing_config(env_file: Path) -> Dict[str, str]:
    """Load existing configuration from .env file"""
    config = {}
    try:
        with open(env_file, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key] = value
        return config
    except Exception as e:
        print(f"❌ Failed to load existing config: {e}")
        return {}


def test_gemini_connection(api_key: str):
    """Test Gemini API connection"""
    print_step(4, "Testing Gemini API Connection")

    try:
        # Import and test Gemini
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        print("Testing API connection...")
        response = model.generate_content(
            "Say 'Connection successful' if you can read this."
        )

        if response.candidates and response.candidates[0].content.parts:
            result = response.candidates[0].content.parts[0].text
            print(f"✅ Gemini API connection successful!")
            print(f"Test response: {result}")
            return True
        else:
            print("❌ No response from Gemini API")
            return False

    except ImportError:
        print("❌ google-generativeai package not installed")
        return False
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        print("Please check your API key and internet connection.")
        return False


def setup_database():
    """Initialize database"""
    print_step(5, "Setting up Database")

    try:
        # Create data directory if using SQLite
        data_dir = Path("backend/data")
        data_dir.mkdir(exist_ok=True)

        # Try to import and initialize database
        sys.path.insert(0, str(Path("backend").resolve()))

        from app.database.database import Base, engine

        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        print("✅ Database initialized successfully!")
        return True

    except ImportError as e:
        print(f"⚠️  Could not import database modules: {e}")
        print("You may need to run database initialization manually.")
        return False
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def run_basic_test():
    """Run basic functionality test"""
    print_step(6, "Running Basic Functionality Test")

    try:
        # Add backend to path
        sys.path.insert(0, str(Path("backend").resolve()))

        # Test imports
        from app.ai.gemini_service import gemini_service
        from app.core.config import get_settings

        settings = get_settings()

        print("Testing configuration loading...")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ AI Model Type: {settings.AI_MODEL_TYPE}")
        print(f"✅ Gemini Enabled: {settings.GEMINI_ENABLED}")

        if settings.GEMINI_ENABLED and gemini_service.is_available():
            print("✅ Gemini service is available")

            # Test basic AI processing
            print("\nTesting AI processing...")
            from app.ai.ai_service_manager import ai_service_manager

            # This would be async in real usage, but for testing we'll use a simpler approach
            from app.ai.emotion_detection import emotion_service

            test_result = emotion_service.analyze_emotion(
                "I'm feeling a bit stressed today"
            )
            print(
                f"✅ Emotion detection test: {test_result.primary_emotion} (confidence: {test_result.confidence:.2f})"
            )

        else:
            print("⚠️  Gemini service not available - check your configuration")

        return True

    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        print("The setup completed, but there may be configuration issues.")
        return False


def print_next_steps():
    """Print next steps for user"""
    print("\n" + "=" * 70)
    print("🎉 Setup Complete!")
    print("=" * 70)

    print("\n📝 Next Steps:")
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python -m app.main")
    print("   # Or: uvicorn app.main:app --reload")

    print("\n2. Test the API:")
    print("   Open: http://localhost:8000/docs")
    print("   Try: http://localhost:8000/health/ai")

    print("\n3. Install and start the frontend:")
    print("   cd frontend")
    print("   npm install")
    print("   npm start")

    print("\n4. Test the complete application:")
    print("   Open: http://localhost:3000")
    print("   Send a test message to see Gemini in action!")

    print("\n🔧 Configuration Files:")
    print("   • Backend config: backend/.env")
    print("   • Requirements: backend/requirements.txt")

    print("\n📚 Documentation:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • AI Status: http://localhost:8000/health/ai")

    print("\n⚠️  Important Notes:")
    print("   • Keep your .env file secure and never commit it to version control")
    print("   • Monitor your Gemini API usage and costs")
    print("   • The hybrid mode provides the best reliability")
    print("   • Check logs if you encounter any issues")

    print("\n🆘 Troubleshooting:")
    print("   • If Gemini fails, the system will fallback to rule-based responses")
    print("   • Check your API key if getting authentication errors")
    print("   • Verify your internet connection for API calls")
    print("   • Review the logs in the backend console for details")


def main():
    """Main setup function"""
    print_header()

    try:
        # Step 1: Check Python version
        check_python_version()

        # Step 2: Install dependencies
        if not install_dependencies():
            print("❌ Setup failed at dependency installation.")
            return

        # Step 3: Setup environment
        config = setup_environment_file()
        if not config:
            print("❌ Setup failed at environment configuration.")
            return

        # Step 4: Test Gemini connection
        gemini_key = config.get("GEMINI_API_KEY")
        if gemini_key and config.get("GEMINI_ENABLED", "").lower() == "true":
            if not test_gemini_connection(gemini_key):
                print("⚠️  Gemini connection test failed, but continuing setup...")

        # Step 5: Setup database
        setup_database()

        # Step 6: Run basic test
        run_basic_test()

        # Show next steps
        print_next_steps()

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        print("Please check the error details and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
