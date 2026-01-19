# Quick Start Visual Guide

## What You Have Now

### ✅ Real-time Lead Pipeline
```
Facebook Lead Form
      ↓
  (User fills form on Meta Ads)
      ↓
Meta Lead API / Webhook
      ↓
Python Backend (Flask on localhost:5000)
      ↓
Supabase Database
      ↓
Meta Dashboard (your HTML)
      ↓
(You review & sync leads back to Meta)
```

### ✅ Key Files Created/Modified

**Backend (Python)**
- `backend/app.py` - Flask API server
- `backend/requirements.txt` - Python dependencies

**Frontend (Already Updated)**
- `meta dashboard.html` - Now connects to real backend
- Removed dummy MOCK_DATA
- Added real data loading

**Configuration**
- `.env.local` - Your credentials (keep private!)
- `supabase_schema.sql` - Database tables

**Documentation**
- `README.md` - Full technical guide
- `SETUP_SUMMARY.md` - What was implemented
- `start.bat` - One-click startup (Windows)
- `quickstart.py` - Setup wizard
- `verify.py` - System health check

---

## 🚀 First Time Setup (5 minutes)

### Step 1: Create Database Tables
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click your project
3. Go to **SQL Editor**
4. Click **New Query**
5. Copy-paste contents from `supabase_schema.sql`
6. Click **Run**

**You'll have:**
- `leads` table - stores all leads
- `reminders` table - follow-up reminders
- `sync_events` table - Meta sync history

### Step 2: Install Dependencies
```bash
# Open PowerShell in Auto dashboard folder

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r backend\requirements.txt
```

### Step 3: Start Backend
```bash
python backend\app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 4: Open Dashboard
1. Open `meta dashboard.html` in browser
2. You should see a loading state
3. Once backend connects, table will populate with leads (if any exist in Supabase)

---

## 📊 How to Test

### Test 1: Manual Lead Creation
1. Click **Add Lead** button (blue + icon)
2. Fill in: Name, Phone, Email
3. Click **Next: Policy Details**
4. Click **Save & Continue**
5. Lead should appear in table immediately

### Test 2: Sync with Meta
1. Click **↻** refresh button (top right)
2. Backend will fetch latest leads from Meta API
3. New leads appear in table
4. Check console (F12) for status

### Test 3: Send to Meta Event Manager
1. Click **Sync** button on any lead (right side of row)
2. Button shows spinner
3. Should show ✓ Sent
4. Timestamp updates
5. Event sent to Meta Conversions API

### Test 4: Verify Backend
```bash
# In PowerShell, while backend is running:
curl http://localhost:5000/api/health
# Should return: {"status": "ok", "service": "Meta Lead Dashboard Backend"}
```

---

## 🔄 Daily Workflow

### Morning
```
1. Open meta dashboard.html
2. Click ↻ to sync overnight leads from Meta
3. Review new leads in table
4. Update status as needed
```

### During Day
```
1. New leads appear automatically (via webhook)
2. Review each lead
3. Click "Sync" to qualify lead to Meta
4. Track in reminder/follow-up
```

### End of Day
```
1. Update lead statuses
2. Check analytics/stats (top of page)
3. Plan follow-ups for tomorrow
```

---

## 📲 Meta API Integration Points

### What's Connected

✅ **Facebook Lead Form**
- Your form: [Live Form](https://www.facebook.com/775140625692611/leads_center)
- Form ID: `1395244698621351`
- Auto-fetches leads on sync

✅ **Webhook (Real-time)**
- Endpoint: `http://localhost:5000/webhook`
- Receives: New leads instantly
- Requires: Public URL (for production)

✅ **Conversions API (Event Manager)**
- Sends: "Lead" events back to Meta
- Used for: Campaign optimization
- Tracks: Lead conversion back to Meta

✅ **Meta Pixel**
- Pixel ID: `2251357192000496`
- Tracks: User interactions
- Used for: Retargeting

---

## 🛠️ Troubleshooting

### "Backend not running"
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# If in use, kill it:
taskkill /PID [PID] /F

# Or change port in .env.local:
FLASK_PORT=5001
```

### "Leads not loading"
1. **Check backend:** `python backend/app.py` running?
2. **Check console:** F12 → Console tab for errors
3. **Check database:** Table exists in Supabase?
4. **Check credentials:** Correct URL & keys in .env.local?

### "Sync button not working"
1. Check backend logs for errors
2. Verify Meta token is valid
3. Verify Lead Form ID is correct
4. Check network tab (F12) for request status

### "Webhook not receiving leads"
For localhost testing:
- Use [ngrok](https://ngrok.com/) to expose local server
- Update webhook URL in Meta App settings
- Webhook only works with public HTTPS URL

---

## 📈 Key Metrics (Top of Dashboard)

- **New Leads**: Leads added today
- **Contacted**: Leads you've called/emailed
- **Quotes Sent**: Follow-up quotes sent
- **Closed Won**: Completed sales
- **Premium Sold**: Total revenue

Updates automatically as you change statuses!

---

## 🔐 Security Notes

### Keep Private ⚠️
- `.env.local` file (API keys)
- Meta access tokens
- Supabase service role key

### Already Protected ✅
- `.gitignore` excludes `.env.local`
- `.env.example` shows template only
- Never commit real credentials

### For Production
1. Use environment variables (not .env files)
2. Rotate tokens regularly
3. Use HTTPS for all endpoints
4. Implement proper authentication
5. Use RLS (Row Level Security) in Supabase

---

## 🎯 Next Features to Add

1. **Lead Scoring** - Auto-rate lead quality
2. **Auto-assignment** - Route to team members
3. **CRM Integration** - Sync with Salesforce/HubSpot
4. **Analytics Dashboard** - Charts and graphs
5. **Email Integration** - Auto-send follow-ups
6. **SMS Notifications** - Text alerts for new leads

---

## 📞 Support Resources

- **Meta API Docs:** https://developers.facebook.com/docs/
- **Supabase Docs:** https://supabase.com/docs
- **Flask Docs:** https://flask.palletsprojects.com/
- **Your Project:** See `README.md` for details

---

## ✨ You're All Set!

Your Meta Leads Dashboard is:
- ✅ Connected to real Facebook leads
- ✅ Backed by Supabase database
- ✅ Integrated with Meta Conversions API
- ✅ Ready for production

**Start:** `python backend/app.py` + Open `meta dashboard.html`

---

Last Updated: January 16, 2026
