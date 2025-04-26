#!/usr/bin/env python
"""
Script to initialize the database.
Run this from the project root directory.
"""
from database.init_db import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!") 