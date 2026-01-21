-- Add to Supabase: Store Auto Dashboard Data linked to Leads

-- Create clients_data table to store all auto dashboard information
CREATE TABLE IF NOT EXISTS clients_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    email VARCHAR(255),
    
    -- Driver Information
    drivers JSONB,
    
    -- Created and updated timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_clients_data_lead_id ON clients_data(lead_id);
CREATE INDEX IF NOT EXISTS idx_clients_data_email ON clients_data(email);
CREATE INDEX IF NOT EXISTS idx_clients_data_updated_at ON clients_data(updated_at DESC);

-- Create properties_data table to store all property information
CREATE TABLE IF NOT EXISTS properties_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    email VARCHAR(255),
    
    -- Property Information
    properties JSONB,
    
    -- Created and updated timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for properties
CREATE INDEX IF NOT EXISTS idx_properties_data_lead_id ON properties_data(lead_id);
CREATE INDEX IF NOT EXISTS idx_properties_data_email ON properties_data(email);
CREATE INDEX IF NOT EXISTS idx_properties_data_updated_at ON properties_data(updated_at DESC);

-- Create trigger for clients_data updated_at
DROP TRIGGER IF EXISTS update_clients_data_updated_at ON clients_data;
CREATE TRIGGER update_clients_data_updated_at BEFORE UPDATE ON clients_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for properties_data updated_at
DROP TRIGGER IF EXISTS update_properties_data_updated_at ON properties_data;
CREATE TRIGGER update_properties_data_updated_at BEFORE UPDATE ON properties_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
