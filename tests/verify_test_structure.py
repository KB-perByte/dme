#!/usr/bin/env python3
"""
Test structure verification script for Cisco DME Collection.
This script verifies that all test files have unique names and can be imported without conflicts.
"""

import os
import sys
from pathlib import Path


def check_test_file_names():
    """Check that all test files have unique basenames."""
    test_files = []
    test_dir = Path(__file__).parent / "unit"

    for test_file in test_dir.rglob("test_*.py"):
        test_files.append(test_file.name)

    # Check for duplicates
    duplicates = []
    seen = set()
    for filename in test_files:
        if filename in seen:
            duplicates.append(filename)
        seen.add(filename)

    if duplicates:
        print(f"❌ Found duplicate test file names: {duplicates}")
        return False
    else:
        print(f"✅ All {len(test_files)} test files have unique names")
        return True


def list_test_files():
    """List all test files in the structure."""
    print("\n📁 Test File Structure:")
    test_dir = Path(__file__).parent / "unit"

    for test_file in sorted(test_dir.rglob("test_*.py")):
        relative_path = test_file.relative_to(Path(__file__).parent)
        print(f"   {relative_path}")


def check_imports():
    """Basic import check for key files."""
    print("\n🔍 Testing imports...")

    # Test that we can at least import the test modules without conflicts
    test_modules = [
        "conftest",
        "fixtures.dme_responses",
    ]

    # Add tests directory to path temporarily
    test_unit_dir = str(Path(__file__).parent / "unit")
    if test_unit_dir not in sys.path:
        sys.path.insert(0, test_unit_dir)

    try:
        for module in test_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError as e:
                print(f"   ⚠️  {module} - {e}")
    finally:
        # Clean up path
        if test_unit_dir in sys.path:
            sys.path.remove(test_unit_dir)


def main():
    """Main verification function."""
    print("🧪 Cisco DME Collection - Test Structure Verification")
    print("=" * 55)

    all_good = True

    # Check file names
    if not check_test_file_names():
        all_good = False

    # List structure
    list_test_files()

    # Check imports
    check_imports()

    print("\n" + "=" * 55)
    if all_good:
        print("✅ Test structure verification PASSED")
        print("\n💡 To run tests:")
        print("   pip install -r requirements.txt")
        print("   pytest unit/ -v")
    else:
        print("❌ Test structure verification FAILED")
        print("\n🔧 To fix issues:")
        print("   - Ensure all test files have unique names")
        print("   - Remove __pycache__ directories")
        print("   - Install required dependencies")

    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
