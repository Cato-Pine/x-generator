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
**Status:** FRONTEND COMPLETE - X OAuth working, posting functional

### Last Session: Dec 18, 2024
- Added React frontend with all pages (Dashboard, Generate, Approval, Queue, Posted, Trending, Settings)
- X OAuth authentication working (connected as @Cato_Pine)
- Post Now functionality works from Trending page
- Fixed multiple backend bugs (timezone, rate limits, scheduler initialization)

### Completed
- ✅ Phase 1-6: Backend complete
- ✅ Phase 7: React Frontend (Vite + TailwindCSS + React Query)
- ✅ Docker multi-container deployment
- ✅ X OAuth2 with PKCE

### Known Issues / Next Steps
1. **Reply posting**: Replies post as standalone tweets instead of actual replies
   - Need to run SQL: `ALTER TABLE posts ADD COLUMN IF NOT EXISTS reply_to_tweet_id TEXT;`
   - Code is ready - just needs the database column
2. Settings page UI could show X connection status better

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
