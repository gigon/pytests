#!/usr/bin/env python3
"""
Launcher script for the Shufersal Coupon UI
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from coupon_ui.app import app, init_db

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    print(f"Starting Shufersal Coupon UI on http://{host}:{port}")
    print("Access the web interface in your browser")
    print("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)