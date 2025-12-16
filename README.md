# x-generator

Stoic-themed X/Twitter content generator with web dashboard, flexible scheduling, and LLM-assisted content refinement.

## Features

- Web dashboard for managing posts
- RAG-powered stoic content generation (all 4 virtues)
- Flexible scheduling with random intervals and blackout windows
- Trending post discovery + manual reply input
- LLM chat panel to refine content
- Direct X API posting (no external dependencies)

## Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Supabase account
- OpenAI and/or Anthropic API keys
- X Developer account (for posting)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Cato-Pine/x-generator.git
   cd x-generator
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   # Backend
   uvicorn src.api.main:app --reload

   # Frontend (separate terminal)
   cd frontend && npm run dev
   ```

## Usage

Access the dashboard at `http://localhost:5173`

### Generate Content
1. Go to Posts page
2. Click "Generate" and select virtue/format
3. Edit if needed
4. Add to queue

### Schedule Posts
1. Go to Settings
2. Configure intervals (45m, 1hr, 2hr)
3. Set blackout windows (e.g., 11pm-5am)
4. Enable scheduler

### Reply to Trending
1. Go to Trending page
2. Auto-discover or paste tweet URL
3. Generate reply
4. Refine with LLM chat if needed

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | - |
| `SUPABASE_KEY` | Supabase anon key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `TWITTERAPI_IO_KEY` | TwitterAPI.io key | - |
| `X_CLIENT_ID` | X OAuth2 client ID | - |
| `X_CLIENT_SECRET` | X OAuth2 secret | - |
| `PORT` | Backend port | `8000` |

## Project Structure

```
x-generator/
├── src/              # Backend source code
│   ├── api/          # FastAPI routes
│   ├── db/           # Database layer
│   ├── llm/          # LLM clients
│   ├── rag/          # Vector store
│   ├── twitter/      # X integration
│   └── scheduler/    # Posting scheduler
├── frontend/         # React frontend
├── data/             # Stoic texts
├── tests/            # Test files
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend && npm test

# Run with coverage
pytest --cov=src
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](LICENSE) for details.
