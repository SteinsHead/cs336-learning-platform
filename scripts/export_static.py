from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DIST = ROOT / "dist"

sys.path.insert(0, str(ROOT))

from backend.content import curriculum  # noqa: E402


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for filename in ("index.html", "app.js", "styles.css"):
        copy_file(FRONTEND / filename, DIST / filename)

    data_dir = DIST / "data"
    data_dir.mkdir()
    (data_dir / "curriculum.json").write_text(
        json.dumps(curriculum(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    copy_file(DIST / "index.html", DIST / "404.html")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Static site exported to {DIST}")


if __name__ == "__main__":
    main()
