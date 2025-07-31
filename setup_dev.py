#!/usr/bin/env python3
"""
Setup script for development environment
Run this script to set up pre-commit hooks and formatting tools
"""

import os
import subprocess
import sys


def run_command(command: str, description: str) -> bool:
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        _ = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main() -> None:
    print("🚀 Setting up development environment for the-fetus project")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists("requirements-dev.txt"):
        print(
            "❌ requirements-dev.txt not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Install requirements
    if not run_command(
        "pip install -r requirements-dev.txt", "Installing development dependencies"
    ):
        sys.exit(1)

    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        sys.exit(1)

    # Run pre-commit on all files (optional - to see current state)
    print("\n🔍 Running pre-commit checks on all files to see current state...")
    subprocess.run("pre-commit run --all-files", shell=True)

    print("\n" + "=" * 60)
    print("🎉 Development environment setup complete!")
    print("\n📝 What's been set up:")
    print("   • Pre-commit hooks installed")
    print("   • Black code formatter configured")
    print("   • isort import sorter configured")
    print("   • flake8 linter configured")
    print("   • mypy type checker configured")
    print("\n🔧 Usage:")
    print("   • Code will be automatically formatted on commit")
    print("   • Run 'black .' to format all Python files manually")
    print("   • Run 'pre-commit run --all-files' to check all files")
    print("   • Run 'flake8' to lint your code")


if __name__ == "__main__":
    main()
