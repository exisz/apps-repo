#!/usr/bin/env python3
"""
rebuild-index.py — Scan apps/*/metadata.json + apks → regenerate index.json
"""
import json
import hashlib
import os
import glob
from datetime import datetime, timezone

APPS_DIR = os.path.join(os.path.dirname(__file__), "..", "apps")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "index.json")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_index():
    apps = []
    for meta_path in sorted(glob.glob(os.path.join(APPS_DIR, "*/metadata.json"))):
        app_dir = os.path.dirname(meta_path)
        app_dir_name = os.path.basename(app_dir)
        with open(meta_path) as f:
            meta = json.load(f)

        # Scan APKs in this app dir and build version entries
        apk_files = sorted(glob.glob(os.path.join(app_dir, "*.apk")))
        versions = list(meta.get("versions", []))

        # Index APKs not already in versions
        existing_apks = {v["apk"] for v in versions}
        for apk_path in apk_files:
            rel_apk = f"apps/{app_dir_name}/{os.path.basename(apk_path)}"
            if rel_apk not in existing_apks:
                size = os.path.getsize(apk_path)
                sha = sha256_file(apk_path)
                versions.append({
                    "versionCode": 0,
                    "versionName": "unknown",
                    "apk": rel_apk,
                    "size": size,
                    "released_at": datetime.now(timezone.utc).isoformat(),
                    "sha256": sha,
                    "changelog": ""
                })

        meta["versions"] = versions
        apps.append(meta)

    index = {
        "version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "apps": apps
    }
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"index.json rebuilt with {len(apps)} app(s)")


if __name__ == "__main__":
    build_index()
