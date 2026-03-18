# HR Analytics System - Quick Start Guide

## Prerequisites

1. **Docker & Docker Compose** - for containerized deployment
2. **NVIDIA GPU with CUDA** - for running local AI models (optional but recommended)
3. **At least 32GB RAM** - 64GB recommended for the 72B model
4. **Python 3.11+** - for local development
5. **Node.js 18+** - for frontend development

## Option 1: Docker Deployment (Recommended)

### Step 1: Clone and Configure

```bash
cd hr-analytics-system
cp .env.example .env

# Edit .env with your settings
# At minimum, change:
# - SECRET_KEY
# - POSTGRES_PASSWORD
```

### Step 2: Download AI Models

```bash
# Create models directory
mkdir -p models

# Download Qwen2 72B GGUF (quantized for efficiency)
# Option 1: Q4_K_M quantization (~40GB, good balance)
# From: https://huggingface.co/Qwen/Qwen2-72B-Instruct-GGUF

# Place file in: models/qwen2-72b-instruct.Q4_K_M.gguf

# For smaller systems, you can use Qwen2-7B instead:
# https://huggingface.co/Qwen/Qwen2-7B-Instruct-GGUF
```

### Step 3: Start Services

```bash
# Start infrastructure (database, cache, vector db)
docker-compose up -d postgres redis qdrant

# Wait for services to be healthy
docker-compose ps

# Start backend
docker-compose up -d backend

# Start frontend
docker-compose up -d frontend
```

### Step 4: Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Load your employee data
docker-compose exec backend python scripts/load_data.py \
    --csv /app/data/pak_bank_employees_100k.csv

# Generate embeddings for AI search (optional)
docker-compose exec backend python scripts/load_data.py --embeddings
```

### Step 5: Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/api/v1/health

---

## Option 2: Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hr_analytics
export REDIS_URL=redis://localhost:6379/0
export QDRANT_HOST=localhost

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Loading Your Data

### CSV Format Requirements

Your CSV file should have these columns (see sample in repo):

| Column | Type | Required | Example |
|--------|------|----------|---------|
| Employee_ID | String | Yes | EMP001 |
| Full_Name | String | Yes | Ahmad Khan |
| Department | String | Yes | Operations |
| Grade_Level | String | Yes | OG-2 |
| Branch_City | String | No | Karachi |
| Branch_Country | String | No | Pakistan |
| Date_of_Birth | Date | No | 1990-01-15 |
| Date_of_Joining | Date | No | 2020-03-01 |
| Gender | String | No | Male |
| Total_Monthly_Salary | Number | No | 150000 |
| Performance_Score | Number | No | 4.2 |

### Loading Command

```bash
# For Docker
docker-compose exec backend python scripts/load_data.py \
    --csv /app/data/your_employees.csv

# For local development
python scripts/load_data.py --csv ../your_employees.csv
```

---

## Using the AI Features

### Natural Language Queries

The AI assistant can answer questions like:
- "Show me employees in IT department with salary > 150k"
- "What is the gender distribution across departments?"
- "Find high performers who joined in 2022"
- "Compare attrition rates between Karachi and Lahore"

### Predictive Analytics

Run predictions from the API:

```bash
# Attrition prediction
curl -X POST http://localhost:8000/api/v1/ai/predict/attrition \
  -H "Content-Type: application/json" \
  -d '{"employee_ids": ["EMP001", "EMP002"], "include_explanations": true}'

# Performance prediction
curl -X POST http://localhost:8000/api/v1/ai/predict/performance \
  -H "Content-Type: application/json" \
  -d '{"employee_ids": ["EMP001"]}'
```

---

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `QDRANT_HOST` | Qdrant vector DB host | `localhost` |
| `SECRET_KEY` | JWT signing key | Required for production |
| `EMBEDDING_MODEL_NAME` | Sentence transformer model | `BAAI/bge-large-en-v1.5` |
| `LLM_MODEL_PATH` | Path to GGUF model file | Required for AI features |
| `USE_GPU` | Enable GPU acceleration | `true` |
| `GPU_LAYERS` | Number of layers on GPU | `-1` (all) |

### Model Options

For smaller deployments, you can use lighter models:

| Model | Size | RAM Required | Use Case |
|-------|------|--------------|----------|
| Qwen2-72B-Q4 | ~40GB | 64GB+ | Best quality |
| Qwen2-72B-Q2 | ~28GB | 48GB+ | Good quality |
| Qwen2-7B-Q4 | ~5GB | 16GB+ | Faster, lighter |
| Phi-3-medium | ~8GB | 16GB+ | Alternative |

---

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U postgres -d hr_analytics
```

### Model Loading Issues
```bash
# Check GPU availability
nvidia-smi

# Check model file exists
ls -la models/
```

### Memory Issues
```bash
# Reduce batch size in .env
BATCH_SIZE=500

# Use smaller model quantization
# Q2_K instead of Q4_K_M
```

---

## Support

For issues:
1. Check logs: `docker-compose logs backend`
2. Review error messages in API docs
3. Contact your system administrator
