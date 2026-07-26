import json
from pathlib import Path
from .config import ROOT, OUTPUT_DIR

INVENTORY_FILE = ROOT / "stock_inventory.json"


def load():
    if not INVENTORY_FILE.exists():
        return {"available": [], "used": []}
    return json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))


def save(inv: dict):
    INVENTORY_FILE.write_text(json.dumps(inv, indent=2), encoding="utf-8")


def scan():
    inv = load()
    known = {c["path"] for c in inv["available"]} | {c["path"] for c in inv["used"]}
    found = set()
    for d in sorted(OUTPUT_DIR.iterdir()):
        bd = d / "broll"
        if bd.exists():
            for f in sorted(bd.glob("scene_*.mp4")):
                found.add(str(f.resolve()))
    for p in sorted(found - known):
        inv["available"].append({"path": p, "from": Path(p).parent.parent.name})
    inv["available"] = [c for c in inv["available"] if Path(c["path"]).exists()]
    inv["used"] = [c for c in inv["used"] if Path(c["path"]).exists()]
    save(inv)
    return inv


def take(n: int) -> list[Path]:
    inv = scan()
    taken: list[Path] = []
    for _ in range(n):
        if not inv["available"]:
            break
        clip = inv["available"].pop(0)
        p = Path(clip["path"])
        if p.exists():
            inv["used"].append(clip)
            taken.append(p)
        else:
            continue
    save(inv)
    return taken


def count_available() -> int:
    return len(load().get("available", []))
