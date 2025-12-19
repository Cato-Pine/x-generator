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
**Status:** BACKEND COMPLETE - Testing in progress

### Completed (Dec 18, 2024)
- ✅ Phase 1: Core Infrastructure (config, DB clients, virtue support)
- ✅ Phase 2: LLM & RAG (OpenAI, Anthropic, virtue prompts)
- ✅ Phase 3: Generation & Twitter (generator, X OAuth2)
- ✅ Phase 4: Scheduler (APScheduler, randomizer, blackout)
- ✅ Phase 5: API Routes (generate, posts, queue, settings, trending, chat, auth, scheduler)
- ✅ Phase 6: Setup files (requirements.txt, .env.example, scripts/setup_supabase.sql)

### In Progress
- Testing API startup - **Python 3.14 compatibility issue with chromadb**
- RAG module made optional (works without chromadb)
- Need to continue fixing import errors

### Known Issues
1. **chromadb incompatible with Python 3.14** - onnxruntime not available
   - Workaround: RAG is now optional, API runs without it
   - Some import errors remain in generate.py route
2. **Database**: User chose to share Supabase project with auto-twitter-stoic
   - Run `scripts/setup_supabase.sql` to add virtue column and new tables

## Resume Checklist
1. Continue fixing import errors for Python 3.14 compatibility
2. Test API startup: `uvicorn src.api.main:app --reload`
3. Test key endpoints once running
4. Build frontend (Phase 7)

## Files Modified for RAG Optional
- `src/rag/__init__.py` - Lazy loading, graceful degradation
- `src/generators/twitter_generator.py` - Optional retriever
- `src/api/routes/generate.py` - Optional RAG imports (needs more work)

## Implementation Plan
See full plan at: `C:\Users\Gungo\.claude\plans\valiant-fluttering-phoenix.md`

## Key Differences from auto-twitter-stoic
| Feature | auto-twitter-stoic | x-generator |
|---------|-------------------|-------------|
| Interface | Discord bot | Web dashboard |
| Posting | n8n workflows | Direct X API |
| Content | Dichotomy of control | All stoic virtues |
| Scheduling | Fixed | Random intervals + blackouts |
| Trending | Shows repeats | Tracks shown/skipped |
