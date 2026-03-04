#!/usr/bin/env python3
"""
🧹 GENESIS CLEANUP SCRIPT
Removes all user-generated data, chat history, and test files
so the repository is clean for a fresh start or open-source distribution.
"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Files and directories to remove
TARGETS = {
    "files": [
        PROJECT_ROOT / "memory" / "chat_sessions.json",
        PROJECT_ROOT / "mac_log.txt",
        PROJECT_ROOT / "mac_script.py",
        PROJECT_ROOT / "mac_address.py",
        PROJECT_ROOT / "script.py",
        PROJECT_ROOT / "wordlist.py",
        PROJECT_ROOT / "generate_wordlist.py",
        PROJECT_ROOT / "analysis.py",
        PROJECT_ROOT / "sys_check.py",
    ],
    "directories": [
        PROJECT_ROOT / "memory" / "chromadb_data",
    ],
}


def cleanup():
    print("🧹 Genesis Cleanup — Removing user data and test artifacts...\n")

    removed = 0

    for filepath in TARGETS["files"]:
        if filepath.exists():
            filepath.unlink()
            print(f"  ✅ Deleted file:      {filepath.relative_to(PROJECT_ROOT)}")
            removed += 1
        else:
            print(f"  ⏭️  Skipped (not found): {filepath.relative_to(PROJECT_ROOT)}")

    for dirpath in TARGETS["directories"]:
        if dirpath.exists():
            shutil.rmtree(dirpath)
            print(f"  ✅ Deleted directory:  {dirpath.relative_to(PROJECT_ROOT)}/")
            removed += 1
        else:
            print(f"  ⏭️  Skipped (not found): {dirpath.relative_to(PROJECT_ROOT)}/")

    print(f"\n🎉 Cleanup complete. Removed {removed} item(s).")
    print("   You can now safely commit or distribute this repository.")


if __name__ == "__main__":
    cleanup()
