---
description: Repository Information Overview
alwaysApply: true
---

# Repository Information Overview

## Repository Summary
The **AI-Powered Mental Health Companion** is a comprehensive, production-ready application designed for emotional support, mood tracking, and personalized coping tools. It leverages real-time emotion detection and sentiment analysis to provide empathetic responses and crisis interventions within a safe, ethical framework.

## Repository Structure
The project is organized as a multi-project repository with distinct frontend and backend services located within the `ai-mental-health-companion/` directory.

### Main Repository Components
- **Frontend**: A modern React and TypeScript application featuring responsive design and advanced animations using Framer Motion.
- **Backend**: A robust FastAPI and Python-based API providing the core AI logic, database management, and business services.
- **Demo Tools**: Includes a standalone `demo.html` and `start_demo.bat` for quick visualization and testing.

## Projects

### Frontend (React Application)
**Configuration File**: [./ai-mental-health-companion/frontend/package.json](./ai-mental-health-companion/frontend/package.json)

#### Language & Runtime
**Language**: TypeScript  
**Version**: Node.js 18+  
**Build System**: react-scripts  
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- `react` (^18.2.0)
- `react-router-dom` (^6.8.1)
- `framer-motion` (^10.8.5) (Advanced Animations)
- `tailwindcss` (^3.2.7) (Responsive Design)
- `axios` (^1.3.4)
- `react-query` (^3.39.3)
- `chart.js` (^4.2.1)

**Development Dependencies**:
- `typescript` (^4.9.5)
- `eslint` (^8.35.0)
- `prettier` (^2.8.4)

#### Build & Installation
```bash
cd "ai-mental-health-companion/frontend"
npm install
npm run build
```

#### Testing
**Framework**: Jest (via react-scripts)
**Test Location**: `src/**/*.test.ts`, `src/**/*.test.tsx`
**Run Command**:
```bash
npm test
```

### Backend (FastAPI API)
**Configuration File**: [./ai-mental-health-companion/backend/requirements.txt](./ai-mental-health-companion/backend/requirements.txt)

#### Language & Runtime
**Language**: Python  
**Version**: 3.9+  
**Build System**: uvicorn  
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- `fastapi` (0.103.2)
- `sqlalchemy` (2.0.21)
- `textblob` (0.17.1) (AI/NLP)
- `vaderSentiment` (3.3.2) (AI/NLP)
- `scikit-learn` (1.3.0) (AI/NLP)
- `pydantic` (2.3.0)

**Development Dependencies**:
- `pytest` (7.4.0)
- `black` (23.7.0)
- `mypy` (1.5.1)

#### Build & Installation
```bash
cd "ai-mental-health-companion/backend"
pip install -r requirements.txt
python -m app.database.init_db
```

#### Testing
**Framework**: Pytest
**Test Location**: `backend/tests/`
**Run Command**:
```bash
pytest
```

#### Usage & Operations
**Startup Script**:
```bash
uvicorn app.main:app --reload --port 8000
```
**API Entry Point**: [./ai-mental-health-companion/backend/app/main.py](./ai-mental-health-companion/backend/app/main.py)
