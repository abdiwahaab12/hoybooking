#!/usr/bin/env python3
import os
from config import Config

print("Testing database configuration...")
print(f"DATABASE_URL environment variable: {os.environ.get('DATABASE_URL')}")
print(f"Config SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")

# Test if we can create the database
from app import app
with app.app_context():
    print(f"App SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
