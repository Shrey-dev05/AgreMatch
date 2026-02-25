-- Core Database Schema for Agreggator
-- Compatible with Supabase PostgreSQL

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    skills TEXT[] DEFAULT '{}',
    resume_url TEXT,
    resume_text TEXT, -- Extracted text for LLM parsing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Internships Table
CREATE TABLE internships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    role_type TEXT NOT NULL,
    stipend_min INTEGER DEFAULT 0,
    stipend_max INTEGER DEFAULT 0,
    duration_months INTEGER,
    is_government BOOLEAN DEFAULT false,
    apply_url TEXT NOT NULL,
    location TEXT,
    source TEXT NOT NULL, -- e.g., 'Internshala', 'LinkedIn'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- 3. Hackathons Table
CREATE TABLE hackathons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('virtual', 'in-person', 'hybrid')),
    theme TEXT NOT NULL,
    prize_pool NUMERIC DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    apply_url TEXT NOT NULL,
    source TEXT NOT NULL, -- e.g., 'Devpost', 'Unstop'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. User Applications (Track compatibility scores)
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    internship_id UUID REFERENCES internships(id) ON DELETE CASCADE,
    hackathon_id UUID REFERENCES hackathons(id) ON DELETE CASCADE,
    compatibility_score NUMERIC DEFAULT 0.0, -- Matches based on resume vs posting
    status TEXT DEFAULT 'saved',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (
        (internship_id IS NOT NULL AND hackathon_id IS NULL) OR 
        (internship_id IS NULL AND hackathon_id IS NOT NULL)
    )
);

-- 5. Team-Up Matchmaker (For Hackathons)
CREATE TABLE team_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hackathon_id UUID REFERENCES hackathons(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    looking_for_skills TEXT[] NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'open', -- 'open', 'matched', 'closed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Team Matches (Track successful matchings)
CREATE TABLE team_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_request_id UUID REFERENCES team_requests(id) ON DELETE CASCADE,
    matched_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;
ALTER TABLE hackathons ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_requests ENABLE ROW LEVEL SECURITY;

-- Basic Read access policies
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_internships_role ON internships(role_type);
CREATE INDEX idx_hackathons_theme ON hackathons(theme);
