#!/usr/bin/env python3
"""Cleanup script to remove migrated data from 'team' table after successful migration"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_supabase, init_db

async def cleanup_team_table():
    """Clean up 'team' table after successful migration to 'team_members'"""
    await init_db()
    supabase = get_supabase()
    
    print("🧹 Cleaning up 'team' table")
    print("=" * 50)
    
    # Verify team_members has data before cleanup
    print("\n🔍 Verifying 'team_members' table has data...")
    try:
        result = supabase.table("team_members").select("*").execute()
        team_members_data = result.data or []
        print(f"   Found {len(team_members_data)} records in 'team_members' table")
        
        if len(team_members_data) == 0:
            print("   ❌ No data in 'team_members' table - aborting cleanup!")
            return
        
        # Show what will be deleted
        print(f"\n📋 Checking 'team' table for cleanup...")
        result = supabase.table("team").select("*").execute()
        team_data = result.data or []
        print(f"   Found {len(team_data)} records in 'team' table to clean up")
        
        if len(team_data) == 0:
            print("   ✅ 'team' table is already clean")
            return
        
        # List items to be deleted
        for item in team_data:
            print(f"   - Will delete: {item.get('name', 'Unknown')} (ID: {item.get('id')})")
        
        # Confirm before deletion
        response = input(f"\n❓ Delete {len(team_data)} records from 'team' table? (y/N): ")
        if response.lower() != 'y':
            print("   🚫 Cleanup cancelled")
            return
        
        # Delete all records
        print(f"\n🗑️ Deleting records from 'team' table...")
        for item in team_data:
            try:
                delete_result = supabase.table("team").delete().eq("id", item["id"]).execute()
                if delete_result.data:
                    print(f"   ✅ Deleted: {item.get('name', 'Unknown')}")
                else:
                    print(f"   ❌ Failed to delete: {item.get('name', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ Error deleting {item.get('name', 'Unknown')}: {e}")
        
        # Verify cleanup
        print(f"\n🔍 Verifying cleanup...")
        result = supabase.table("team").select("*").execute()
        remaining_data = result.data or []
        print(f"   Remaining records in 'team' table: {len(remaining_data)}")
        
        if len(remaining_data) == 0:
            print("   ✅ Cleanup successful! 'team' table is now empty")
        else:
            print("   ⚠️ Some records remain - check for errors above")
            
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_team_table())