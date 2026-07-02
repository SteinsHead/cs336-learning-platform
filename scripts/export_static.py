from pathlib import Path
import json
import shutil
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DIST = ROOT / "dist"

sys.path.insert(0, str(ROOT))

from backend.content import curriculum  # noqa: E402


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def download_file(url, target):
    if not url:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            target.write_bytes(response.read())
        return True
    except Exception as error:  # noqa: BLE001 - static export should keep working offline.
        print(f"Warning: could not mirror {url}: {error}")
        return False


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for filename in ("index.html", "app.js", "styles.css", "config.js"):
        copy_file(FRONTEND / filename, DIST / filename)

    data_dir = DIST / "data"
    data_dir.mkdir()
    data = curriculum()
    (data_dir / "curriculum.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lectures_dir = data_dir / "lectures"
    for lesson in data["lessons"]:
        material = lesson.get("official_material", {})
        local_url = material.get("local_reader_url", "")
        remote_url = material.get("reader_url", "")
        if local_url and remote_url:
            download_file(remote_url, DIST / local_url)

    copy_file(DIST / "index.html", DIST / "404.html")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Static site exported to {DIST}")


if __name__ == "__main__":
    main()
