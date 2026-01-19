#!/usr/bin/env python3
"""
Quick Start Script - Meta Leads Dashboard
Run this to set up and start the application
"""

import os
import sys
import subprocess
import time

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step_num, text):
    print(f"\n[Step {step_num}] {text}")

def main():
    print_header("Meta Leads Dashboard - Quick Start")
    
    # Step 1: Check Python
    print_step(1, "Checking Python installation...")
    try:
        python_version = subprocess.check_output([sys.executable, '--version']).decode().strip()
        print(f"✓ {python_version}")
    except:
        print("✗ Python not found. Please install Python 3.8+")
        return False
    
    # Step 2: Create virtual environment
    print_step(2, "Setting up virtual environment...")
    venv_path = "venv"
    if not os.path.exists(venv_path):
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            print(f"✓ Virtual environment created at {venv_path}")
        except Exception as e:
            print(f"✗ Failed to create venv: {e}")
            return False
    else:
        print(f"✓ Virtual environment already exists")
    
    # Step 3: Install dependencies
    print_step(3, "Installing dependencies...")
    try:
        if sys.platform == "win32":
            activate_cmd = f"{venv_path}\\Scripts\\activate.bat && "
            pip_cmd = f"{venv_path}\\Scripts\\pip"
        else:
            activate_cmd = f"source {venv_path}/bin/activate && "
            pip_cmd = f"{venv_path}/bin/pip"
        
        subprocess.run([pip_cmd, "install", "-r", "backend/requirements.txt"], check=True)
        print("✓ Dependencies installed")
    except Exception as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    
    # Step 4: Check Supabase setup
    print_step(4, "Checking Supabase setup...")
    print("   ⚠ Manual step required:")
    print("   1. Go to Supabase dashboard")
    print("   2. Run the SQL from 'supabase_schema.sql' to create tables")
    print("   ✓ Press Enter when complete...")
    input()
    
    # Step 5: Check .env.local
    print_step(5, "Checking environment configuration...")
    if os.path.exists(".env.local"):
        print("✓ .env.local found with credentials")
    else:
        print("✗ .env.local not found. Please create it with your credentials.")
        return False
    
    # Step 6: Start backend
    print_step(6, "Starting Flask backend...")
    print("   Backend will run on http://localhost:5000")
    print("   Dashboard: file:///d:/Auto%20dashboard/meta%20dashboard.html")
    print("\n   Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "backend/app.py"])
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
        return True
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
