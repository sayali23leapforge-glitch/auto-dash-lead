"""
Run the Flask backend server locally
"""
import sys
import os

# Add parent directory to path so we can import backend module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

# Now import and run the app
from backend import app

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"🚀 Starting Flask server on http://localhost:{port}")
    print(f"📂 Backend directory: {os.getcwd()}")
    app.app.run(debug=True, port=port, host='0.0.0.0')
