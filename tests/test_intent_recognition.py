#!/usr/bin/env python3
"""
Test intent recognition for user and storage commands
"""

import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

from nix_humanity.core.intents import IntentRecognizer, IntentType

def test_intent_recognition():
    """Test if intent recognition works for new commands"""
    recognizer = IntentRecognizer()
    
    test_cases = [
        # User management
        ("create user alice", IntentType.CREATE_USER),
        ("add new user bob", IntentType.CREATE_USER),
        ("list users", IntentType.LIST_USERS),
        ("show me all users", IntentType.LIST_USERS),
        ("add alice to docker group", IntentType.ADD_USER_TO_GROUP),
        ("change password alice", IntentType.CHANGE_PASSWORD),
        ("grant alice sudo", IntentType.GRANT_SUDO),
        ("make bob sudoer", IntentType.GRANT_SUDO),
        
        # Storage management
        ("disk usage", IntentType.DISK_USAGE),
        ("show disk space", IntentType.DISK_USAGE),
        ("analyze disk", IntentType.ANALYZE_DISK),
        ("what's using disk space", IntentType.ANALYZE_DISK),
        ("mount /dev/sdb1", IntentType.MOUNT_DEVICE),
        ("unmount /dev/sdb1", IntentType.UNMOUNT_DEVICE),
        ("find large files", IntentType.FIND_LARGE_FILES),
        ("find the 20 largest files", IntentType.FIND_LARGE_FILES),
    ]
    
    print("🧪 Testing Intent Recognition")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for query, expected_type in test_cases:
        intent = recognizer.recognize(query)
        
        if intent.type == expected_type:
            print(f"✅ '{query}' → {intent.type.value}")
            if intent.entities:
                print(f"   Entities: {intent.entities}")
            passed += 1
        else:
            print(f"❌ '{query}' → {intent.type.value} (expected: {expected_type.value})")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")

if __name__ == "__main__":
    test_intent_recognition()