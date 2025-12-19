#!/usr/bin/env python3
"""Development environment checker.

Verifies that all required development tools are installed and configured properly.
"""

import subprocess
import sys
from pathlib import Path


def check_command(cmd: str, version_arg: str = "--version") -> bool:
    """Check if a command is available."""
    try:
        result = subprocess.run(
            [cmd, version_arg],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_file(path: Path) -> bool:
    """Check if a file exists."""
    return path.exists()


def main() -> int:
    """Run all checks."""
    print("Checking development environment...\n")
    
    repo_root = Path(__file__).parent.parent
    checks = []
    
    # Python version
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    checks.append(("Python >= 3.10", py_ok))
    print(f"{'✓' if py_ok else '✗'} Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    # PDM
    pdm_ok = check_command("pdm")
    checks.append(("PDM", pdm_ok))
    print(f"{'✓' if pdm_ok else '✗'} PDM installed")
    
    # Pre-commit
    precommit_ok = check_command("pre-commit")
    checks.append(("Pre-commit", precommit_ok))
    print(f"{'✓' if precommit_ok else '✗'} Pre-commit installed")
    
    # Git hooks
    hooks_ok = check_file(repo_root / ".git" / "hooks" / "pre-commit")
    checks.append(("Git hooks", hooks_ok))
    print(f"{'✓' if hooks_ok else '✗'} Git hooks configured")
    
    # Configuration files
    editorconfig_ok = check_file(repo_root / ".editorconfig")
    checks.append((".editorconfig", editorconfig_ok))
    print(f"{'✓' if editorconfig_ok else '✗'} .editorconfig present")
    
    makefile_ok = check_file(repo_root / "Makefile")
    checks.append(("Makefile", makefile_ok))
    print(f"{'✓' if makefile_ok else '✗'} Makefile present")
    
    print("\n" + "=" * 50)
    
    all_ok = all(result for _, result in checks)
    if all_ok:
        print("✓ All checks passed!")
        return 0
    else:
        failed = [name for name, result in checks if not result]
        print(f"✗ Failed checks: {', '.join(failed)}")
        print("\nTo fix:")
        if not pdm_ok:
            print("  - Install PDM: pip install pdm")
        if not precommit_ok:
            print("  - Install pre-commit: pip install pre-commit")
        if not hooks_ok:
            print("  - Setup git hooks: pre-commit install")
        return 1


if __name__ == "__main__":
    sys.exit(main())
