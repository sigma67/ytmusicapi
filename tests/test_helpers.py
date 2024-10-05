import os


def is_ci() -> bool:
    return bool(os.environ.get("CI", False))
