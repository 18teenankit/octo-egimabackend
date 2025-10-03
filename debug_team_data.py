#!/usr/bin/env python3
"""Debug script to check team data in database"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_supabase, init_db

async def check_team_tables():
    """Check both 'team' and 'team_members' tables"""
    await init_db()  # Initialize the database connection
    supabase = get_supabase()
    
    print("🔍 Checking Team Data in Database")
    print("=" * 50)
    
    # Check team table
    print("\n📋 Checking 'team' table:")
    try:
        result = supabase.table("team").select("*").execute()
        team_data = result.data or []
        print(f"   Found {len(team_data)} records in 'team' table")
        for item in team_data:
            print(f"   - {item}")
    except Exception as e:
        print(f"   ❌ Error querying 'team' table: {e}")
    
    # Check team_members table
    print("\n👥 Checking 'team_members' table:")
    try:
        result = supabase.table("team_members").select("*").execute()
        team_members_data = result.data or []
        print(f"   Found {len(team_members_data)} records in 'team_members' table")
        for item in team_members_data:
            print(f"   - {item}")
    except Exception as e:
        print(f"   ❌ Error querying 'team_members' table: {e}")

if __name__ == "__main__":
    asyncio.run(check_team_tables())