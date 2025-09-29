#!/usr/bin/env python3
import os
import sys
import zipfile


def main(dest_name: str = "Vikram_binance_bot_assignment.zip") -> None:
    # Project root (one level up from this script)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    exclude_dirs = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".vscode"}
    exclude_files = {".env"}
    exclude_exts = {".pyc", ".pyo"}
    reserved_names = {"CON", "PRN", "AUX", "NUL",
                      "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                      "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}

    dest_path = os.path.join(root, dest_name)
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(root):
            rel = os.path.relpath(folder, root)
            # Skip excluded directories anywhere in the path
            if rel != "." and any(part in exclude_dirs for part in rel.split(os.sep)):
                continue
            # Prune excluded dirs in-place to avoid walking them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                if f in exclude_files:
                    continue
                base, ext = os.path.splitext(f)
                # Skip reserved device names (case-insensitive)
                if f.upper() in reserved_names or base.upper() in reserved_names:
                    continue
                if ext in exclude_exts:
                    continue
                full = os.path.join(folder, f)
                arc = os.path.relpath(full, root)
                z.write(full, arc)
    print(f"Created {dest_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Vikram_binance_bot_assignment.zip"
    main(out)
