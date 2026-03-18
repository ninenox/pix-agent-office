"""
pytest configuration — shared fixtures และ path setup
"""

import os
import sys

# เพิ่ม agents/ และ backend/ เข้า path ให้ทุก test file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "agents"))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
