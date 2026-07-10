from pathlib import Path
import json
import shutil
import subprocess
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


def download_file(url, target, attempts=3, timeout=60):
    if not url:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(f"{target.suffix}.part")
    curl = shutil.which("curl")
    if curl:
        for attempt in range(1, attempts + 1):
            result = subprocess.run(
                [
                    curl,
                    "--fail",
                    "--location",
                    "--silent",
                    "--show-error",
                    "--retry",
                    "2",
                    "--retry-all-errors",
                    "--connect-timeout",
                    "20",
                    "--max-time",
                    str(timeout * 3),
                    "--output",
                    str(partial),
                    url,
                ],
                check=False,
            )
            if result.returncode == 0 and partial.exists():
                partial.replace(target)
                return True
            print(f"Warning: curl could not mirror {url} on attempt {attempt}/{attempts}")
        partial.unlink(missing_ok=True)
        return False

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                target.write_bytes(response.read())
            return True
        except Exception as error:  # noqa: BLE001 - retry and report all material failures together.
            last_error = error
            print(f"Warning: could not mirror {url} on attempt {attempt}/{attempts}: {error}")
    if last_error:
        print(f"Warning: giving up on {url}: {last_error}")
    return False


def render_pdf_pages(pdf_path, output_dir, public_dir):
    try:
        import fitz  # PyMuPDF
    except Exception as error:  # noqa: BLE001
        print(f"Warning: PyMuPDF unavailable, cannot render {pdf_path.name}: {error}")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    images = []
    try:
        with fitz.open(pdf_path) as document:
            for index, page in enumerate(document, start=1):
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35), alpha=False)
                image_path = output_dir / f"page-{index:03d}.png"
                pixmap.save(image_path)
                images.append(f"{public_dir}/page-{index:03d}.png")
    except Exception as error:  # noqa: BLE001
        print(f"Warning: could not render {pdf_path.name}: {error}")
        return []
    return images


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for filename in ("index.html", "app.js", "styles.css", "config.js", "code-highlight.js", "pyodide-worker.js"):
        copy_file(FRONTEND / filename, DIST / filename)

    data_dir = DIST / "data"
    data_dir.mkdir()
    data = curriculum()
    material_failures = []

    lectures_dir = data_dir / "lectures"
    for lesson in data["lessons"]:
        material = lesson.get("official_material", {})
        local_url = material.get("local_reader_url", "")
        remote_url = material.get("reader_url", "")
        if local_url and remote_url:
            local_path = DIST / local_url
            downloaded = download_file(remote_url, local_path)
            if not downloaded:
                material_failures.append(f"{lesson['id']}: could not mirror {remote_url}")
                continue
            if local_path.stat().st_size < 100:
                material_failures.append(f"{lesson['id']}: mirrored material is unexpectedly small")
                continue
            if material.get("kind") == "slides-pdf":
                stem = local_path.stem
                public_dir = f"data/lectures/{stem}"
                page_images = render_pdf_pages(local_path, lectures_dir / stem, public_dir)
                material["page_images"] = page_images
                material["page_count"] = len(page_images)
                material["reader_mode"] = "image-deck" if page_images else "pdf-source"
                if page_images:
                    local_path.unlink(missing_ok=True)
                else:
                    material_failures.append(f"{lesson['id']}: PDF could not be rendered into in-platform pages")

    if material_failures:
        details = "\n".join(f"- {item}" for item in material_failures)
        raise RuntimeError(f"Static export is incomplete; refusing to publish:\n{details}")

    (data_dir / "curriculum.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    copy_file(DIST / "index.html", DIST / "404.html")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Static site exported to {DIST}")


if __name__ == "__main__":
    main()
