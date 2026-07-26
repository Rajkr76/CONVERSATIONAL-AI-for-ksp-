-- ═══════════════════════════════════════════════════════════════════
-- KSP Crime Intelligence Platform — Database Schema
-- PostgreSQL 16 + PostGIS
-- ═══════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Users (Authentication) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username        VARCHAR(100) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'officer'
                    CHECK (role IN ('admin', 'officer', 'analyst', 'viewer')),
    badge_number    VARCHAR(50),
    department      VARCHAR(200),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- ─── Officers ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS officer (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(200) NOT NULL,
    badge_number    VARCHAR(50) UNIQUE NOT NULL,
    rank            VARCHAR(100) NOT NULL,
    department      VARCHAR(200) NOT NULL,
    station         VARCHAR(200) NOT NULL,
    phone           VARCHAR(20),
    email           VARCHAR(255),
    date_of_joining DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_officer_badge ON officer(badge_number);
CREATE INDEX idx_officer_station ON officer(station);
CREATE INDEX idx_officer_rank ON officer(rank);

-- ─── FIR (First Information Report) ─────────────────────────────
CREATE TABLE IF NOT EXISTS fir (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_number      VARCHAR(50) UNIQUE NOT NULL,
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    fir_date        DATE NOT NULL,
    fir_type        VARCHAR(100) NOT NULL
                    CHECK (fir_type IN (
                        'theft', 'robbery', 'murder', 'assault',
                        'fraud', 'cybercrime', 'kidnapping', 'drug_offense',
                        'domestic_violence', 'missing_person', 'accident',
                        'property_dispute', 'sexual_offense', 'other'
                    )),
    status          VARCHAR(50) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'under_investigation', 'chargesheet_filed', 'closed', 'reopened')),
    severity        VARCHAR(20) NOT NULL DEFAULT 'medium'
                    CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    ipc_sections    TEXT[],
    station         VARCHAR(200) NOT NULL,
    district        VARCHAR(200) NOT NULL,
    state           VARCHAR(100) DEFAULT 'Karnataka',
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    location_point  GEOGRAPHY(Point, 4326),
    reporting_officer_id UUID REFERENCES officer(id) ON DELETE SET NULL,
    investigating_officer_id UUID REFERENCES officer(id) ON DELETE SET NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_fir_number ON fir(fir_number);
CREATE INDEX idx_fir_date ON fir(fir_date);
CREATE INDEX idx_fir_type ON fir(fir_type);
CREATE INDEX idx_fir_status ON fir(status);
CREATE INDEX idx_fir_severity ON fir(severity);
CREATE INDEX idx_fir_station ON fir(station);
CREATE INDEX idx_fir_district ON fir(district);
CREATE INDEX idx_fir_location ON fir USING GIST(location_point);

-- ─── Accused ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS accused (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    alias           VARCHAR(200),
    age             INTEGER CHECK (age > 0 AND age < 150),
    gender          VARCHAR(20) CHECK (gender IN ('male', 'female', 'other')),
    address         TEXT,
    phone           VARCHAR(20),
    id_type         VARCHAR(50),
    id_number       VARCHAR(100),
    occupation      VARCHAR(200),
    is_arrested     BOOLEAN DEFAULT FALSE,
    arrest_date     DATE,
    bail_status     VARCHAR(50) DEFAULT 'not_applicable'
                    CHECK (bail_status IN ('not_applicable', 'bail_granted', 'bail_denied', 'bail_pending')),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_accused_fir ON accused(fir_id);
CREATE INDEX idx_accused_name ON accused(name);
CREATE INDEX idx_accused_arrested ON accused(is_arrested);

-- ─── Victim ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS victim (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    age             INTEGER CHECK (age > 0 AND age < 150),
    gender          VARCHAR(20) CHECK (gender IN ('male', 'female', 'other')),
    address         TEXT,
    phone           VARCHAR(20),
    injury_type     VARCHAR(100),
    injury_severity VARCHAR(50)
                    CHECK (injury_severity IN ('none', 'minor', 'moderate', 'severe', 'fatal')),
    hospital_name   VARCHAR(200),
    is_minor        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_victim_fir ON victim(fir_id);
CREATE INDEX idx_victim_name ON victim(name);

-- ─── Investigation ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS investigation (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    officer_id      UUID NOT NULL REFERENCES officer(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    findings        TEXT,
    status          VARCHAR(50) NOT NULL DEFAULT 'in_progress'
                    CHECK (status IN ('in_progress', 'completed', 'pending_review', 'on_hold')),
    started_at      DATE NOT NULL,
    completed_at    DATE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_investigation_fir ON investigation(fir_id);
CREATE INDEX idx_investigation_officer ON investigation(officer_id);
CREATE INDEX idx_investigation_status ON investigation(status);

-- ─── Evidence ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evidence (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    evidence_type   VARCHAR(100) NOT NULL
                    CHECK (evidence_type IN (
                        'physical', 'digital', 'documentary', 'testimonial',
                        'forensic', 'photographic', 'video', 'audio', 'other'
                    )),
    description     TEXT NOT NULL,
    collected_by    UUID REFERENCES officer(id) ON DELETE SET NULL,
    collected_at    TIMESTAMP WITH TIME ZONE,
    storage_location VARCHAR(200),
    chain_of_custody TEXT,
    is_verified     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evidence_fir ON evidence(fir_id);
CREATE INDEX idx_evidence_type ON evidence(evidence_type);

-- ─── Witness ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS witness (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    age             INTEGER CHECK (age > 0 AND age < 150),
    gender          VARCHAR(20) CHECK (gender IN ('male', 'female', 'other')),
    address         TEXT,
    phone           VARCHAR(20),
    statement       TEXT,
    statement_date  DATE,
    is_reliable     BOOLEAN DEFAULT TRUE,
    protection_needed BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_witness_fir ON witness(fir_id);

-- ─── Criminal History ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS criminal_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    accused_id      UUID NOT NULL REFERENCES accused(id) ON DELETE CASCADE,
    offense_type    VARCHAR(100) NOT NULL,
    case_number     VARCHAR(50),
    court_name      VARCHAR(200),
    conviction_date DATE,
    sentence        VARCHAR(200),
    status          VARCHAR(50) DEFAULT 'recorded'
                    CHECK (status IN ('recorded', 'convicted', 'acquitted', 'pending')),
    remarks         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_criminal_history_accused ON criminal_history(accused_id);
CREATE INDEX idx_criminal_history_offense ON criminal_history(offense_type);

-- ─── Financial Transaction ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS financial_transaction (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fir_id          UUID NOT NULL REFERENCES fir(id) ON DELETE CASCADE,
    accused_id      UUID REFERENCES accused(id) ON DELETE SET NULL,
    transaction_type VARCHAR(50) NOT NULL
                    CHECK (transaction_type IN ('credit', 'debit', 'transfer', 'cash_deposit', 'cash_withdrawal')),
    amount          DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    currency        VARCHAR(10) DEFAULT 'INR',
    from_account    VARCHAR(100),
    to_account      VARCHAR(100),
    bank_name       VARCHAR(200),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_suspicious   BOOLEAN DEFAULT FALSE,
    remarks         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_financial_fir ON financial_transaction(fir_id);
CREATE INDEX idx_financial_accused ON financial_transaction(accused_id);
CREATE INDEX idx_financial_suspicious ON financial_transaction(is_suspicious);
CREATE INDEX idx_financial_date ON financial_transaction(transaction_date);

-- ─── Location History ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS location_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    accused_id      UUID REFERENCES accused(id) ON DELETE CASCADE,
    fir_id          UUID REFERENCES fir(id) ON DELETE SET NULL,
    location_name   VARCHAR(200) NOT NULL,
    address         TEXT,
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    location_point  GEOGRAPHY(Point, 4326),
    recorded_at     TIMESTAMP WITH TIME ZONE NOT NULL,
    source          VARCHAR(100)
                    CHECK (source IN ('cell_tower', 'cctv', 'gps', 'witness', 'manual', 'other')),
    remarks         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_location_accused ON location_history(accused_id);
CREATE INDEX idx_location_fir ON location_history(fir_id);
CREATE INDEX idx_location_point ON location_history USING GIST(location_point);
CREATE INDEX idx_location_recorded ON location_history(recorded_at);

-- ─── Chat History ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    sql_query       TEXT,
    sql_result      JSONB,
    chart_data      JSONB,
    graph_data      JSONB,
    confidence      DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    language        VARCHAR(10) DEFAULT 'en',
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_conversation ON chat_history(conversation_id);
CREATE INDEX idx_chat_user ON chat_history(user_id);
CREATE INDEX idx_chat_created ON chat_history(created_at);
