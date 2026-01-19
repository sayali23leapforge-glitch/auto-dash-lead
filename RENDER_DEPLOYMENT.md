# 🚀 Render Deployment Guide

## ✅ Project Successfully Pushed to GitHub
Repository: https://github.com/sayali23leapforge-glitch/auto-dash-lead

---

## 📋 Deploy to Render

### Step 1: Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select repository: `sayali23leapforge-glitch/auto-dash-lead`

### Step 2: Configure Service

**Basic Settings:**
- **Name**: `auto-dash-lead`
- **Environment**: `Python 3`
- **Branch**: `master`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app`

**Environment Variables** (Add these in Render dashboard):

```env
VITE_SUPABASE_URL=https://iollfvjduazbmccxtsdn.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlvbGxmdmpkdWF6Ym1jY3h0c2RuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NTIzNzEsImV4cCI6MjA4NDEyODM3MX0.d_k31U0zY5bMWx_fTlJGLD4AjVU-FAu6Xkk7AOnpTUk
VITE_SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlvbGxmdmpkdWF6Ym1jY3h0c2RuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODU1MjM3MSwiZXhwIjoyMDg0MTI4MzcxfQ.puSyqxog5TbgnXjVjnrvyoOX0plsDD2YuJovNoQlmj8

META_APP_ID=1374336741109403
META_APP_SECRET=ca57447d436108c0452657bb084f8632
META_PAGE_ID=775140625692611
META_PAGE_ACCESS_TOKEN=EAATh87VBbpsBQaMowxa6R0cFGbPefZAynMuGtLTzHi1ZAMxJSMkegB19BsvAn3CIDU5SE56kIFGIxnXvwGSrFu6i3cdqWhg29xCiLXeY7qde97FVd9hTwZC4JBBbYq8gy3DcNNvqep9d7wKZALfNv1dLDZC0CPTgoGntWM6Lj3ApieOdYsGdNrZAz0phnDn88k
META_LEAD_FORM_ID=1395244698621351
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
FB_PIXEL_ID=2251357192000496
FB_PIXEL_TOKEN=EAAlfVZB2VnDsBQah1hA3ZBFLM9fZAeQpI4KuEM1lmjX436BCzxGZAHHyAjjeUDv2jsr2bKvACPD5ElkZAKIhqBqkv0QXbWz1WORbItTtbZBZAixHC5wZAO4rh8y09HL7Nr2w5x2pZCDZCZBuOeyJQ9idAqooMogxqroZCR0KTOJJmB1QBCR0xC0JcSzAnT4SptsiqQZDZD

FLASK_PORT=5000
FLASK_ENV=production
PYTHON_VERSION=3.11.0
```

### Step 3: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (~5-10 minutes)
3. Your app will be live at: `https://auto-dash-lead.onrender.com`

---

## 🔧 Post-Deployment Updates

### Update Frontend URLs

After deployment, update the API URLs in your HTML files:

**In `Auto dashboard.html`, `meta dashboard.html`, `property.html`:**

Replace all instances of:
```javascript
http://localhost:5000
```

With your Render URL:
```javascript
https://auto-dash-lead.onrender.com
```

**Quick Find & Replace:**
- Search: `http://localhost:5000`
- Replace: `https://auto-dash-lead.onrender.com`

Then commit and push:
```bash
git add -A
git commit -m "Update API URLs for production"
git push origin master
```

Render will auto-deploy the changes!

---

## ✅ Verify Deployment

### Test Endpoints:

1. **Backend Health Check**: `https://auto-dash-lead.onrender.com/`
2. **Leads API**: `https://auto-dash-lead.onrender.com/api/leads`
3. **Meta Dashboard**: `https://auto-dash-lead.onrender.com/meta%20dashboard.html`
4. **Auto Dashboard**: `https://auto-dash-lead.onrender.com/Auto%20dashboard.html`
5. **Property**: `https://auto-dash-lead.onrender.com/property.html`

### Test Lead Sync:

1. Go to Meta Dashboard
2. Should automatically load leads from Supabase
3. Click "Process" on a lead → Should open Auto Dashboard with params
4. Upload DASH/MVR PDFs → Should parse correctly
5. Click "Save Client Data" → Should save to Supabase
6. Check Property button → Should navigate to property page

---

## 📊 Database Setup

Run this SQL in Supabase SQL Editor:

```sql
-- Clients table (already created)
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    drivers JSONB NOT NULL
);

-- Properties table
CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    customer JSONB NOT NULL,
    properties JSONB NOT NULL,
    view_mode TEXT,
    blank_tenant JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_clients_updated ON clients (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_updated ON properties (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_customer_name ON properties ((customer->>'name'));
```

---

## 🎯 Features Deployed

✅ **Meta Leads Dashboard**
- Automatic lead sync from Facebook
- Lead filtering and search
- Process leads to Auto Dashboard

✅ **Auto Dashboard**
- URL parameter handling from Meta Dashboard
- DASH PDF parsing (driver info, vehicle, claims, policies)
- MVR PDF parsing (license, convictions, demerit points)
- Lead search with autocomplete
- Gap calculation
- License experience calculation (G/G2/G1)
- Complete data save to Supabase

✅ **Property Module**
- Homeowners and Tenants quotes
- Multiple properties support
- Complete property data collection
- Save to Supabase

✅ **Backend API**
- Lead management (CRUD)
- PDF parsing (DASH & MVR)
- Client data save
- Property data save
- Meta webhook for live lead sync

---

## 🔐 Security Notes

- ✅ `.env.local` and `.env.production` excluded from git
- ✅ All sensitive keys stored in Render environment variables
- ✅ CORS configured for production
- ✅ Supabase RLS enabled (configure policies as needed)

---

## 📞 Support

If deployment fails:
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify all environment variables are set
3. Ensure Supabase tables exist
4. Check that Python version matches (3.11)

**Common Issues:**
- "Module not found" → Check `requirements.txt`
- "Port already in use" → Render auto-assigns port via `$PORT`
- "Database connection failed" → Verify Supabase credentials
- "CORS error" → Update frontend URLs to production domain
