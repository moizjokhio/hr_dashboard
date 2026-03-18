# Enterprise HR Analytics & AI System

## Overview
An enterprise-level on-premises HR Analytics and AI system designed for a bank with 100,000 employees. 
The system runs entirely locally with no cloud dependencies or external API calls.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │   Filters    │  │  AI Search   │  │   Reports    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth       │  │   Rate Limit │  │   Logging    │  │   Caching    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Employee Svc    │    │   Analytics Svc  │    │     AI Svc       │
│  ┌────────────┐  │    │  ┌────────────┐  │    │  ┌────────────┐  │
│  │ CRUD Ops   │  │    │  │ Dashboards │  │    │  │ NLP Query  │  │
│  │ Filters    │  │    │  │ KPIs       │  │    │  │ Embeddings │  │
│  │ Search     │  │    │  │ Charts     │  │    │  │ Predictions│  │
│  └────────────┘  │    │  └────────────┘  │    │  └────────────┘  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                       │
│  ┌──────────────────────┐              ┌──────────────────────┐             │
│  │     PostgreSQL       │              │   Qdrant/Milvus      │             │
│  │  ┌────────────────┐  │              │  ┌────────────────┐  │             │
│  │  │ Employees      │  │              │  │ Query Vectors  │  │             │
│  │  │ Analytics      │  │              │  │ Employee Embed │  │             │
│  │  │ Audit Logs     │  │              │  │ Semantic Cache │  │             │
│  │  └────────────────┘  │              │  └────────────────┘  │             │
│  └──────────────────────┘              └──────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL AI MODELS (GPU)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ BGE-Large    │  │ Qwen2 72B    │  │  XGBoost     │  │    SHAP      │     │
│  │ Embeddings   │  │ GGUF/TensorRT│  │  LightGBM    │  │  Explainer   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Components**: ShadCN/UI
- **Charts**: ECharts
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Task Queue**: Celery + Redis
- **Caching**: Redis

### Database
- **Primary**: PostgreSQL 15
- **Vector DB**: Qdrant (or Milvus)
- **Cache**: Redis

### AI/ML Stack
- **Embeddings**: BGE-Large-EN-v1.5 / BGE-M3
- **LLM**: Qwen2-72B-Instruct (GGUF via llama-cpp-python)
- **Predictive Models**: XGBoost, LightGBM, CatBoost
- **Explainability**: SHAP
- **ML Framework**: PyTorch + CUDA

## Project Structure

```
hr-analytics-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core config, security
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── ml/               # ML models & pipelines
│   │   └── workers/          # Background tasks
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── stores/           # Zustand stores
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   └── package.json
├── ml-models/                # Local model files
├── docker/
└── docs/
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- CUDA 11.8+ (for GPU acceleration)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Features

1. **Advanced Filter System** - Stack multiple filter blocks for complex queries
2. **AI Search** - Natural language to SQL conversion
3. **Analytics Dashboards** - Headcount, diversity, compensation, performance
4. **Predictive Models** - Attrition, performance, promotion predictions
5. **Prescriptive Analytics** - SHAP-based recommendations
6. **Report Generation** - PDF, Word, Excel exports

## License
Proprietary - Internal Use Only
