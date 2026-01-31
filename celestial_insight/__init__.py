"""
Celestial Insight - Django Project
"""

import os

# Print startup message when Django loads this module
print("=" * 60)
print("🔮 CELESTIAL INSIGHT - Django Server")
print("=" * 60)
print(f"📡 API URL: {os.getenv('API_URL', 'http://localhost:8000')}")
print(f"🗄️  Database: {os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')}")
print("-" * 60)
print("✅ Django initialized successfully!")
print("=" * 60)
