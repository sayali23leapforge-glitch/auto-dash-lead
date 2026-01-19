# Meta Leads Dashboard - Setup Guide

## Overview
Real-time lead management dashboard that integrates with:
- **Facebook Lead Form API** - Automatic lead collection from Meta ads
- **Supabase** - Cloud database for lead storage
- **Python Flask** - Backend API for Meta integration and event management
- **Conversions API** - Send qualified lead events back to Meta

## Prerequisites
- Python 3.8+
- Node.js (for frontend development, optional)
- Supabase account (free tier available)
- Meta Business Account with API access

## Setup Steps

### 1. Database Setup (Supabase)

Go to your Supabase dashboard and:
1. Create a new project or use existing
2. Navigate to **SQL Editor**
3. Create a new query and paste contents of `supabase_schema.sql`
4. Execute the query to create tables

**Tables created:**
- `leads` - Main leads table
- `reminders` - Follow-up reminders
- `sync_events` - Track Meta API syncs

### 2. Environment Variables

The `.env.local` file has been pre-configured with your Meta API credentials:

```env
# Supabase
VITE_SUPABASE_URL=https://iollfvjduazbmcccxtsdn.supabase.co
VITE_SUPABASE_ANON_KEY=...
VITE_SUPABASE_SERVICE_ROLE_KEY=...

# Meta API
META_APP_ID=1374336741109403
META_APP_SECRET=ca57447d436108c0452657bb084f8632
META_PAGE_ID=775140625692611
META_PAGE_ACCESS_TOKEN=EAATh87VBbpsBQaMowxa6R0cFGbPefZAynMuGtLTzHi1ZAMxJSMkegB19BsvAn3CIDU5SE56kIFGIxnXvwGSrFu6i3cdqWhg29xCiLXeY7qde97FVd9hTwZC4JBBbYq8gy3DcNNvqep9d7wKZALfNv1dLDZC0CPTgoGntWM6Lj3ApieOdYsGdNrZAz0phnDn88k
META_LEAD_FORM_ID=1395244698621351
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
FB_PIXEL_ID=2251357192000496
FB_PIXEL_TOKEN=...

# Backend
FLASK_PORT=5000
FLASK_ENV=development
```

### 3. Install Dependencies

```bash
cd "d:\Auto dashboard"
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
```

### 4. Start the Backend Server

**Option A - Automatic (Windows):**
```bash
start.bat
```

**Option B - Manual:**
```bash
python backend\app.py
```

The server will start on `http://localhost:5000`

### 5. Open the Dashboard

1. Navigate to `d:\Auto dashboard\meta dashboard.html`
2. Open in browser (or use Live Server in VS Code)
3. Backend will automatically load real leads from Meta on page load

## API Endpoints

### Get Leads
```
GET /api/leads?type=general&status=New Lead
Returns: { data: [...], count: N }
```

### Sync Leads from Meta
```
POST /api/leads/sync
Returns: { success: true, message: "...", leads: [...] }
```

### Create Manual Lead
```
POST /api/leads/create
Body: { name, phone, email, type, notes }
Returns: { success: true, data: {...} }
```

### Update Lead
```
PUT /api/leads/{id}
Body: { status, notes, ... }
Returns: { success: true, data: {...} }
```

### Delete Lead
```
DELETE /api/leads/{id}
Returns: { success: true, message: "..." }
```

### Send Lead Event to Meta
```
POST /api/leads/{id}/sync-event
Body: { event_type: "Lead" }
Returns: { success: true, message: "..." }
```

### Webhook (Incoming Leads)
```
POST /webhook
GET /webhook?hub.challenge=...&hub.verify_token=...
```

## Features

✅ **Real-time Lead Collection**
- Automatic sync from Meta Lead Forms
- Webhook support for instant updates
- Manual lead creation

✅ **Lead Management**
- Search and filter by status/type
- Bulk actions (delete, mark contacted)
- Set reminders for follow-ups
- Save to Google Contacts

✅ **Meta Integration**
- Send qualified leads to Meta Conversions API
- Track sync history
- Signal control (green/red)
- Event timestamp tracking

✅ **Database**
- All leads stored in Supabase
- Full CRUD operations
- Timestamps and audit trails
- JSON metadata support

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r backend\requirements.txt
```

### Leads not loading
1. Check browser console for errors (F12)
2. Verify `FLASK_PORT=5000` in .env.local
3. Ensure Flask server is running on localhost:5000
4. Check CORS is enabled in backend/app.py

### Supabase connection error
1. Verify credentials in .env.local are correct
2. Check Supabase project is active
3. Ensure `leads` table exists (run supabase_schema.sql)

### Meta API errors
1. Check access token hasn't expired (usually 60 days)
2. Verify Lead Form ID is correct
3. Ensure webhook URL is accessible (use ngrok for local testing)

## Next Steps

1. **Configure Webhook URL:**
   - Go to Meta App Settings → Webhooks
   - Set callback URL to your server's `/webhook` endpoint
   - Verify token: `insurance_dashboard_webhook`

2. **Test Lead Flow:**
   - Submit a test lead through Meta Lead Form
   - Check if it appears in dashboard (may take a few seconds)
   - Click "Sync" button to manually pull latest leads

3. **Customize Calculations:**
   - Edit calculator fields in modal for different insurance types
   - Add new fields as needed (life insurance coverage, travel dates, etc)

4. **Production Deployment:**
   - Use proper domain (not localhost)
   - Switch to production Supabase project
   - Implement proper authentication
   - Use environment-specific config files

## Architecture

```
┌─────────────────────┐
│  Meta Dashboard     │
│  (HTML/JS/Tailwind) │
└──────────┬──────────┘
           │ (HTTP/JSON)
           ▼
┌─────────────────────┐
│  Flask Backend      │ ◄─── Meta API
│  (Python)           │      - Leads
│                     │      - Events
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Supabase           │
│  (PostgreSQL)       │
│  - leads            │
│  - reminders        │
│  - sync_events      │
└─────────────────────┘
```

## Support

For issues with:
- **Meta API**: https://developers.facebook.com/docs/
- **Supabase**: https://supabase.com/docs
- **Flask**: https://flask.palletsprojects.com

---

**Last Updated:** January 16, 2026
