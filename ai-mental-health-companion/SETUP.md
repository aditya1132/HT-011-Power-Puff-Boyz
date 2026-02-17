# AI Mental Health Companion - Setup Guide

A comprehensive, production-ready mental health support application with emotion detection, mood tracking, and personalized coping tools.

## 🌟 Project Overview

This hackathon project demonstrates a complete AI-powered mental health companion that provides:
- **Emotion-aware chat interface** with real-time sentiment analysis
- **Interactive coping tools** for stress, anxiety, and emotional support
- **Mood tracking dashboard** with visual trends and insights  
- **Daily check-in system** with streak tracking
- **Safety-first design** with crisis detection and resource suggestions

**⚠️ Important Disclaimer**: This application is designed as a supportive tool and is NOT a replacement for professional mental health care.

## 🏗️ Architecture Overview

```
Frontend (React + TypeScript)     Backend (FastAPI + Python)     Database (SQL Server/SQLite)
├── Chat Interface               ├── Emotion Detection API       ├── Users & Profiles
├── Mood Tracking               ├── Coping Tools Engine         ├── Mood Logs
├── Coping Tools                ├── Response Generation         ├── Chat History  
├── Dashboard & Analytics       ├── Safety Systems              ├── Coping Sessions
└── User Management             └── Data Analytics              └── Safety Logs
```

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.9+** and pip
- **Git** for version control
- **SQL Server** (production) or **SQLite** (development)

### 1. Clone and Setup
```bash
# Clone the repository (or extract from zip)
cd "Healthcare & Fitness/ai-mental-health-companion"

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env

# Frontend setup  
cd ../frontend
npm install
```

### 2. Configure Environment
Edit `backend/.env` with your settings:
```bash
# Quick development setup
ENVIRONMENT=development
SECRET_KEY=your-32-character-secret-key-here
DATABASE_URL=sqlite:///./data/mental_health_companion.db
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Initialize Database
```bash
cd backend
python -m app.database.init_db
```

### 4. Start the Application
```bash
# Terminal 1: Start backend (from backend/ directory)
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend (from frontend/ directory)  
npm start
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Demo Flow

### Complete Demo Scenario (5-10 minutes)

1. **User Registration**
   - Visit http://localhost:3000
   - Click "Get Started" to create a new user
   - Set preferences for coping tools and notifications

2. **Daily Check-In**
   - Click "Daily Check-In"
   - Select mood score (1-5) and add a quick note
   - Observe streak counter and encouraging message

3. **Emotion-Aware Chat**
   - Navigate to "Chat" tab
   - Type: *"I feel really overwhelmed with everything I need to do today"*
   - Watch the system:
     - Detect "overwhelmed" emotion with confidence score
     - Provide validating, supportive response
     - Suggest relevant coping tools
     - Offer follow-up questions

4. **Interactive Coping Tools**
   - Click on suggested "Breathing Exercise"
   - Follow the guided 4-7-8 breathing technique
   - Complete the session and rate helpfulness
   - Try the "5-4-3-2-1 Grounding" technique

5. **Mood Tracking**
   - Go to "Mood Log" 
   - Log detailed mood entry with triggers
   - Add notes about the day's challenges
   - View the automatically generated insights

6. **Dashboard Analytics**
   - Visit "Dashboard" for comprehensive overview
   - Explore mood trends over time
   - Review coping tool effectiveness
   - Check achievements and milestones

7. **Safety Features** (Optional)
   - Test crisis detection by typing concerning phrases
   - Observe safety interventions and resource suggestions
   - Note how the system maintains supportive boundaries

## 📊 Sample Data

The system automatically creates a demo user with sample data including:
- **10 days of mood logs** with various emotions and scores
- **5 coping sessions** with different tools and completion rates
- **Chat history** demonstrating emotion detection
- **Streak tracking** showing consistent check-ins

## 🔧 Detailed Setup Instructions

### Backend Configuration

#### Database Options

**Development (SQLite)**:
```env
DATABASE_URL=sqlite:///./data/mental_health_companion.db
```

**Production (SQL Server)**:
```env
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
```

**Azure SQL Database**:
```env
DATABASE_URL=mssql+pyodbc://username:password@server.database.windows.net/database?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30
```

#### Security Configuration
```env
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key

# CORS for frontend access
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Safety features
SAFETY_KEYWORDS_ENABLED=True
CRISIS_DETECTION_SENSITIVITY=medium
```

#### AI/NLP Configuration
```env
# Built-in rule-based emotion detection
AI_MODEL_TYPE=rule_based
EMOTION_DETECTION_THRESHOLD=0.6

# Optional: Advanced AI features
# OPENAI_API_KEY=your-openai-key
# HUGGINGFACE_API_KEY=your-huggingface-key
```

### Frontend Configuration

#### Environment Variables
Create `frontend/.env`:
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

#### Build for Production
```bash
cd frontend
npm run build
```

### Database Management

#### Initialize Database
```bash
cd backend
python -m app.database.init_db init
```

#### Reset Database (Development)
```bash
python -m app.database.init_db reset
```

#### Verify Installation
```bash
python -m app.database.init_db verify
```

## 🎨 Customization Guide

### Adding New Coping Tools

1. **Backend**: Edit `backend/app/ai/coping_tools.py`
```python
@staticmethod
def get_custom_tool() -> CopingTool:
    return CopingTool(
        id="custom_technique",
        name="Custom Coping Technique",
        type=CopingToolType.MINDFULNESS,
        description="Your custom technique description",
        target_emotions=[EmotionTarget.STRESS],
        duration_minutes=5,
        difficulty="easy",
        instructions=["Step 1", "Step 2", "Step 3"],
        benefits=["Benefit 1", "Benefit 2"],
        requirements=["Quiet space"],
        interactive=True
    )
```

2. **Frontend**: Add to `frontend/src/components/CopingTools/`

### Customizing Emotion Detection

Edit `backend/app/ai/emotion_detection.py`:
```python
# Add new emotion keywords
"custom_emotion": {
    "keywords": ["keyword1", "keyword2"],
    "phrases": [r"phrase\s+pattern"],
    "intensifiers": ["very", "extremely"],
    "weight": 1.0
}
```

### Styling and Themes

Modify `frontend/tailwind.config.js` for custom colors:
```javascript
colors: {
  'custom-primary': '#your-color',
  'custom-secondary': '#your-color',
}
```

## 🔒 Security and Privacy

### Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Privacy Controls**: User-configurable data retention
- **Minimal Collection**: Only essential data stored
- **Local Storage**: Sensitive operations use local storage when possible

### Safety Systems
- **Crisis Detection**: Keyword-based detection with resource suggestions
- **Professional Boundaries**: Clear limitations about AI capabilities
- **Resource Integration**: Crisis hotlines and professional help suggestions
- **Audit Logging**: All safety events logged for review

### GDPR Compliance
- User data export functionality
- Right to deletion (account deletion API)
- Consent management for data processing
- Privacy policy integration points

## 🚀 Deployment Guide

### Frontend Deployment (Netlify/Vercel)

**Netlify**:
```bash
cd frontend
npm run build
# Deploy the build/ folder to Netlify
```

**Vercel**:
```bash
cd frontend  
vercel --prod
```

### Backend Deployment (Heroku/Azure/AWS)

**Docker Deployment**:
```dockerfile
# Create Dockerfile in backend/
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables for Production**:
```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=your-production-database-url
ALLOWED_ORIGINS=https://your-domain.com
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=True
```

### Database Deployment

**Azure SQL Database**:
1. Create Azure SQL Database
2. Configure connection string
3. Run migrations: `python -m app.database.init_db`

**AWS RDS**:
1. Create RDS SQL Server instance
2. Configure VPC and security groups
3. Update DATABASE_URL in environment

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
python -m pytest tests/test_api.py::test_chat_endpoint
```

### Frontend Testing  
```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End Testing
```bash
# Using Cypress or Playwright
cd frontend
npm run test:e2e
```

## 📊 Monitoring and Analytics

### Health Monitoring
- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics` (if Prometheus enabled)
- **Database Status**: `GET /api/v1/system/status`

### Performance Monitoring
```env
# Enable monitoring
PROMETHEUS_METRICS_ENABLED=True
LOG_LEVEL=INFO
LOG_FILE=/var/log/mental-health-companion/app.log
```

### User Analytics (Privacy-Respecting)
- Aggregated usage statistics
- Feature adoption rates  
- Performance metrics
- Error tracking (without PII)

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**:
```bash
# Check connection string
python -c "from app.database.database import test_connection; print(test_connection())"

# Verify SQL Server is running
# For SQLite, ensure directory exists
```

**CORS Errors**:
```env
# Update backend .env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Port Already in Use**:
```bash
# Backend (change port)
uvicorn app.main:app --reload --port 8001

# Frontend (change port)  
PORT=3001 npm start
```

**Module Not Found**:
```bash
# Backend - ensure virtual environment activated
pip install -r requirements.txt

# Frontend - clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode
```env
# Backend debugging
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_ECHO=True

# Frontend debugging  
REACT_APP_DEBUG=true
```

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Make changes and test thoroughly
3. Run linting: `npm run lint` / `flake8`
4. Submit pull request with clear description

### Code Standards
- **Backend**: Black formatting, type hints, docstrings
- **Frontend**: Prettier formatting, TypeScript strict mode
- **Testing**: Unit tests for new features
- **Documentation**: Update relevant docs

## 📋 API Documentation

### Key Endpoints

**Chat Interface**:
- `POST /api/v1/chat/message` - Send message to AI companion
- `GET /api/v1/chat/history/{user_id}` - Get chat history

**Mood Tracking**:
- `POST /api/v1/mood/log` - Log mood entry
- `GET /api/v1/mood/history/{user_id}` - Get mood history
- `GET /api/v1/mood/trends/{user_id}` - Get mood trends and insights

**Coping Tools**:
- `GET /api/v1/coping/tools` - Get available coping tools
- `POST /api/v1/coping/session/start` - Start coping session
- `PUT /api/v1/coping/session/complete` - Complete session

**Dashboard**:
- `GET /api/v1/dashboard/overview/{user_id}` - Get dashboard data
- `GET /api/v1/dashboard/quick-stats/{user_id}` - Get quick stats

Full API documentation available at: http://localhost:8000/docs

## 🏆 Hackathon Optimization

### Demo Highlights
1. **Real-time Emotion Detection**: Live sentiment analysis with confidence scores
2. **Interactive Coping Tools**: Guided breathing exercises and grounding techniques
3. **Safety-First Design**: Crisis detection with appropriate resources
4. **Modern UI/UX**: Calm, supportive design with accessibility features
5. **Comprehensive Analytics**: Mood trends, insights, and progress tracking

### Technical Excellence
- **Clean Architecture**: Modular, testable, scalable codebase
- **Type Safety**: Full TypeScript implementation
- **Error Handling**: Comprehensive error management and logging
- **Performance**: Optimized for fast response times
- **Security**: Built-in safety systems and data protection

### Social Impact
- **Accessibility**: Mental health support for teens and young adults
- **Privacy-First**: User control over personal data
- **Educational**: Promotes mental health awareness and coping skills
- **Scalable**: Designed to support thousands of users

## 📞 Support and Resources

### Crisis Resources
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **International**: https://www.iasp.info/resources/Crisis_Centres/

### Technical Support
- Check the troubleshooting section above
- Review API documentation at `/docs`
- Examine logs in console/terminal output
- Test individual components with provided endpoints

### Mental Health Resources
- **NAMI (National Alliance on Mental Illness)**: nami.org
- **Mental Health America**: mhanational.org
- **Anxiety and Depression Association**: adaa.org

---

## 🎉 Congratulations!

You now have a fully functional AI-powered mental health companion that demonstrates:
- Advanced emotion detection and response generation
- Interactive coping tools and mood tracking
- Safety-first design with crisis intervention
- Modern, accessible user interface
- Comprehensive analytics and insights

This project showcases production-ready code, ethical AI design, and meaningful social impact - perfect for hackathon presentation and real-world deployment.

**Remember**: This tool supports mental health journeys but never replaces professional care. Always encourage users to seek qualified help when needed.