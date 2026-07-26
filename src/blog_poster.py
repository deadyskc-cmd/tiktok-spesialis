import json, os, time
from pathlib import Path
from datetime import datetime
from . import state, blogger
from .config import ROOT

POSTED_LOG = ROOT / "blog_posted.json"

def _load_posted() -> list:
    if POSTED_LOG.exists():
        return json.loads(POSTED_LOG.read_text(encoding="utf-8"))
    return []

def _save_posted(posted: list):
    POSTED_LOG.write_text(json.dumps(posted, indent=2), encoding="utf-8")

def main():
    if not os.environ.get("BLOG_ID"):
        print("BLOG_ID not set, skipping")
        return

    posted = _load_posted()
    published = state.load().get("published", [])

    for entry in published:
        vid = entry.get("video_id") or entry.get("path", "")
        if vid in posted:
            continue

        print(f"Posting: {entry.get('title', 'untitled')}")
        try:
            url = blogger.publish(entry)
            if url:
                posted.append(vid)
                _save_posted(posted)
                print(f"  OK: {url}")
            else:
                print("  FAILED to post")
        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()
