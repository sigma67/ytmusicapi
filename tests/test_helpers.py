import os


def is_ci() -> bool:
    return "CI" in os.environ
