import subprocess
import sys
from typing import NoReturn


def lint() -> NoReturn:
    """執行 Ruff 檢查"""
    print("Running Ruff check...")
    result = subprocess.run(["ruff", "check", "."])
    sys.exit(result.returncode)


def format() -> NoReturn:
    """執行 Ruff 格式化"""
    print("Running Ruff format...")
    result = subprocess.run(["ruff", "format", "."])
    sys.exit(result.returncode)


def test() -> NoReturn:
    """執行 Pytest"""
    print("Running Pytest...")
    result = subprocess.run(["pytest"])
    sys.exit(result.returncode)


def type_check() -> NoReturn:
    """執行 Mypy 型別檢查"""
    print("Running Mypy...")
    result = subprocess.run(["mypy", "."])
    sys.exit(result.returncode)
