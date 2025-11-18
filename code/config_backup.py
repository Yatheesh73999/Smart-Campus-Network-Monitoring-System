"""
Simple configuration backup & restore for Smart Campus NMS.
Backs up devices.json into backups/ with timestamp.
"""

import os
import shutil
from datetime import datetime

CONFIG_FILE = "devices.json"
BACKUP_DIR = "backups"


def backup_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] {CONFIG_FILE} not found.")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"devices_{timestamp}.json"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    shutil.copy2(CONFIG_FILE, backup_path)
    print(f"[BACKUP] Saved configuration backup to {backup_path}")


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print("[INFO] No backups found.")
        return []

    files = sorted(os.listdir(BACKUP_DIR))
    for f in files:
        print(f"- {f}")
    return files


def restore_latest():
    """Restore the most recent backup file over devices.json."""
    if not os.path.exists(BACKUP_DIR):
        print("[ERROR] No backup directory found.")
        return

    files = sorted(os.listdir(BACKUP_DIR))
    if not files:
        print("[ERROR] No backup files to restore.")
        return

    latest = files[-1]
    latest_path = os.path.join(BACKUP_DIR, latest)
    shutil.copy2(latest_path, CONFIG_FILE)
    print(f"[RESTORE] Restored {latest_path} to {CONFIG_FILE}")


if __name__ == "__main__":
    print("1) Backup config\n2) List backups\n3) Restore latest")
    choice = input("Choose option: ").strip()
    if choice == "1":
        backup_config()
    elif choice == "2":
        list_backups()
    elif choice == "3":
        restore_latest()
    else:
        print("Invalid choice.")
