import json, sys
from pathlib import Path

REQUIRED_KEYS = {"ts", "level", "action"}


def check_line(i: int, line: str):
    try:
        obj = json.loads(line)
    except Exception as e:
        print(f"Line {i}: invalid JSON: {e}")
        return 1
    missing = REQUIRED_KEYS - obj.keys()
    if missing:
        print(f"Line {i}: missing keys: {missing}")
        return 1
    return 0


def main(path: str):
    p = Path(path)
    if not p.exists():
        print(f"No such file: {path}")
        return 1
    errors = 0
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        errors += check_line(i, line)
    if errors:
        print(f"Validation failed with {errors} issue(s)")
        return 1
    print("Logs look good.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "bot.log"))
