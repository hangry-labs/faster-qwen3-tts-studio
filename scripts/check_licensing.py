"""Check consolidated notices and Python distribution contents offline.

This validates notice preservation, not legal interpretation or a runtime image.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import tarfile
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
LICENSE_FILES = ("LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md")
REQUIRED = (*LICENSE_FILES, "docs/LICENSING.md")
LICENSE_EXPRESSION = "MIT AND Apache-2.0"
# SHA-256 of the original upstream texts, with LF newlines and outer whitespace
# removed. Keep the copyright, grant, and disclaimer intact when editing prose.
LICENSE_TEXT_HASHES = {
    "nano-parakeet MIT notice": "717aa5a6795bbd1367dbbf33c11e238a2923e379231de7a8b42c1bdae5f57af3",
    "nano-qwen3tts-vllm MIT notice": "cad241ce93ea8cf56730f2b9ca37950d8a11d845cfb0fb9d1b3a3ebbbd285435",
    "qwentts-cpp-python MIT notice": "494d421b44f446c54097a4df290728144d644b8e0b6b451063bcc4cae03d5a3c",
    "qwentts.cpp MIT notice": "557951720fe81d864f320e83c8d3fd1ba2a4a2af5cfcee5be1c504ab8878b3eb",
    "ggml MIT notice": "3468798dd4eb1badf2d665d4afec49d424aa31fd4f0af91638ccd4b1a48615d0",
    "cpp-httplib MIT notice": "d260e6eaf487837d051bb6dbb9bba4715e354470ba7d2db1e102aa8a75302041",
    "Apache-2.0 license text": "f843da8c75d96e7303bc6dc92ebf88926921d16d6bd3b8c04d8cbe3de810821f",
}


def check_notice_text(text: str) -> list[str]:
    text = text.replace("\r\n", "\n")
    errors = []
    for heading, expected in LICENSE_TEXT_HASHES.items():
        blocks = re.findall(r"^### " + re.escape(heading) + r"\n\n```text\n(.*?)\n```", text, re.M | re.S)
        if len(blocks) != 1:
            errors.append(f"Consolidated notices need exactly one license block: {heading}")
        elif hashlib.sha256(blocks[0].strip().encode("utf-8")).hexdigest() != expected:
            errors.append(f"Original license text changed: {heading}")
    return errors


def check_source(root: Path) -> list[str]:
    errors = []
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f"Missing required notice/document: {name}")
    if errors:
        return errors
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    if metadata["project"]["license"] != LICENSE_EXPRESSION:
        errors.append("Package metadata must retain MIT and Apache-2.0 obligations")
    if set(metadata["project"]["license-files"]) != set(LICENSE_FILES):
        errors.append("Package license files must include the three consolidated notice files")
    errors.extend(check_notice_text((root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")))
    for name in ("THIRD_PARTY_NOTICES.md", "docs/LICENSING.md"):
        document = root / name
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            if not (document.parent / target.split("#", 1)[0]).exists():
                errors.append(f"Broken licensing document link in {name}: {target}")
    return errors


def check_artifact(path: Path) -> list[str]:
    errors = []
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                errors.append("Wheel must contain exactly one distribution metadata record")
            elif f"License-Expression: {LICENSE_EXPRESSION}" not in archive.read(metadata_names[0]).decode("utf-8"):
                errors.append("Wheel license metadata dropped mixed-source obligations")
            for name in LICENSE_FILES:
                matches = [member for member in names if member.endswith(".dist-info/licenses/" + name)]
                if len(matches) != 1:
                    errors.append(f"Wheel missing license material or has duplicates: {name}")
                elif name == "THIRD_PARTY_NOTICES.md":
                    errors.extend(check_notice_text(archive.read(matches[0]).decode("utf-8")))
    else:
        with tarfile.open(path) as archive:
            names = [member.name for member in archive.getmembers() if member.isfile()]
            roots = {PurePosixPath(member).parts[0] for member in names}
            if len(roots) != 1:
                errors.append('Source archive must contain one package root')
            prefix = next(iter(roots), '') + '/'
            for name in REQUIRED:
                matches = [member for member in names if member == prefix + name]
                if len(matches) != 1:
                    errors.append(f"Source archive missing licensing material or has duplicates: {name}")
                elif name == "THIRD_PARTY_NOTICES.md":
                    with archive.extractfile(matches[0]) as stream:
                        errors.extend(check_notice_text(stream.read().decode("utf-8")))
    for name in names:
        parts = PurePosixPath(name).parts
        if any(part in {".ai", ".idea", "AGENTS.md"} for part in parts):
            errors.append(f"Private material in distribution: {name}")
        if name.lower().endswith((".wav", ".mp3", ".safetensors", ".gguf")):
            errors.append(f"Unqualified media/model payload in Python distribution: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--artifact", action="append", type=Path, default=[])
    args = parser.parse_args()
    errors = check_source(args.root)
    for artifact in args.artifact:
        errors.extend(check_artifact(artifact))
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: consolidated source notices and requested Python artifacts")
    print("Release images require their own exact installed/native/source review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
