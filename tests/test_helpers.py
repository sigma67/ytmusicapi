import os


def is_ci() -> bool:
    return "GITHUB_ACTIONS" in os.environ
