#!/usr/bin/env python3
"""Post-installation functional tests for mcp_pdftools.

This script verifies that all PDF tools are correctly installed
and can perform basic operations.

Version: 1.0
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple


class TestResult:
    """Represents the result of a single test."""

    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        msg = f"\n         {self.message}" if self.message else ""
        return f"{status}: {self.name}{msg}"


def run_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Run command and return success status and output.

    Args:
        cmd: Command and arguments as list
        timeout: Timeout in seconds

    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def test_cli_tool_version(tool_name: str) -> TestResult:
    """Test that CLI tool responds to --version.

    Args:
        tool_name: Name of CLI tool

    Returns:
        TestResult indicating success or failure
    """
    success, output = run_command([tool_name, "--version"])
    if success:
        version = output.strip().split('\n')[0] if output else "unknown"
        return TestResult(
            f"{tool_name} --version",
            True,
            version
        )
    else:
        return TestResult(
            f"{tool_name} --version",
            False,
            f"Failed: {output[:100]}"
        )


def test_cli_tool_help(tool_name: str) -> TestResult:
    """Test that CLI tool responds to --help.

    Args:
        tool_name: Name of CLI tool

    Returns:
        TestResult indicating success or failure
    """
    success, output = run_command([tool_name, "--help"])
    if success and len(output) > 0:
        return TestResult(
            f"{tool_name} --help",
            True,
            "Help displayed successfully"
        )
    else:
        return TestResult(
            f"{tool_name} --help",
            False,
            f"Failed: {output[:100] if output else 'No output'}"
        )


def test_python_imports() -> TestResult:
    """Test that all Python modules can be imported.

    Returns:
        TestResult indicating success or failure
    """
    modules = [
        "pdftools",
        "pdftools.merge",
        "pdftools.split",
        "pdftools.ocr",
        "pdftools.protection",
        "pdftools.text_extraction",
        "pdftools.thumbnails",
        "pdftools.renaming",
    ]

    failed_imports = []
    for module in modules:
        try:
            __import__(module)
        except Exception as e:
            failed_imports.append(f"{module}: {e}")

    if not failed_imports:
        return TestResult(
            "Python module imports",
            True,
            f"All {len(modules)} modules imported successfully"
        )
    else:
        return TestResult(
            "Python module imports",
            False,
            "Failed imports:\n" + "\n".join(failed_imports)
        )


def test_docker_accessible() -> TestResult:
    """Test that Docker is accessible.

    Returns:
        TestResult indicating success or failure
    """
    success, output = run_command(["docker", "ps"])
    if success:
        return TestResult(
            "Docker accessibility",
            True,
            "Docker daemon is running"
        )
    else:
        return TestResult(
            "Docker accessibility",
            False,
            f"Docker not accessible: {output[:100]}"
        )


def test_pdftools_version() -> TestResult:
    """Test that pdftools package has a version.

    Returns:
        TestResult indicating success or failure
    """
    try:
        import pdftools
        version = pdftools.__version__
        return TestResult(
            "pdftools package version",
            True,
            f"Version: {version}"
        )
    except Exception as e:
        return TestResult(
            "pdftools package version",
            False,
            str(e)
        )


def test_virtual_environment() -> TestResult:
    """Test that we're running in a virtual environment.

    Returns:
        TestResult indicating success or failure
    """
    import os
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        return TestResult(
            "Virtual environment",
            True,
            f"Running in venv: {venv}"
        )
    else:
        return TestResult(
            "Virtual environment",
            False,
            "Not running in a virtual environment"
        )


def main():
    """Run all post-installation tests."""
    print("=" * 60)
    print("Running Post-Installation Functional Tests")
    print("=" * 60)
    print()

    results: List[TestResult] = []

    # Test 1: Virtual environment
    print("Test 1: Virtual Environment...")
    results.append(test_virtual_environment())

    # Test 2: Python module imports
    print("Test 2: Python Module Imports...")
    results.append(test_python_imports())

    # Test 3: pdftools version
    print("Test 3: PDFTools Package Version...")
    results.append(test_pdftools_version())

    # Test 4-10: CLI tools --version
    cli_tools = [
        "pdfmerge",
        "pdfsplit",
        "ocrutil",
        "pdfgettxt",
        "pdfprotect",
        "pdfthumbnails",
        "pdfrename",
    ]

    for i, tool in enumerate(cli_tools, start=4):
        print(f"Test {i}: {tool} --version...")
        results.append(test_cli_tool_version(tool))

    # Test 11-17: CLI tools --help
    for i, tool in enumerate(cli_tools, start=11):
        print(f"Test {i}: {tool} --help...")
        results.append(test_cli_tool_help(tool))

    # Test 18: Docker
    print("Test 18: Docker Accessibility...")
    results.append(test_docker_accessible())

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print()

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    for result in results:
        print(result)

    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    # Write report to file
    report_file = Path.home() / ".mcp_pdftools" / "installation_test_report.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w") as f:
        f.write("Post-Installation Test Report\n")
        f.write("=" * 60 + "\n\n")

        for result in results:
            status = "PASS" if result.passed else "FAIL"
            f.write(f"{status}: {result.name}\n")
            if result.message:
                f.write(f"  {result.message}\n")
            f.write("\n")

        f.write(f"Total: {len(results)}, Passed: {passed}, Failed: {failed}\n")

    print(f"Test report saved to: {report_file}")
    print()

    # Exit with appropriate code
    if failed == 0:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"✗ {failed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
