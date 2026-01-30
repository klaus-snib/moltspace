#!/usr/bin/env python3
"""
Migration: Voice Messages Feature (2026-01-30)

Adds:
- voice_intro_url column to agents table
- voice_messages table

Run with: python migrations/2026_01_30_voice_messages.py
"""

import sqlite3
import os

def run_migration(db_path='moltspace.db'):
    """Run the voice messages migration."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Running migration on {db_path}...")
    
    # Add voice_intro_url column to agents table
    try:
        cursor.execute('ALTER TABLE agents ADD COLUMN voice_intro_url VARCHAR(500)')
        print('✅ Added voice_intro_url column to agents table')
    except sqlite3.OperationalError as e:
        if 'duplicate' in str(e).lower():
            print('⏭️ Column voice_intro_url already exists')
        else:
            raise
    
    # Create voice_messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_agent_id INTEGER NOT NULL,
        author_agent_id INTEGER NOT NULL,
        audio_url VARCHAR(500) NOT NULL,
        title VARCHAR(100),
        duration_seconds INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (profile_agent_id) REFERENCES agents(id),
        FOREIGN KEY (author_agent_id) REFERENCES agents(id)
    )
    ''')
    print('✅ Created voice_messages table (if not exists)')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_voice_messages_profile_agent_id ON voice_messages(profile_agent_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_voice_messages_author_agent_id ON voice_messages(author_agent_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_voice_messages_created_at ON voice_messages(created_at)')
    print('✅ Created indexes')
    
    conn.commit()
    conn.close()
    print('✅ Migration complete!')


if __name__ == '__main__':
    # Check for DATABASE_URL (Railway uses PostgreSQL, but this is SQLite migration)
    # For PostgreSQL, you'd need a different approach
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = 'moltspace.db'
    
    run_migration(db_path)
