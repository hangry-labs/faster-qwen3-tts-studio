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


def notice_name(path: str) -> bool:
    parts = PurePosixPath(path.replace("\\", "/")).parts
    base = parts[-1].lower() if parts else ""
    return any(word in base for word in ("license", "licence", "copying", "copyright", "notice", "authors")) or "licenses" in (part.lower() for part in parts)


def save_notice(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def collect_python(output: Path) -> list[dict]:
    records = []
    for dist in sorted(metadata.distributions(), key=lambda value: (value.metadata.get("Name") or "").lower()):
        name = dist.metadata.get("Name", "UNNAMED")
        slug = re.sub(r"[^a-zA-Z0-9_.-]", "_", name + "-" + dist.version)
        notices = []
        native = []
        for entry in dist.files or ():
            relative = PurePosixPath(str(entry).replace("\\", "/"))
            if str(relative).lower().endswith((".so", ".dll", ".dylib", ".pyd")):
                native.append(str(relative))
            if not notice_name(str(relative)):
                continue
            source = Path(dist.locate_file(entry))
            if not source.is_file():
                continue
            # Keep RECORD-relative identity without allowing ../../ to escape.
            safe = Path(*(re.sub(r"[^a-zA-Z0-9_.-]", "_", part)
                          for part in relative.parts if part not in {"..", ".", "/"}))
            destination = output / "python" / slug / safe
            sha = save_notice(source, destination)
            notices.append({"file": destination.relative_to(output).as_posix(), "sha256": sha})
        records.append({
            "name": name, "version": dist.version,
            "declared_license": dist.metadata.get("License-Expression") or dist.metadata.get("License") or "",
            "license_classifiers": [value for value in dist.metadata.get_all("Classifier", []) if value.startswith("License ::")],
            "declared_license_files": dist.metadata.get_all("License-File", []),
            "notices": notices, "native_members": native,
            "review_required": not bool(notices),
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
