"""Collect actual installed Python and Debian notices without importing packages.

Run inside the final candidate image. This collector does not approve licenses
or supply missing corresponding source. Review every reported gap before release.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from importlib import metadata
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

SUPPLEMENTAL_APACHE = {('tokenizers', '0.22.2')}
SUPPLEMENTAL_BUNDLED = {('torch', '2.10.0+cu128')}


def supplemental_notice(name: str, version: str, document: Path) -> str:
    normalized = re.sub(r'[-_.]+', '-', name).lower()
    if (normalized, version) in SUPPLEMENTAL_APACHE | SUPPLEMENTAL_BUNDLED and document.is_file():
        listed_name = normalized
        row = rf'^\| {re.escape(listed_name)} {re.escape(version)} \|'
        if re.search(row, document.read_text(encoding='utf-8'), re.M):
            return 'THIRD_PARTY_NOTICES.md#supplemental-notices-for-installed-wheels'
    return ''


def notice_name(path: str) -> bool:
    parts = PurePosixPath(path.replace("\\", "/")).parts
    base = parts[-1].lower() if parts else ""
    return any(word in base for word in ("license", "licence", "copying", "copyright", "notice", "authors")) or "licenses" in (part.lower() for part in parts)


def native_name(path: str) -> bool:
    """Include versioned SONAMEs and static/device libraries carried by wheels."""
    name = PurePosixPath(path.replace("\\", "/")).name.lower()
    return bool(re.search(r"\.so(?:\.[0-9]+)*$", name)) or name.endswith(
        (".dll", ".dylib", ".pyd", ".a", ".cubin", ".fatbin"))


def native_file(path: Path, relative: str) -> bool:
    if native_name(relative):
        return True
    # Wheels also carry tools such as ptxas with no library extension.
    with path.open('rb') as stream:
        return stream.read(4) == b'\x7fELF'


def file_sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save_notice(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return file_sha256(destination)


def collect_python(output: Path) -> list[dict]:
    records = []
    supplement = Path(__file__).resolve().parents[1] / 'THIRD_PARTY_NOTICES.md'
    if supplement.is_file():
        save_notice(supplement, output / 'supplemental/THIRD_PARTY_NOTICES.md')
    for dist in sorted(metadata.distributions(), key=lambda value: (value.metadata.get("Name") or "").lower()):
        name = dist.metadata.get("Name", "UNNAMED")
        slug = re.sub(r"[^a-zA-Z0-9_.-]", "_", name + "-" + dist.version)
        notices = []
        native = []
        native_files = []
        for entry in dist.files or ():
            relative = PurePosixPath(str(entry).replace("\\", "/"))
            source = Path(dist.locate_file(entry))
            if not source.is_file():
                continue
            if native_file(source, str(relative)):
                native.append(str(relative))
                native_files.append({'file': str(relative), 'size': source.stat().st_size,
                                     'sha256': file_sha256(source)})
            if not notice_name(str(relative)):
                continue
            # Keep RECORD-relative identity without allowing ../../ to escape.
            safe = Path(*(re.sub(r"[^a-zA-Z0-9_.-]", "_", part)
                          for part in relative.parts if part not in {"..", ".", "/"}))
            destination = output / "python" / slug / safe
            sha = save_notice(source, destination)
            notices.append({"file": destination.relative_to(output).as_posix(), "sha256": sha})
        supplemental = supplemental_notice(name, dist.version, supplement)
        records.append({
            "name": name, "version": dist.version,
            "declared_license": dist.metadata.get("License-Expression") or dist.metadata.get("License") or "",
            "license_classifiers": [value for value in dist.metadata.get_all("Classifier", []) if value.startswith("License ::")],
            "declared_license_files": dist.metadata.get_all("License-File", []),
            "notices": notices, "native_members": native, "native_files": native_files,
            "supplemental_notice": supplemental,
            "review_required": not bool(notices or supplemental),
        })
    return records


def collect_debian(output: Path) -> list[dict]:
    executable = shutil.which("dpkg-query")
    if not executable:
        return []
    result = subprocess.run(
        [executable, "-W", "-f=${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n"],
        check=True, capture_output=True, text=True,
    )
    records = []
    for line in result.stdout.splitlines():
        package, version, source_package, source_version = line.split("\t")
        copyright_file = Path("/usr/share/doc") / package.split(":")[0] / "copyright"
        target = output / "debian" / package.replace(":", "_") / "copyright"
        sha = save_notice(copyright_file, target) if copyright_file.is_file() else ""
        records.append({"package": package, "version": version,
                        "source_package": source_package or package, "source_version": source_version or version,
                        "copyright_sha256": sha, "review_required": not bool(sha)})
    common = Path("/usr/share/common-licenses")
    if common.is_dir():
        shutil.copytree(common, output / "common-licenses", dirs_exist_ok=True)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Output must be empty so stale notices cannot mask missing current evidence")
    output.mkdir(parents=True, exist_ok=True)
    python_records = collect_python(output)
    debian_records = collect_debian(output)
    for candidate in (Path(sys.prefix) / "LICENSE.txt", Path(sys.base_prefix) / "LICENSE.txt",
                      Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "LICENSE.txt"):
        if candidate.is_file():
            save_notice(candidate, output / "python-runtime" / "LICENSE.txt")
            break
    inventory = {"python_version": sys.version.split()[0], "python_packages": python_records,
                 "debian_packages": debian_records, "legal_approval": False}
    (output / "inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    with (output / "debian-source-identities.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_package", "source_version"], delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(debian_records)
    gaps = sum(record["review_required"] for record in python_records + debian_records)
    print(f"Collected {len(python_records)} Python and {len(debian_records)} Debian records; {gaps} missing-notice review items.")
    print("Inspect NVIDIA/runtime payloads and supply exact corresponding source before redistribution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
