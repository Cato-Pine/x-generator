# Project: x-generator

## Overview
Stoic-themed X/Twitter content generator with web dashboard, flexible scheduling, and LLM-assisted content refinement. Fork of auto-twitter-stoic.

## Tech Stack
- **Language**: Python 3.11, TypeScript
- **Backend**: FastAPI
- **Frontend**: React 18, Vite, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Vector Store**: ChromaDB
- **LLMs**: OpenAI GPT-4, Anthropic Claude
- **Testing**: Pytest, Vitest

## Project Structure
```
src/
├── api/              # FastAPI backend
│   ├── routes/       # API endpoints
│   └── models.py     # Pydantic models
├── db/               # Database layer
├── llm/              # LLM clients + prompts
├── rag/              # Knowledge retrieval
├── twitter/          # X/Twitter integration
├── scheduler/        # Posting scheduler
└── utils/            # Helpers
frontend/
├── src/pages/        # React pages
├── src/components/   # UI components
└── src/api/          # API client hooks
tests/                # Test files
scripts/              # Utility scripts
data/                 # Stoic texts for RAG
```

## Commands
```bash
# Backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload

# Frontend
cd frontend && npm install
npm run dev

# Tests
pytest
cd frontend && npm test

# Docker
docker-compose up -d --build
```

## Environment Variables
See `.env.example` for required variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `TWITTERAPI_IO_KEY` - TwitterAPI.io key
- `X_CLIENT_ID` - X OAuth2 client ID
- `X_CLIENT_SECRET` - X OAuth2 client secret

## Architecture Patterns
- **API**: RESTful with FastAPI
- **Database**: Repository pattern with Supabase client
- **LLM**: Strategy pattern for multiple providers
- **RAG**: ChromaDB for vector storage, retrieval augmented generation
- **Scheduler**: Background task with APScheduler

## Important Conventions
- All API routes return JSON with consistent error format
- Database operations go through `src/db/` layer
- LLM prompts organized by stoic virtue in `src/llm/prompts/`
- Character limits validated before saving posts

## Things to Avoid
- Don't commit API keys or credentials
- Don't bypass the scheduler for posting
- Don't generate content without RAG context
- Don't post without rate limit checks

## Key Features
1. **Dashboard**: View/edit/schedule posts
2. **Stoic Virtues**: Wisdom, courage, justice, temperance
3. **Scheduling**: Random intervals, blackout windows
4. **Trending**: Auto-discover + manual input
5. **LLM Chat**: Refine content with AI

## Related Documentation
- [README.md](./README.md) - Setup and usage
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- Full Plan: `~/pCloudDrive/1-Projects/Claude/claude-projects/x-generator/x-generator.md`
