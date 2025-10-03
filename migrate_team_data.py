#!/usr/bin/env python3
"""Migration script to move team data from 'team' table to 'team_members' table"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_supabase, init_db

async def migrate_team_data():
    """Move data from 'team' table to 'team_members' table"""
    await init_db()
    supabase = get_supabase()
    
    print("🔄 Migrating Team Data")
    print("=" * 50)
    
    # Get data from 'team' table
    print("\n📋 Reading data from 'team' table...")
    try:
        result = supabase.table("team").select("*").execute()
        team_data = result.data or []
        print(f"   Found {len(team_data)} records in 'team' table")
        
        if not team_data:
            print("   ✅ No data to migrate")
            return
        
        # Transform and insert into 'team_members' table
        print("\n👥 Migrating to 'team_members' table...")
        for item in team_data:
            print(f"   📤 Migrating: {item.get('name', 'Unknown')}")
            
            # Map fields from 'team' to 'team_members' (adjust field names as needed)
            member_data = {
                "name": item.get("name"),
                "position": item.get("position") or item.get("role"),  # Handle both field names
                "bio": item.get("bio", ""),
                "image": item.get("image"),
                "social_links": item.get("social_links", {}),
                "order": item.get("order", 0),
                "active": item.get("active", True)
            }
            
            # Insert into team_members table
            try:
                insert_result = supabase.table("team_members").insert(member_data).execute()
                if insert_result.data:
                    print(f"   ✅ Migrated: {member_data['name']}")
                else:
                    print(f"   ❌ Failed to migrate: {member_data['name']}")
            except Exception as e:
                print(f"   ❌ Error migrating {member_data['name']}: {e}")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        result = supabase.table("team_members").select("*").execute()
        team_members_data = result.data or []
        print(f"   Found {len(team_members_data)} records in 'team_members' table after migration")
        
        if len(team_members_data) >= len(team_data):
            print("   ✅ Migration successful!")
            print("\n⚠️  Consider cleaning up 'team' table after verifying everything works")
        else:
            print("   ❌ Migration incomplete - check for errors above")
            
    except Exception as e:
        print(f"   ❌ Error during migration: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_team_data())