# Meta Leads Dashboard - Complete Setup

## 📖 Documentation Index

Start here based on your needs:

### 🚀 **I want to get started NOW**
→ Read: [QUICK_START.md](QUICK_START.md)
- 5-minute setup guide
- Visual diagrams
- Daily workflow
- Testing steps

### 📚 **I want full technical details**
→ Read: [README.md](README.md)
- Complete API documentation
- Architecture overview
- Troubleshooting guide
- Production deployment

### ✅ **What was actually implemented?**
→ Read: [SETUP_SUMMARY.md](SETUP_SUMMARY.md)
- What changed from original
- File-by-file breakdown
- Feature list
- Important notes

### 🔧 **Setup Scripts**

**Automatic Setup (Recommended)**
```bash
python quickstart.py
```
Wizard walks you through everything.

**Manual Start**
```bash
python backend\app.py
```
Then open `meta dashboard.html` in browser.

**One-Click Start (Windows)**
```bash
start.bat
```

### ✔️ **Verify Everything Works**
```bash
python verify.py
```
Checks all components are configured correctly.

---

## 🗂️ Project Structure

```
Auto dashboard/
│
├── 📱 Frontend (HTML/JS/Tailwind)
│   ├── Auto dashboard.html         (Auto insurance - unchanged)
│   ├── meta dashboard.html         (Lead management - UPDATED)
│   └── property.html               (Property insurance - unchanged)
│
├── 🐍 Backend (Python Flask)
│   ├── backend/app.py              (REST API server)
│   └── backend/requirements.txt     (Dependencies)
│
├── 🗄️ Database (Supabase PostgreSQL)
│   └── supabase_schema.sql         (SQL to create tables)
│
├── ⚙️ Configuration
│   ├── .env.local                  (Your secrets - keep private)
│   ├── .env.example                (Template for sharing)
│   └── .gitignore                  (Git protection)
│
├── 🚀 Startup
│   ├── start.bat                   (Windows one-click start)
│   ├── quickstart.py               (Setup wizard)
│   └── verify.py                   (Health check)
│
└── 📖 Documentation
    ├── README.md                   (Full guide)
    ├── QUICK_START.md              (5-min setup)
    ├── SETUP_SUMMARY.md            (What changed)
    └── INDEX.md                    (This file)
```

---

## 🔌 What's Connected

### Frontend → Backend
```javascript
// All dashboard operations now call backend
fetch('http://localhost:5000/api/leads')
fetch('http://localhost:5000/api/leads/create', {POST})
fetch('http://localhost:5000/api/leads/{id}/sync-event', {POST})
```

### Backend → Meta APIs
```python
# Meta Lead Form API - fetch leads
requests.get('https://graph.instagram.com/v18.0/{FORM_ID}/leads')

# Meta Conversions API - send events
requests.post('https://graph.instagram.com/v18.0/{PIXEL_ID}/events')

# Webhook - receive real-time leads
POST /webhook (from Meta)
```

### Backend → Supabase
```python
# Store/retrieve leads
supabase.table('leads').select('*').execute()
supabase.table('leads').insert(lead_data).execute()
```

---

## 📊 Key Features

✅ **Real Lead Collection**
- Facebook Lead Form integration
- Automatic sync on demand
- Webhook support for real-time updates
- Manual lead creation

✅ **Lead Management**  
- Search and filter
- Status tracking
- Bulk operations
- Reminders and follow-ups
- Google Contacts export

✅ **Meta Event Tracking**
- Send qualified leads to Meta Conversions API
- Track sync history
- Signal control (qualified/not qualified)
- Timestamp all events

✅ **Database Backend**
- Supabase PostgreSQL
- Full audit trail
- Real-time updates
- JSON metadata support

✅ **No UI Changes**
- Same beautiful design
- Same user experience
- Just with real data!

---

## 🎯 Your Credentials Are Already Set Up

All Meta API credentials in `.env.local`:

```env
META_APP_ID=1374336741109403
META_PAGE_ID=775140625692611
META_LEAD_FORM_ID=1395244698621351
FB_PIXEL_ID=2251357192000496
META_WEBHOOK_VERIFY_TOKEN=insurance_dashboard_webhook
```

Supabase credentials included (read-only access for frontend).

---

## 🚦 Quick Start Checklist

- [ ] Read QUICK_START.md (2 min)
- [ ] Run supabase_schema.sql (1 min)
- [ ] Install Python packages (2 min)
- [ ] Start backend: `python backend\app.py`
- [ ] Open `meta dashboard.html` in browser
- [ ] Click "Add Lead" to test
- [ ] Click "↻" to sync from Meta
- [ ] Done! ✅

---

## 📞 Common Tasks

### Start Everything
```bash
python backend\app.py
# Then open meta dashboard.html in browser
```

### Check If Working
```bash
python verify.py
```

### Set Up Database
1. Go to Supabase dashboard
2. SQL Editor → New Query
3. Paste `supabase_schema.sql`
4. Run

### Add New Feature
1. Add endpoint to `backend/app.py`
2. Call it from JavaScript in `meta dashboard.html`
3. Update database schema if needed

### Deploy to Production
See "Production Deployment" in [README.md](README.md)

---

## 🛡️ Security

- ✅ `.gitignore` protects `.env.local`
- ✅ Credentials not exposed in code
- ⚠️ Never share `.env.local` file
- ⚠️ Rotate Meta tokens every 60 days
- ⚠️ Use HTTPS in production

---

## 📈 Next Steps

1. **Customize** - Add your company branding
2. **Scale** - Deploy backend to production
3. **Optimize** - Monitor lead quality
4. **Integrate** - Connect to your CRM
5. **Automate** - Add lead scoring and routing

---

## 💡 Pro Tips

- Use `verify.py` before troubleshooting
- Check browser console (F12) for errors
- Backend logs show Meta API responses
- Webhook only works with public URL (use ngrok locally)
- Test leads show in dashboard within seconds

---

## 📚 Additional Resources

- [Meta Developers](https://developers.facebook.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Your Repository](.)

---

## ✨ You're Ready!

Everything is configured and ready to go:

1. ✅ Backend API built
2. ✅ Database schema ready
3. ✅ Frontend connected
4. ✅ Meta API integrated
5. ✅ Documentation complete

**Next: Read [QUICK_START.md](QUICK_START.md) and get started!**

---

**Last Updated:** January 16, 2026
**Status:** Production Ready ✅
**Version:** 1.0.0
