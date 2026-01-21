"""
Meta/Facebook Lead Form Backend
Integrates with Facebook Lead API and Supabase
"""

import sys
import io

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
import hmac
import hashlib
# Import pdf_parser using package-relative import
from backend.pdf_parser import parse_mvr_pdf, parse_dash_pdf

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.local'))

# Configure Flask to serve static files from parent directory
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '..')
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CORS(app)

# ========== CONFIG ==========
META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')
META_PAGE_ID = os.getenv('META_PAGE_ID')
META_PAGE_ACCESS_TOKEN = os.getenv('META_PAGE_ACCESS_TOKEN')
META_LEAD_FORM_ID = os.getenv('META_LEAD_FORM_ID')
META_WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
FB_PIXEL_ID = os.getenv('FB_PIXEL_ID')

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SERVICE_ROLE_KEY')

# Debug: Print Supabase URL
print(f"🔗 Supabase URL: {SUPABASE_URL}")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Meta API Base URL
META_API_VERSION = 'v18.0'
META_BASE_URL = f'https://graph.facebook.com/{META_API_VERSION}'

# ========== HELPER FUNCTIONS ==========

def verify_meta_webhook(data, hub_signature):
    """Verify webhook signature from Meta"""
    hash_obj = hmac.new(
        META_APP_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    )
    expected_signature = f'sha256={hash_obj.hexdigest()}'
    return hmac.compare_digest(expected_signature, hub_signature)


def get_leads_from_meta():
    """Fetch all leads from Meta Lead Form API with pagination (up to 500 leads)"""
    try:
        all_leads = []
        url = f'{META_BASE_URL}/{META_LEAD_FORM_ID}/leads'
        
        # Try to get leads from Jan 12, 2026 onwards
        from datetime import datetime, timezone
        jan_12_timestamp = int(datetime(2026, 1, 12, 0, 0, 0, tzinfo=timezone.utc).timestamp())
        
        params = {
            'fields': 'id,created_time,field_data,adgroup_id',
            'access_token': META_PAGE_ACCESS_TOKEN,
            'limit': 500,  # Request max leads
            'filtering': f'[{{"field":"time_created","operator":"GREATER_THAN","value":{jan_12_timestamp}}}]'
        }
        
        print(f"📞 Fetching leads from Meta API since Jan 12, 2026: {url}")
        print(f"🔑 Using Lead Form ID: {META_LEAD_FORM_ID}")
        print(f"📅 Filtering from timestamp: {jan_12_timestamp}")
        
        # Fetch first page
        response = requests.get(url, params=params)
        print(f"📡 Meta API Response Status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        all_leads.extend(data.get('data', []))
        print(f"📄 Page 1: {len(data.get('data', []))} leads")
        
        # Continue fetching all pages (max 500 total to avoid overwhelming)
        page_count = 1
        while 'paging' in data and 'next' in data['paging'] and len(all_leads) < 500:
            page_count += 1
            next_url = data['paging']['next']
            print(f"📄 Fetching page {page_count}... (Total so far: {len(all_leads)})")
            response = requests.get(next_url)
            response.raise_for_status()
            data = response.json()
            page_leads = data.get('data', [])
            all_leads.extend(page_leads)
            print(f"   + {len(page_leads)} leads")
            
            # Safety limit
            if page_count > 10:
                print(f"⚠️ Reached page limit (10 pages)")
                break
        
        print(f"✅ Found {len(all_leads)} total leads from Meta")
        return all_leads
    
    except Exception as e:
        print(f"❌ Error fetching leads from Meta: {str(e)}")
        if hasattr(e, 'response'):
            print(f"❌ Meta API Error Response: {e.response.text if e.response else 'No response'}")
        return []


def parse_meta_lead(meta_lead):
    """Parse Meta lead data into standardized format"""
    field_data = meta_lead.get('field_data', [])
    lead_dict = {}
    
    # Facebook returns field_data with "values" as an array
    for field in field_data:
        field_name = field.get('name', '').lower()
        field_values = field.get('values', [])
        # Take the first value from the array
        lead_dict[field_name] = field_values[0] if field_values else ''
    
    meta_lead_id = meta_lead.get('id')
    
    return {
        # Don't set 'id' - let database auto-generate it
        'meta_lead_id': meta_lead_id,
        'name': lead_dict.get('full_name', lead_dict.get('name', 'Unknown')),
        'phone': lead_dict.get('phone_number', lead_dict.get('phone', '')),
        'email': lead_dict.get('email_address', lead_dict.get('email', '')),
        'message': lead_dict.get('message', ''),
        'created_at': meta_lead.get('created_time', datetime.utcnow().isoformat()),
        'meta_data': meta_lead,
        'is_manual': False,
        'status': 'New Lead',
        'type': 'Auto',
        'potential_status': 'Not Qualified',
        'premium': 0,
        'sync_status': 'Not Synced',
        'sync_signal': False,
        'notes': ''
        # Removed: company, address, city, state, country, zip_code - not in database schema
    }


def save_lead_to_supabase(lead_data):
    """Save lead to Supabase (skip if already exists)"""
    try:
        # Check if lead already exists by meta_lead_id (only for Facebook leads)
        if lead_data.get('meta_lead_id'):
            existing = supabase.table('leads').select('id').eq('meta_lead_id', lead_data.get('meta_lead_id')).execute()
            
            if existing.data:
                print(f"⏭️ Lead {lead_data.get('meta_lead_id')} already exists, skipping")
                return existing.data[0]
        
        # Insert new lead
        print(f"🔄 Attempting to save lead: {lead_data.get('name')}")
        response = supabase.table('leads').insert(lead_data).execute()
        print(f"💾 Saved lead: {lead_data.get('name')} (ID: {response.data[0].get('id') if response.data else 'N/A'})")
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error saving lead to Supabase: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_leads_from_db(filters=None):
    """Get leads from Supabase"""
    try:
        print(f"📋 Querying leads table with filters: {filters}")
        query = supabase.table('leads').select('*')
        
        if filters:
            if filters.get('type'):
                query = query.eq('type', filters['type'])
            if filters.get('status'):
                query = query.eq('status', filters['status'])
        
        # No limit - fetch ALL leads
        response = query.order('created_at', desc=True).execute()
        print(f"✅ Query returned {len(response.data)} leads")
        return response.data
    except Exception as e:
        print(f"❌ Error fetching leads from Supabase: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def send_event_to_meta(lead_id, event_type, event_data):
    """Send event to Meta Conversions API (Event Manager)"""
    try:
        url = f'{META_BASE_URL}/{FB_PIXEL_ID}/events'
        
        payload = {
            'data': [
                {
                    'event_name': event_type,  # 'Purchase', 'Lead', 'ViewContent', etc
                    'event_time': int(datetime.utcnow().timestamp()),
                    'user_data': {
                        'em': event_data.get('email', ''),  # hashed email
                        'ph': event_data.get('phone', ''),  # hashed phone
                        'fn': event_data.get('name', ''),   # hashed first name
                    },
                    'custom_data': {
                        'value': event_data.get('premium', 0),
                        'currency': 'USD'
                    },
                    'event_source_url': event_data.get('source_url', ''),
                    'action_source': 'website'
                }
            ],
            'access_token': META_PAGE_ACCESS_TOKEN
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"Error sending event to Meta: {str(e)}")
        return {'success': False, 'error': str(e)}


# ========== API ENDPOINTS ==========

@app.route('/')
def index():
    """Serve Meta Dashboard as home page"""
    return send_from_directory(app.static_folder, 'meta dashboard.html')

@app.route('/auto')
def auto_dashboard():
    """Serve Auto Dashboard"""
    return send_from_directory(app.static_folder, 'Auto dashboard.html')

@app.route('/property')
def property_dashboard():
    """Serve Property Dashboard"""
    return send_from_directory(app.static_folder, 'property.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Meta Lead Dashboard Backend'}), 200


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get leads from database for instant load"""
    try:
        filters = {}
        if request.args.get('type'):
            filters['type'] = request.args.get('type')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        print("📊 Loading leads from database (instant)...")
        leads = get_leads_from_db(filters)
        
        print(f"📤 Returning {len(leads)} leads from database")
        return jsonify({'data': leads, 'count': len(leads)}), 200
        
    except Exception as e:
        print(f"❌ Error loading leads from database: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/sync', methods=['POST'])
def sync_leads():
    """Fetch fresh leads from Facebook and save to database"""
    try:
        print("📞 Fetching fresh leads from Facebook API...")
        
        # Fetch from Facebook
        meta_leads = get_leads_from_meta()
        print(f"✅ Fetched {len(meta_leads)} leads from Facebook")
        
        # Parse and save
        new_leads = []
        for meta_lead in meta_leads:
            parsed_lead = parse_meta_lead(meta_lead)
            saved = save_lead_to_supabase(parsed_lead)
            if saved:
                new_leads.append(parsed_lead)
        
        print(f"💾 Saved {len(new_leads)} new leads to database")
        
        return jsonify({
            'success': True,
            'message': f'Synced {len(new_leads)} new leads from Facebook',
            'leads': new_leads,
            'count': len(new_leads)
        }), 200
        
    except Exception as e:
        print(f"❌ Error syncing from Facebook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/debug-meta', methods=['GET'])
def debug_meta_leads():
    """Debug endpoint to see raw Facebook API response"""
    try:
        meta_leads = get_leads_from_meta()
        # Get first 10 leads with their names
        debug_info = []
        for lead in meta_leads[:10]:
            parsed = parse_meta_lead(lead)
            debug_info.append({
                'id': lead.get('id'),
                'created_time': lead.get('created_time'),
                'name': parsed.get('name'),
                'email': parsed.get('email'),
                'phone': parsed.get('phone')
            })
        
        return jsonify({
            'success': True,
            'total_from_facebook': len(meta_leads),
            'first_10_leads': debug_info
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/test-save-one', methods=['POST'])
def test_save_one_lead():
    """Test saving one lead from Facebook"""
    try:
        meta_leads = get_leads_from_meta()
        if not meta_leads:
            return jsonify({'success': False, 'error': 'No leads from Facebook'}), 400
        
        # Try to save the first lead
        first_lead = meta_leads[0]
        parsed = parse_meta_lead(first_lead)
        
        # Try to save directly with better error handling
        try:
            if parsed.get('meta_lead_id'):
                existing = supabase.table('leads').select('id').eq('meta_lead_id', parsed.get('meta_lead_id')).execute()
                if existing.data:
                    return jsonify({
                        'success': True,
                        'message': f'Lead already exists: {parsed.get("name")}',
                        'existing': True
                    }), 200
            
            # Try insert
            response = supabase.table('leads').insert(parsed).execute()
            
            if response.data:
                return jsonify({
                    'success': True,
                    'message': f'Successfully saved lead: {parsed.get("name")}',
                    'lead': response.data[0]
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'No data returned from insert',
                    'lead_data': parsed
                }), 500
                
        except Exception as save_error:
            import traceback
            return jsonify({
                'success': False,
                'message': f'Failed to save lead: {parsed.get("name")}',
                'error': str(save_error),
                'traceback': traceback.format_exc(),
                'lead_data': parsed
            }), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/leads/check-forms', methods=['GET'])
def check_lead_forms():
    """Check all lead forms on the page"""
    try:
        url = f'{META_BASE_URL}/{META_PAGE_ID}/leadgen_forms'
        params = {
            'fields': 'id,name,status,leads_count',
            'access_token': META_PAGE_ACCESS_TOKEN
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return jsonify({
            'success': True,
            'forms': data.get('data', []),
            'current_form_id': META_LEAD_FORM_ID
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/sync-event', methods=['POST'])
def sync_lead_event(lead_id):
    """Send lead qualification event to Meta Event Manager"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', 'Lead')  # Lead, Purchase, etc
        
        # Get lead from database
        response = supabase.table('leads').select('*').eq('id', lead_id).execute()
        lead = response.data[0] if response.data else None
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Send to Meta
        event_data = {
            'email': lead.get('email', ''),
            'phone': lead.get('phone', ''),
            'name': lead.get('name', ''),
            'premium': lead.get('premium', 0),
            'source_url': request.host_url
        }
        
        result = send_event_to_meta(lead_id, event_type, event_data)
        
        # Update lead sync timestamp and status
        supabase.table('leads').update({
            'last_sync': datetime.utcnow().isoformat(),
            'sync_status': 'sent' if result else 'failed'
        }).eq('id', lead_id).execute()
        
        # Log sync event
        supabase.table('sync_events').insert({
            'lead_id': lead_id,
            'event_type': event_type,
            'meta_response': result,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        return jsonify({
            'success': True,
            'message': f'Event "{event_type}" sent to Meta Event Manager',
            'meta_response': result
        }), 200
    
    except Exception as e:
        print(f"Error syncing lead event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/create', methods=['POST'])
def create_lead():
    """Create manual lead"""
    try:
        data = request.get_json()
        
        new_lead = {
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'type': data.get('type', 'general'),
            'status': data.get('status', 'New Lead'),
            'potential_status': data.get('potential_status', 'qualified'),
            'notes': data.get('notes', ''),
            'is_manual': True,
            'premium': float(data.get('premium', 0)),
            'renewal_date': data.get('renewal_date'),
            'insurance_type': data.get('insurance_type'),
            'policy_term': data.get('policy_term'),
            'visa_type': data.get('visa_type'),
            'coverage': float(data.get('coverage', 0)) if data.get('coverage') else None,
            'trip_start': data.get('trip_start'),
            'trip_end': data.get('trip_end'),
            'sync_status': 'pending',
            'sync_signal': 'green',
            'created_at': datetime.utcnow().isoformat()
        }
        
        saved = save_lead_to_supabase(new_lead)
        return jsonify({'success': True, 'data': saved}), 201
    
    except Exception as e:
        print(f"Error creating lead: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead"""
    try:
        data = request.get_json()
        
        response = supabase.table('leads').update(data).eq('id', lead_id).execute()
        
        return jsonify({'success': True, 'data': response.data[0] if response.data else None}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Delete lead"""
    try:
        # Delete from clients_data and properties_data first
        supabase.table('clients_data').delete().eq('lead_id', lead_id).execute()
        supabase.table('properties_data').delete().eq('lead_id', lead_id).execute()
        # Then delete from leads
        supabase.table('leads').delete().eq('id', lead_id).execute()
        return jsonify({'success': True, 'message': 'Lead and all related data deleted'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/clear-all', methods=['POST'])
def clear_all_leads():
    """Delete all leads from database"""
    try:
        # Get all lead IDs first
        all_leads = supabase.table('leads').select('id').execute()
        
        if all_leads.data:
            # Delete each lead
            for lead in all_leads.data:
                supabase.table('leads').delete().eq('id', lead['id']).execute()
            
            return jsonify({
                'success': True, 
                'message': f'Cleared {len(all_leads.data)} leads from database'
            }), 200
        else:
            return jsonify({
                'success': True, 
                'message': 'Database already empty'
            }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/signal', methods=['POST'])
def update_signal(lead_id):
    """Update lead signal (green/red)"""
    try:
        data = request.get_json()
        signal = data.get('signal', 'green')  # 'green' or 'red'
        
        supabase.table('leads').update({
            'sync_signal': signal,
            'potential_status': 'qualified' if signal == 'green' else 'not-qualified'
        }).eq('id', lead_id).execute()
        
        return jsonify({'success': True, 'message': f'Signal updated to {signal}'}), 200
    
    except Exception as e:
        print(f"Error updating signal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Meta webhook endpoint for incoming leads"""
    
    if request.method == 'GET':
        # Webhook verification
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        
        if hub_verify_token != META_WEBHOOK_VERIFY_TOKEN:
            return 'Invalid verify token', 403
        
        return hub_challenge, 200
    
    elif request.method == 'POST':
        # Verify signature
        hub_signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_meta_webhook(request.data, hub_signature):
            return 'Invalid signature', 403
        
        data = request.get_json()
        
        # Process incoming leads
        entry = data.get('entry', [{}])[0]
        messaging = entry.get('messaging', [])
        
        for msg in messaging:
            if msg.get('message', {}).get('is_echo'):
                continue
            
            sender_id = msg.get('sender', {}).get('id')
            message = msg.get('message', {}).get('text', '')
            
            # Save to Supabase
            lead_data = {
                'meta_user_id': sender_id,
                'message': message,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'New Lead',
                'is_manual': False
            }
            save_lead_to_supabase(lead_data)
        
        return jsonify({'success': True}), 200


# ========== PDF PARSING ENDPOINT ==========

@app.route('/api/parse-mvr', methods=['POST'])
def parse_mvr():
    """Parse uploaded MVR PDF and extract driver information"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Read file content
        pdf_content = file.read()
        
        # Parse the PDF
        result = parse_mvr_pdf(pdf_content)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Return extracted data
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/parse-dash', methods=['POST'])
def parse_dash():
    """Parse uploaded DASH PDF and extract driver information"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Read file content
        pdf_content = file.read()
        
        # Parse the PDF
        result = parse_dash_pdf(pdf_content)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Return extracted data AND raw text for debugging
        return jsonify({
            'success': True,
            'data': result['data'],
            'raw_text': result['raw_text'][:1000]  # First 1000 chars for debugging
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/save-client', methods=['POST'])
def save_client():
    """Save complete client data to Supabase linked to a lead"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"💾 Saving client data to Supabase...")
        print(f"📊 Data received keys: {list(data.keys())}")
        print(f"📊 Received drivers: {len(data.get('drivers', []))} driver(s)")
        
        # Get email/phone/name to identify the lead
        email = None
        phone = None
        name = None
        
        if data.get('drivers') and len(data['drivers']) > 0:
            driver = data['drivers'][0]
            print(f"🔍 First driver keys: {list(driver.keys())[:5]}...")
            email = driver.get('personalEmail')
            phone = driver.get('personalMobile')
            name = driver.get('personalName') or driver.get('mainName')
            print(f"✓ Extracted - Email: {email}, Phone: {phone}, Name: {name}")
        else:
            print(f"⚠️ No drivers data found in request")
        
        print(f"📋 Lead info - Name: {name}, Email: {email}, Phone: {phone}")
        
        # Find lead by email, phone, or name
        lead_id = None
        
        # Try email first
        if email:
            try:
                result = supabase.table('leads').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by email {email}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by email: {str(e)}")
        
        # Try phone if email didn't work
        if not lead_id and phone:
            try:
                result = supabase.table('leads').select('id').eq('phone', phone).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by phone {phone}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by phone: {str(e)}")
        
        # Try name if still not found
        if not lead_id and name:
            try:
                result = supabase.table('leads').select('id').eq('name', name).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by name {name}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by name: {str(e)}")
        
        if not lead_id:
            print(f"⚠️ No lead found with email={email}, phone={phone}, name={name}")
        
        # Prepare data for storage - only include columns that exist in table
        save_data = {
            'email': email,
            'drivers': data.get('drivers', []),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add lead_id if found
        if lead_id:
            save_data['lead_id'] = lead_id
        
        print(f"💾 INSERT/UPDATE STEP - lead_id: {lead_id}, email: {email}, phone: {phone}")
        print(f"📦 Data to save keys: {list(save_data.keys())}")
        print(f"📦 Drivers count: {len(save_data.get('drivers', []))}")
        
        # Insert or update in clients_data table
        if email:
            print(f"💡 Saving client data by email: {email} (lead_id: {lead_id})")
            try:
                # Prefer to update by lead_id if found, else by email
                if lead_id:
                    result = supabase.table('clients_data').select('id').eq('lead_id', lead_id).limit(1).execute()
                    if result.data and len(result.data) > 0:
                        print(f"🔄 Existing record found for lead {lead_id}, updating...")
                        save_result = supabase.table('clients_data').update(save_data).eq('lead_id', lead_id).execute()
                        print(f"✅ Updated existing client data for lead {lead_id}")
                    else:
                        print(f"📝 No existing record for lead {lead_id}, inserting new...")
                        save_result = supabase.table('clients_data').insert(save_data).execute()
                        print(f"✅ Inserted new client data for lead {lead_id}")
                        if save_result.data:
                            print(f"   Inserted ID: {save_result.data[0].get('id')}")
                else:
                    # Always upsert by email if no lead_id
                    result = supabase.table('clients_data').select('id').eq('email', email).limit(1).execute()
                    if result.data and len(result.data) > 0:
                        print(f"🔄 Existing record found for email {email}, updating...")
                        save_result = supabase.table('clients_data').update(save_data).eq('email', email).execute()
                        print(f"✅ Updated client data by email {email}")
                    else:
                        print(f"📝 No existing record for email {email}, inserting new...")
                        save_result = supabase.table('clients_data').insert(save_data).execute()
                        print(f"✅ Inserted new client data by email {email}")
                        if save_result.data:
                            print(f"   Inserted ID: {save_result.data[0].get('id')}")
            except Exception as e:
                print(f"❌ Error saving client data: {str(e)}")
                import traceback
                traceback.print_exc()
                save_result = None
        else:
            print(f"❌ Cannot save - no email available in drivers")
            return jsonify({
                'success': False,
                'error': 'Cannot save without email'
            }), 400
        
        print(f"✅ Client data save operation completed")
        
        # Verify data was actually saved
        try:
            verify_result = supabase.table('clients_data').select('count', count='exact').execute()
            print(f"📊 Total clients_data rows in DB: {verify_result.count}")
        except Exception as e:
            print(f"⚠️ Could not verify save: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Client data saved successfully',
            'lead_id': lead_id,
            'email': email,
            'phone': phone
        }), 200
        
    except Exception as e:
        print(f"❌ Error saving client: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to save client: {str(e)}'
        }), 500


@app.route('/api/get-client-data/<query>', methods=['GET'])
def get_client_data(query):
    """Retrieve saved client data by email or lead ID"""
    try:
        print(f"📂 Retrieving client data for: {query}")
        
        # Try to find by lead_id first (if valid UUID format)
        try:
            if len(query) == 36 and query.count('-') == 4:  # UUID format check
                result = supabase.table('clients_data').select('*').eq('lead_id', query).limit(1).execute()
                if result.data and len(result.data) > 0:
                    print(f"✅ Found client data by lead_id: {query}")
                    return jsonify({
                        'success': True,
                        'data': result.data[0]
                    }), 200
        except Exception as e:
            print(f"⚠️ Error searching by lead_id: {str(e)}")
        
        # Try to find by email (primary search)
        try:
            result = supabase.table('clients_data').select('*').eq('email', query).limit(1).execute()
            if result.data and len(result.data) > 0:
                print(f"✅ Found client data by email: {query}")
                return jsonify({
                    'success': True,
                    'data': result.data[0]
                }), 200
        except Exception as e:
            print(f"⚠️ Error searching by email: {str(e)}")
        
        print(f"⚠️ No client data found for: {query}")
        return jsonify({
            'success': False,
            'error': 'No data found',
            'data': None
        }), 404
        
    except Exception as e:
        print(f"❌ Error retrieving client data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve client data: {str(e)}'
        }), 500



@app.route('/api/save-property', methods=['POST'])

@app.route('/api/get-property-data/<query>', methods=['GET'])
def get_property_data(query):
    """Retrieve saved property data by email or lead ID"""
    try:
        print(f"📂 Retrieving property data for: {query}")
        # Try to find by email (primary search)
        try:
            result = supabase.table('properties').select('*').eq('customer->>email', query).limit(1).execute()
            if result.data and len(result.data) > 0:
                print(f"✅ Found property data by email: {query}")
                return jsonify({
                    'success': True,
                    'data': result.data[0]
                }), 200
        except Exception as e:
            print(f"⚠️ Error searching by email: {str(e)}")
        print(f"⚠️ No property data found for: {query}")
        return jsonify({
            'success': False,
            'error': 'No data found',
            'data': None
        }), 404
    except Exception as e:
        print(f"❌ Error retrieving property data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve property data: {str(e)}'
        }), 500

@app.route('/api/save-property', methods=['POST'])
def save_property():
    """Save complete property data to Supabase, upsert by customer email"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        print(f"🏠 Saving property data to Supabase...")
        print(f"📊 Data received: {json.dumps(data, indent=2)[:500]}...")
        # Extract email from customer object
        email = ''
        if 'customer' in data and isinstance(data['customer'], dict):
            email = data['customer'].get('email', '').strip().lower()
        if not email:
            return jsonify({'success': False, 'error': 'No email found in customer data'}), 400
        # Upsert by customer email
        result = supabase.table('properties').upsert(data, on_conflict=['customer->>email']).execute()
        print(f"✅ Property saved successfully for email: {email}")
        return jsonify({
            'success': True,
            'message': 'Property data saved successfully',
            'data': result.data
        }), 200
    except Exception as e:
        print(f"❌ Error saving property: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save property: {str(e)}'
        }), 500


# ========== INITIALIZATION ==========

if __name__ == '__main__':
    # Create tables if they don't exist
    try:
        # Check if leads table exists, if not this will fail gracefully
        supabase.table('leads').select('*').limit(1).execute()
    except:
        print("Note: Ensure 'leads' table exists in Supabase")
    
    port = int(os.getenv('FLASK_PORT', 5000))
    # Disable use_reloader to avoid issues on Windows
    app.run(debug=True, port=port, host='0.0.0.0', use_reloader=False)
