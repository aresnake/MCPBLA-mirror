from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ADDON_NAME = "mcp_blender_addon"


def package_addon() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    addon_src = repo_root / "src" / "mcpbla" / "blender" / "addon"
    if not addon_src.exists():
        raise FileNotFoundError(f"Addon source not found at {addon_src}")

    dist_dir = repo_root / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    zip_path = dist_dir / f"{ADDON_NAME}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in addon_src.rglob("*"):
            if path.is_dir():
                continue
            arcname = Path(ADDON_NAME) / path.relative_to(addon_src)
            zipf.write(path, arcname)
            print(f"Added {arcname}")

    print(f"Packaged addon to {zip_path}")
    return zip_path


def main() -> None:
    argparse.ArgumentParser(description="Package Blender addon into a ZIP").parse_args()
    package_addon()


if __name__ == "__main__":
    main()
