import subprocess
import sys


def _run(cmd: list[str], label: str) -> int:
    result = subprocess.run(cmd)
    status = "OK" if result.returncode == 0 else "FAILED"
    print(f"── {label} {'─' * (68 - len(label))} {status}")
    return result.returncode


def main() -> None:
    src = "src/tvbox_config"

    exit_code = 0

    exit_code |= _run(["ruff", "check", src], "ruff check")
    exit_code |= _run(["ruff", "format", "--check", src], "ruff format")
    exit_code |= _run(["ty", "check", "--error", "all", src], "ty check")

    sys.exit(exit_code)
