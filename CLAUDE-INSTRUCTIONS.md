# x-generator - Claude Instructions

## Setup
**Type:** Code
**Location:**
- Linux: `~/projects/x-generator/`
- Windows: `c:\home\Gungo\projects\x-generator\`
**VCS:** GitHub
**Repository:** https://github.com/Cato-Pine/x-generator
**Branch:** main

## Before Starting
1. `git pull origin main`
2. Read CLAUDE.md for project conventions
3. Check `~/pCloudDrive/1-Projects/Claude/claude-projects/x-generator/x-generator.md` for full plan

## Current Status
**Status:** BACKEND COMPLETE - Docker configured

### Completed (Dec 18, 2024)
- ✅ Phase 1: Core Infrastructure (config, DB clients, virtue support)
- ✅ Phase 2: LLM & RAG (OpenAI, Anthropic, virtue prompts)
- ✅ Phase 3: Generation & Twitter (generator, X OAuth2)
- ✅ Phase 4: Scheduler (APScheduler, randomizer, blackout)
- ✅ Phase 5: API Routes (generate, posts, queue, settings, trending, chat, auth, scheduler)
- ✅ Phase 6: Setup files (requirements.txt, .env.example, scripts/setup_supabase.sql)
- ✅ Docker configuration (Dockerfile, docker-compose.yml)

### Known Issues
1. **Database**: User chose to share Supabase project with auto-twitter-stoic
   - Run `scripts/setup_supabase.sql` to add virtue column and new tables

## Development Setup

**Docker (recommended):**
```bash
cp .env.example .env
# Edit .env with real credentials
docker compose up
```

Uses Python 3.11 + Debian Bookworm (sqlite3 3.40+ included, chromadb works).

**Local development notes:**
- Ubuntu 20.04 has sqlite3 3.31.1, chromadb requires 3.35+
- Use Docker for development to avoid sqlite3 issues

## Resume Checklist
1. Configure `.env` with real Supabase/API credentials
2. Run `scripts/setup_supabase.sql` in Supabase SQL editor
3. Test API: `docker compose up`
4. Build frontend (Phase 7)

## Key Differences from auto-twitter-stoic
| Feature | auto-twitter-stoic | x-generator |
|---------|-------------------|-------------|
| Interface | Discord bot | Web dashboard |
| Posting | n8n workflows | Direct X API |
| Content | Dichotomy of control | All stoic virtues |
| Scheduling | Fixed | Random intervals + blackouts |
| Trending | Shows repeats | Tracks shown/skipped |
