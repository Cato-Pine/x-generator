-- x-generator Supabase Database Schema
-- Run this in your Supabase SQL Editor to set up the database

-- =============================================================================
-- POSTS TABLE
-- Stores generated content with virtue classification
-- =============================================================================
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_hash TEXT,
    post_type TEXT DEFAULT 'original',  -- original, reply, quote
    format_type TEXT DEFAULT 'short',   -- short, thread, long
    virtue TEXT,                         -- wisdom, courage, justice, temperance, general
    status TEXT DEFAULT 'pending_review', -- pending_review, approved, posted, rejected, recycled
    x_post_id TEXT,                      -- X/Twitter post ID after posting
    approved_at TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    recycle_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_virtue ON posts(virtue);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

-- =============================================================================
-- QUEUE TABLE
-- Scheduled posts waiting to be published
-- =============================================================================
CREATE TABLE IF NOT EXISTS queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    scheduled_for TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',  -- pending, posted, failed, cancelled
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status);
CREATE INDEX IF NOT EXISTS idx_queue_scheduled ON queue(scheduled_for);

-- =============================================================================
-- SETTINGS TABLE
-- Key-value store for app configuration
-- =============================================================================
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TRENDING CACHE TABLE
-- Track shown/skipped/replied trending tweets to avoid duplicates
-- =============================================================================
CREATE TABLE IF NOT EXISTS trending_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tweet_id TEXT NOT NULL UNIQUE,
    content TEXT,
    username TEXT,
    status TEXT DEFAULT 'shown',  -- shown, skipped, replied
    shown_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trending_tweet_id ON trending_cache(tweet_id);
CREATE INDEX IF NOT EXISTS idx_trending_status ON trending_cache(status);

-- =============================================================================
-- OAUTH TOKENS TABLE
-- Store X OAuth2 tokens securely
-- =============================================================================
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL DEFAULT 'x',
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_oauth_provider ON oauth_tokens(provider);

-- =============================================================================
-- RATE LIMITS TABLE
-- Track X API rate limit usage
-- =============================================================================
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint TEXT NOT NULL,
    daily_count INTEGER DEFAULT 0,
    last_reset_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rate_limits_endpoint ON rate_limits(endpoint);

-- =============================================================================
-- DEFAULT SETTINGS
-- =============================================================================
INSERT INTO settings (key, value) VALUES
    ('scheduler', '{"enabled": false, "intervals": [45, 60, 90, 120], "blackout_start": "23:00", "blackout_end": "05:00", "timezone": "America/New_York", "paused": false}'::jsonb),
    ('generation', '{"default_virtue": null, "format_weights": {"short": 70, "thread": 20, "long": 10}}'::jsonb),
    ('rate_limits', '{"daily_posts": 17, "daily_replies": 10}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- =============================================================================
-- UPDATED_AT TRIGGER
-- Automatically update updated_at column on row changes
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY['posts', 'queue', 'settings', 'oauth_tokens', 'rate_limits'])
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END;
$$;

-- =============================================================================
-- ROW LEVEL SECURITY (Optional - enable if using Supabase Auth)
-- =============================================================================
-- Uncomment these if you want to enable RLS
-- ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE queue ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trending_cache ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE rate_limits ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- CLEANUP OLD DATA (Optional scheduled job)
-- =============================================================================
-- You can create a Supabase Edge Function or pg_cron job to run this periodically:
-- DELETE FROM trending_cache WHERE created_at < NOW() - INTERVAL '30 days';
-- DELETE FROM posts WHERE status = 'rejected' AND created_at < NOW() - INTERVAL '90 days';
