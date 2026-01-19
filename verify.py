#!/usr/bin/env python3
"""
Verification Script - Test Meta Leads Dashboard Setup
Run this to verify all components are working
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load env
load_dotenv('.env.local')

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check(name, condition, details=""):
    status = "✓" if condition else "✗"
    print(f"{status} {name}" + (f" - {details}" if details else ""))
    return condition

def main():
    print_section("Meta Leads Dashboard - Verification")
    
    all_good = True
    
    # Check 1: Environment Variables
    print_section("1. Environment Variables")
    
    required_env = {
        'VITE_SUPABASE_URL': 'Supabase URL',
        'VITE_SUPABASE_ANON_KEY': 'Supabase Anon Key',
        'META_APP_ID': 'Meta App ID',
        'META_PAGE_ACCESS_TOKEN': 'Meta Page Token',
        'META_LEAD_FORM_ID': 'Meta Lead Form ID',
    }
    
    for env_var, desc in required_env.items():
        value = os.getenv(env_var, '')
        is_set = bool(value.strip())
        all_good &= check(env_var, is_set, desc)
    
    # Check 2: Python Dependencies
    print_section("2. Python Dependencies")
    
    required_packages = [
        'flask',
        'flask_cors',
        'dotenv',
        'requests',
        'supabase'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
            all_good &= check(package, True, "Installed")
        except ImportError:
            all_good &= check(package, False, "NOT installed - run: pip install -r backend/requirements.txt")
    
    # Check 3: File Structure
    print_section("3. File Structure")
    
    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'meta dashboard.html',
        '.env.local',
        '.gitignore',
        'supabase_schema.sql',
        'README.md',
    ]
    
    for file in required_files:
        exists = os.path.exists(file)
        all_good &= check(file, exists)
    
    # Check 4: Backend Connectivity
    print_section("4. Backend Server")
    
    backend_url = 'http://localhost:5000'
    try:
        response = requests.get(f'{backend_url}/api/health', timeout=2)
        is_running = response.status_code == 200
        all_good &= check("Backend running", is_running, f"Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        all_good &= check("Backend running", False, "Server not responding on localhost:5000")
        print("   → Start backend with: python backend/app.py")
    except Exception as e:
        all_good &= check("Backend running", False, str(e))
    
    # Check 5: Supabase Connectivity (if backend is running)
    if is_running:
        print_section("5. Supabase Database")
        
        try:
            response = requests.get(f'{backend_url}/api/leads', timeout=5)
            if response.status_code == 200:
                data = response.json()
                all_good &= check("Database connection", True, f"Leads found: {data.get('count', 0)}")
            else:
                all_good &= check("Database connection", False, f"Status: {response.status_code}")
        except Exception as e:
            all_good &= check("Database connection", False, str(e))
            print("   → Ensure Supabase tables exist: Run supabase_schema.sql")
    
    # Check 6: Meta API Credentials
    print_section("6. Meta API Configuration")
    
    meta_app_id = os.getenv('META_APP_ID', '')
    meta_token = os.getenv('META_PAGE_ACCESS_TOKEN', '')
    
    all_good &= check("Meta App ID configured", len(meta_app_id) > 0)
    all_good &= check("Meta Access Token configured", len(meta_token) > 10)
    
    if len(meta_token) > 10:
        # Check if token is valid by checking first few chars
        print(f"   Token preview: {meta_token[:20]}...")
    
    # Summary
    print_section("Verification Summary")
    
    if all_good:
        print("✓ All checks passed!")
        print("\nNext steps:")
        print("1. Ensure backend is running: python backend/app.py")
        print("2. Open meta dashboard.html in browser")
        print("3. Click refresh button to load leads from Meta")
    else:
        print("✗ Some checks failed. See details above.")
        print("\nTroubleshooting:")
        print("- Backend: python backend/app.py")
        print("- Dependencies: pip install -r backend/requirements.txt")
        print("- Database: Run supabase_schema.sql in Supabase SQL editor")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
