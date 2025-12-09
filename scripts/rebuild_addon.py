from __future__ import annotations

from scripts.package_addon import package_addon, ADDON_NAME


def main() -> None:
    zip_path = package_addon()
    print("\nAddon packaged.")
    print(f"Location: {zip_path}")
    print("Next steps:")
    print("1) Open Blender > Preferences > Add-ons.")
    print("2) Click 'Install...', choose the zip above.")
    print("3) Enable the addon (MCP Blender Bridge).")
    print("Optional: run purge script first if you want a clean reinstall:")
    print("   python scripts/purge_installed_addon.py --dry-run")


if __name__ == "__main__":
    main()
