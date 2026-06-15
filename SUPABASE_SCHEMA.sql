-- Run this in Supabase SQL Editor to create the songs table

CREATE TABLE IF NOT EXISTS public.songs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    duration INTEGER DEFAULT 0,
    audio_url TEXT NOT NULL,
    image_url TEXT,
    genre TEXT,
    release_year INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.songs ENABLE ROW LEVEL SECURITY;

-- Allow public read access (since audio URLs are public)
CREATE POLICY "Public read access for songs" ON public.songs
    FOR SELECT USING (true);

-- Allow authenticated users to insert (or use service role key on backend)
CREATE POLICY "Allow insert for authenticated users" ON public.songs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');

-- Allow updates by service role
CREATE POLICY "Allow update for service role" ON public.songs
    FOR UPDATE USING (auth.role() = 'service_role');

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_songs_created_at ON public.songs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_songs_id ON public.songs (id);