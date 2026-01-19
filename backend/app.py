"""
Meta/Facebook Lead Form Backend
Integrates with Facebook Lead API and Supabase
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
import hmac
import hashlib
from pdf_parser import parse_mvr_pdf, parse_dash_pdf

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.local'))

app = Flask(__name__)
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
    """Fetch ALL leads from Meta Lead Form API with pagination"""
    try:
        all_leads = []
        url = f'{META_BASE_URL}/{META_LEAD_FORM_ID}/leads'
        params = {
            'fields': 'id,created_time,field_data,adgroup_id',
            'access_token': META_PAGE_ACCESS_TOKEN,
            'limit': 100  # Max per page
        }
        
        print(f"📞 Fetching leads from Meta API: {url}")
        print(f"🔑 Using Lead Form ID: {META_LEAD_FORM_ID}")
        
        # Fetch first page
        response = requests.get(url, params=params)
        print(f"📡 Meta API Response Status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        all_leads.extend(data.get('data', []))
        
        # Fetch remaining pages
        while 'paging' in data and 'next' in data['paging']:
            next_url = data['paging']['next']
            print(f"📄 Fetching next page...")
            response = requests.get(next_url)
            response.raise_for_status()
            data = response.json()
            all_leads.extend(data.get('data', []))
        
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
        'id': meta_lead_id,  # Use meta_lead_id as id for frontend compatibility
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
        'notes': '',
        'company': lead_dict.get('company', ''),
        'address': lead_dict.get('address', ''),
        'city': lead_dict.get('city', ''),
        'state': lead_dict.get('state', ''),
        'country': lead_dict.get('country', ''),
        'zip_code': lead_dict.get('zip_code', '')
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
        response = supabase.table('leads').insert(lead_data).execute()
        print(f"💾 Saved lead: {lead_data.get('name')} (ID: {response.data[0].get('id') if response.data else 'N/A'})")
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error saving lead to Supabase: {str(e)}")
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

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Meta Lead Dashboard Backend'}), 200


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get leads from database (instant load)"""
    filters = {}
    if request.args.get('type'):
        filters['type'] = request.args.get('type')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    
    print("📊 Loading leads from database (instant)...")
    
    # Get from database (instant)
    leads = get_leads_from_db(filters)
    
    print(f"📤 Returning {len(leads)} leads from database")
    return jsonify({'data': leads, 'count': len(leads)}), 200


@app.route('/api/leads/sync', methods=['POST'])
def sync_leads():
    """Fetch latest leads from Meta and save to Supabase"""
    try:
        meta_leads = get_leads_from_meta()
        saved_leads = []
        
        for meta_lead in meta_leads:
            parsed_lead = parse_meta_lead(meta_lead)
            saved = save_lead_to_supabase(parsed_lead)
            if saved:
                saved_leads.append(saved)
        
        return jsonify({
            'success': True,
            'message': f'Synced {len(saved_leads)} leads from Meta',
            'leads': saved_leads
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
        supabase.table('leads').delete().eq('id', lead_id).execute()
        
        return jsonify({'success': True, 'message': 'Lead deleted'}), 200
    
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
    """Save complete client data to Supabase"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"💾 Saving client data to Supabase...")
        print(f"📊 Data received: {json.dumps(data, indent=2)[:500]}...")
        
        # Insert or update in Supabase clients table
        result = supabase.table('clients').upsert(data).execute()
        
        print(f"✅ Client saved successfully")
        return jsonify({
            'success': True,
            'message': 'Client data saved successfully',
            'data': result.data
        }), 200
        
    except Exception as e:
        print(f"❌ Error saving client: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save client: {str(e)}'
        }), 500


@app.route('/api/save-property', methods=['POST'])
def save_property():
    """Save complete property data to Supabase"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"🏠 Saving property data to Supabase...")
        print(f"📊 Data received: {json.dumps(data, indent=2)[:500]}...")
        
        # Insert or update in Supabase properties table
        result = supabase.table('properties').upsert(data).execute()
        
        print(f"✅ Property saved successfully")
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
    app.run(debug=True, port=port, host='0.0.0.0')
