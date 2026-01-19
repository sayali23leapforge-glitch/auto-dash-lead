-- Supabase SQL Setup for Meta Leads Dashboard

-- Create leads table
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meta_lead_id VARCHAR(255) UNIQUE,
    meta_user_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    message TEXT,
    type VARCHAR(50) DEFAULT 'general', -- 'general', 'life', 'travel'
    status VARCHAR(50) DEFAULT 'New Lead',
    potential_status VARCHAR(50) DEFAULT 'qualified', -- 'qualified', 'not-qualified'
    notes TEXT,
    is_manual BOOLEAN DEFAULT FALSE,
    premium DECIMAL(10, 2) DEFAULT 0,
    renewal_date DATE,
    insurance_type VARCHAR(100),
    policy_term VARCHAR(50),
    visa_type VARCHAR(100),
    coverage DECIMAL(12, 2),
    trip_start DATE,
    trip_end DATE,
    last_sync TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    sync_signal VARCHAR(20) DEFAULT 'green', -- 'green', 'red'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    meta_data JSONB
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_type ON leads(type);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_meta_lead_id ON leads(meta_lead_id);

-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    reminder_time TIMESTAMP NOT NULL,
    reminder_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for reminders
CREATE INDEX IF NOT EXISTS idx_reminders_lead_id ON reminders(lead_id);
CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time);

-- Create sync_events table for tracking Meta syncs
CREATE TABLE IF NOT EXISTS sync_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    event_type VARCHAR(50), -- 'Lead', 'Purchase', etc
    meta_response JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for sync events
CREATE INDEX IF NOT EXISTS idx_sync_events_lead_id ON sync_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_sync_events_created_at ON sync_events(created_at DESC);

-- Enable realtime for leads table (optional, for live updates)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_publication_tables WHERE pubname = 'supabase_realtime' AND tablename = 'leads') THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE leads;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_publication_tables WHERE pubname = 'supabase_realtime' AND tablename = 'reminders') THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE reminders;
    END IF;
END $$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update updated_at
DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) - Optional, adjust based on your auth setup
-- ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sync_events ENABLE ROW LEVEL SECURITY;
