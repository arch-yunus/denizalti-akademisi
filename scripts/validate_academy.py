"""
Denizalti Akademisi repo dogrulayicisi.

Statik TRL panelinin veri butunlugunu ve Markdown baglantilarini kontrol eder.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "docs" / "data" / "projects.json"
DOCS_ROOT = ROOT / "docs"
MARKDOWN_FILES = [
    ROOT / "README.md",
    ROOT / "TRL_REHBERI.md",
    ROOT / "SOZLUK.md",
    ROOT / "CONTRIBUTING.md",
    *ROOT.glob("[0-9][0-9]_*/*.md"),
    *ROOT.glob("05_DUNYA_DEVLERI/*/*.md"),
]

LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def load_data() -> dict:
    if not DATA_FILE.exists():
        fail(f"Veri dosyasi bulunamadi: {DATA_FILE}")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def validate_project_data(data: dict) -> None:
    domain_ids = {domain["id"] for domain in data.get("domains", [])}
    if len(domain_ids) != len(data.get("domains", [])):
        fail("Tekrarlanan domain id bulundu.")

    for project in data.get("projects", []):
        if project.get("domainId") not in domain_ids:
            fail(f"Gecersiz domainId: {project.get('name')}")
        trl = project.get("trl")
        if not isinstance(trl, int) or not 1 <= trl <= 9:
            fail(f"Gecersiz TRL degeri: {project.get('name')} -> {trl}")
        source = (DOCS_ROOT / project["source"]).resolve()
        if not source.exists():
            fail(f"Proje kaynak baglantisi bulunamadi: {project['source']}")

    for platform in data.get("platforms", []):
        source = (DOCS_ROOT / platform["source"]).resolve()
        if not source.exists():
            fail(f"Platform kaynak baglantisi bulunamadi: {platform['source']}")


def validate_markdown_links() -> None:
    missing: list[str] = []
    for md_file in MARKDOWN_FILES:
        if not md_file.exists():
            continue
        content = md_file.read_text(encoding="utf-8", errors="replace")
        content = FENCE_RE.sub("", content)
        for match in LINK_RE.finditer(content):
            raw_target = match.group(1).split("#", 1)[0].strip()
            if not raw_target:
                continue
            target = (md_file.parent / unquote(raw_target)).resolve()
            if not str(target).startswith(str(ROOT.resolve())):
                missing.append(f"{md_file.relative_to(ROOT)} -> repo disi hedef: {raw_target}")
            elif not target.exists():
                missing.append(f"{md_file.relative_to(ROOT)} -> eksik hedef: {raw_target}")

    if missing:
        fail("Markdown baglanti hatalari:\n" + "\n".join(missing))


def main() -> int:
    data = load_data()
    validate_project_data(data)
    validate_markdown_links()
    print("[OK] TRL verisi ve Markdown baglantilari dogrulandi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
