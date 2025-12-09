from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Iterable, List


ADDON_NAME = "addon"  # Will be replaced in main based on source folder


def find_addon_paths(base_blender_dir: Path, addon_name: str) -> Iterable[Path]:
    if not base_blender_dir.exists():
        return []
    for version_dir in base_blender_dir.iterdir():
        if not version_dir.is_dir():
            continue
        addons_dir = version_dir / "scripts" / "addons"
        if addons_dir.exists():
            target_dir = addons_dir / addon_name
            target_zip = addons_dir / f"{addon_name}.zip"
            if target_dir.exists():
                yield target_dir
            if target_zip.exists():
                yield target_zip


def purge_targets(targets: List[Path], dry_run: bool) -> None:
    action = "Would remove" if dry_run else "Removing"
    for target in targets:
        print(f"{action}: {target}")
        if dry_run:
            continue
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            target.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Purge installed copies of the addon from Blender addons folders.")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be removed.")
    parser.add_argument(
        "--extra-path",
        action="append",
        help="Optional extra addons directory to clean (e.g. portable builds). Can be passed multiple times.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    addon_src = repo_root / "blender" / "addon"
    addon_name = addon_src.name

    appdata = os.environ.get("APPDATA")
    targets: List[Path] = []

    if appdata:
        base = Path(appdata) / "Blender Foundation" / "Blender"
        targets.extend(find_addon_paths(base, addon_name))
    else:
        print("APPDATA not set; skipping default Blender paths.")

    if args.extra_path:
        for extra in args.extra_path:
            extra_path = Path(extra)
            if extra_path.exists():
                target_dir = extra_path / addon_name
                target_zip = extra_path / f"{addon_name}.zip"
                if target_dir.exists():
                    targets.append(target_dir)
                if target_zip.exists():
                    targets.append(target_zip)

    if not targets:
        print("No installed addon copies found.")
        return

    purge_targets(targets, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
