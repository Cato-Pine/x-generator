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
**Status:** SKELETON - Project structure created, no code yet

Project folder initialized with:
- Template files (README, CLAUDE.md, LICENSE, etc.)
- GitHub repo created and pushed
- No backend or frontend code yet

## Implementation Plan
See full plan at: `~/pCloudDrive/1-Projects/Claude/claude-projects/x-generator/x-generator.md`

### Phases:
1. **Project Setup** - DONE
2. **Backend Refactor** - Copy from auto-twitter-stoic, add scheduler
3. **Frontend Dashboard** - React + Vite + Tailwind
4. **Scheduler** - Background posting with random intervals
5. **Content Enhancement** - Virtue-based prompts
6. **Polish & Deploy** - Tests, Docker, DigitalOcean

## Next Steps
When ready to implement:
1. Copy backend code from auto-twitter-stoic
2. Refactor to remove Discord, add scheduler
3. Build React frontend
4. Test and deploy

## Key Differences from auto-twitter-stoic
| Feature | auto-twitter-stoic | x-generator |
|---------|-------------------|-------------|
| Interface | Discord bot | Web dashboard |
| Posting | n8n workflows | Direct X API |
| Content | Dichotomy of control | All stoic virtues |
| Scheduling | Fixed | Random intervals + blackouts |
| Trending | Shows repeats | Tracks shown/skipped |
