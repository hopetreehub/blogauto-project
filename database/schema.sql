-- Blog Auto Process Database Schema

-- Users table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Countries table for keyword analysis by region
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(2) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Keywords table for storing analyzed keywords
CREATE TABLE IF NOT EXISTS keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword VARCHAR(500) NOT NULL,
    country_id INTEGER REFERENCES countries(id),
    search_volume INTEGER DEFAULT 0,
    competition VARCHAR(20) CHECK (competition IN ('Low', 'Medium', 'High')),
    cpc DECIMAL(10, 2) DEFAULT 0.00,
    opportunity_score INTEGER CHECK (opportunity_score >= 0 AND opportunity_score <= 100),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(keyword, country_id)
);

-- Keyword search history for tracking user searches
CREATE TABLE IF NOT EXISTS keyword_search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    keyword VARCHAR(500) NOT NULL,
    country_id INTEGER REFERENCES countries(id),
    search_params JSONB,
    result_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- CSV export logs for tracking downloads
CREATE TABLE IF NOT EXISTS csv_export_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL, -- 'keywords', 'titles', 'content'
    filename VARCHAR(255) NOT NULL,
    record_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generated titles table
CREATE TABLE IF NOT EXISTS generated_titles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID REFERENCES keywords(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    length_option VARCHAR(20) CHECK (length_option IN ('short', 'medium', 'long')),
    language VARCHAR(5) DEFAULT 'ko',
    tone VARCHAR(20) CHECK (tone IN ('professional', 'casual', 'exciting')),
    duplicate_rate DECIMAL(5, 2) DEFAULT 0.00,
    ai_model VARCHAR(50), -- 'openai', 'gemini', 'huggingface', etc.
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generated content table
CREATE TABLE IF NOT EXISTS generated_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_id UUID REFERENCES generated_titles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    keywords TEXT[], -- Additional keywords used in content
    seo_score INTEGER CHECK (seo_score >= 0 AND seo_score <= 100),
    geo_score INTEGER CHECK (geo_score >= 0 AND geo_score <= 100),
    copyscape_result VARCHAR(20) DEFAULT 'Pending',
    ai_model VARCHAR(50),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generated images table
CREATE TABLE IF NOT EXISTS generated_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES generated_content(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    image_prompt TEXT,
    ai_model VARCHAR(50),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Platform configurations for blog posting
CREATE TABLE IF NOT EXISTS platform_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform_type VARCHAR(50) NOT NULL, -- 'wordpress', 'blogspot', etc.
    platform_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(500),
    auth_token TEXT,
    additional_config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled posts table
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES generated_content(id) ON DELETE CASCADE,
    platform_config_id UUID REFERENCES platform_configs(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Publishing', 'Published', 'Failed')),
    post_url VARCHAR(500),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Post publishing logs
CREATE TABLE IF NOT EXISTS post_publish_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scheduled_post_id UUID REFERENCES scheduled_posts(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User settings and preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    default_language VARCHAR(5) DEFAULT 'ko',
    default_tone VARCHAR(20) DEFAULT 'professional',
    keywords_per_search INTEGER DEFAULT 10,
    titles_per_generation INTEGER DEFAULT 5,
    auto_save BOOLEAN DEFAULT TRUE,
    project_folder VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API keys management
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(50) NOT NULL, -- 'openai', 'gemini', 'semrush', etc.
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, service_name)
);

-- SEO analytics dashboard data
CREATE TABLE IF NOT EXISTS seo_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID REFERENCES generated_content(id) ON DELETE CASCADE,
    url VARCHAR(500),
    page_views INTEGER DEFAULT 0,
    click_through_rate DECIMAL(5, 2) DEFAULT 0.00,
    search_ranking INTEGER,
    keyword_position JSONB, -- Store keyword rankings as JSON
    date_recorded DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(content_id, date_recorded)
);

-- Team permissions (for future team features)
CREATE TABLE IF NOT EXISTS team_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team_id UUID, -- Will reference teams table when implemented
    permission_level VARCHAR(20) DEFAULT 'Member' CHECK (permission_level IN ('Admin', 'Editor', 'Member')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_keywords_country ON keywords(country_id);
CREATE INDEX IF NOT EXISTS idx_keywords_created_by ON keywords(created_by);
CREATE INDEX IF NOT EXISTS idx_keywords_search_volume ON keywords(search_volume DESC);
CREATE INDEX IF NOT EXISTS idx_keywords_opportunity_score ON keywords(opportunity_score DESC);

CREATE INDEX IF NOT EXISTS idx_keyword_search_history_user ON keyword_search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_keyword_search_history_created_at ON keyword_search_history(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_generated_titles_keyword ON generated_titles(keyword_id);
CREATE INDEX IF NOT EXISTS idx_generated_titles_created_by ON generated_titles(created_by);

CREATE INDEX IF NOT EXISTS idx_generated_content_title ON generated_content(title_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_created_by ON generated_content(created_by);

CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_time ON scheduled_posts(scheduled_time);

CREATE INDEX IF NOT EXISTS idx_seo_analytics_user ON seo_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_seo_analytics_date ON seo_analytics(date_recorded DESC);

-- Insert default countries
INSERT INTO countries (code, name) VALUES 
('KR', '한국'),
('US', '미국'),
('JP', '일본'),
('CN', '중국'),
('GB', '영국'),
('DE', '독일'),
('FR', '프랑스'),
('CA', '캐나다'),
('AU', '호주'),
('IN', '인도')
ON CONFLICT (code) DO NOTHING;