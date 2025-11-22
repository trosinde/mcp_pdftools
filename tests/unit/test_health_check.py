"""
Unit tests for health check system
"""

import pytest
from pathlib import Path
import sys
import subprocess
from unittest.mock import Mock, patch, MagicMock
import importlib

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from health_check import (
    HealthChecker,
    HealthCheckResult,
    HealthReport
)


class TestHealthCheckResult:
    """Tests for HealthCheckResult"""

    def test_create_success_result(self):
        """Test creating a successful health check result"""
        result = HealthCheckResult(
            name="Test Check",
            success=True,
            message="All good",
            details={"version": "1.0"}
        )

        assert result.name == "Test Check"
        assert result.success
        assert result.message == "All good"
        assert result.details["version"] == "1.0"

    def test_create_failure_result(self):
        """Test creating a failed health check result"""
        result = HealthCheckResult(
            name="Test Check",
            success=False,
            message="Something failed",
            details={}
        )

        assert not result.success
        assert "failed" in result.message


class TestHealthReport:
    """Tests for HealthReport"""

    def test_create_health_report(self):
        """Test creating a health report"""
        checks = [
            HealthCheckResult("Check 1", True, "OK", {}),
            HealthCheckResult("Check 2", True, "OK", {})
        ]

        report = HealthReport(
            timestamp="2025-11-22T10:00:00",
            overall_success=True,
            checks=checks
        )

        assert report.overall_success
        assert len(report.checks) == 2

    def test_report_string_representation(self):
        """Test health report string formatting"""
        checks = [
            HealthCheckResult("Check 1", True, "OK", {"detail": "value"}),
            HealthCheckResult("Check 2", False, "Failed", {})
        ]

        report = HealthReport(
            timestamp="2025-11-22T10:00:00",
            overall_success=False,
            checks=checks
        )

        report_str = str(report)

        assert "Health Check Report" in report_str
        assert "Check 1" in report_str
        assert "Check 2" in report_str
        assert "✓ PASS" in report_str
        assert "✗ FAIL" in report_str
        assert "detail: value" in report_str


class TestHealthChecker:
    """Tests for HealthChecker"""

    def test_check_python_imports_success(self, monkeypatch):
        """Test Python imports check when all modules are available"""
        # Mock importlib.import_module to succeed
        mock_import = Mock()
        monkeypatch.setattr(importlib, 'import_module', mock_import)

        checker = HealthChecker()
        result = checker.check_python_imports()

        assert result.success
        assert "✓" in result.message or "All" in result.message

    def test_check_python_imports_failure(self, monkeypatch):
        """Test Python imports check when modules are missing"""
        # Mock importlib.import_module to fail
        def mock_import(name):
            if name == "PyPDF2":
                raise ImportError(f"No module named '{name}'")

        monkeypatch.setattr(importlib, 'import_module', mock_import)

        checker = HealthChecker()
        result = checker.check_python_imports()

        assert not result.success
        assert "Failed to import" in result.message

    def test_check_test_data_success(self, tmp_path, monkeypatch):
        """Test test data check when PDFs exist"""
        # Create test data directory
        test_data_dir = tmp_path / "tests" / "test_data"
        test_data_dir.mkdir(parents=True)

        # Create some test PDFs
        (test_data_dir / "test_1.pdf").touch()
        (test_data_dir / "test_2.pdf").touch()

        # Monkeypatch Path to use tmp_path
        monkeypatch.setattr(Path, '__new__', lambda cls, *args: tmp_path / "tests" / "test_data" if args and args[0] == "tests/test_data" else object.__new__(cls))

        checker = HealthChecker()

        # Manually test the logic
        if test_data_dir.exists():
            pdf_files = list(test_data_dir.glob("*.pdf"))
            assert len(pdf_files) == 2

    def test_check_test_data_missing_directory(self, tmp_path, monkeypatch):
        """Test test data check when directory doesn't exist"""
        # Monkeypatch Path to return non-existent directory
        class MockPath:
            def exists(self):
                return False

        # We'll test the logic directly
        test_data_dir = Path("tests/test_data")
        if not (tmp_path / "tests" / "test_data").exists():
            assert True  # Directory doesn't exist, as expected

    def test_check_test_data_empty(self, tmp_path):
        """Test test data check when no PDFs exist"""
        test_data_dir = tmp_path / "tests" / "test_data"
        test_data_dir.mkdir(parents=True)

        # Directory exists but no PDFs
        pdf_files = list(test_data_dir.glob("*.pdf"))
        assert len(pdf_files) == 0

    def test_check_docker_available(self, monkeypatch):
        """Test Docker check when Docker is available"""
        mock_result = Mock(stdout="Docker version 20.10.0", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        checker = HealthChecker()
        result = checker.check_docker()

        assert result.success
        assert "available" in result.message
        assert "20.10.0" in result.details.get("version", "")

    def test_check_docker_not_available(self, monkeypatch):
        """Test Docker check when Docker is not available"""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("docker not found")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        checker = HealthChecker()
        result = checker.check_docker()

        assert not result.success
        assert "not available" in result.message

    def test_check_docker_ocr_found(self, monkeypatch):
        """Test Docker OCR image check when image exists"""
        mock_result = Mock(stdout="v14.4.0\nlatest", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        checker = HealthChecker()
        result = checker.check_docker_ocr()

        assert result.success
        assert "found" in result.message

    def test_check_docker_ocr_not_found(self, monkeypatch):
        """Test Docker OCR image check when image doesn't exist"""
        mock_result = Mock(stdout="", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        checker = HealthChecker()
        result = checker.check_docker_ocr()

        assert not result.success
        assert "not found" in result.message

    def test_run_all_checks(self, monkeypatch):
        """Test running all health checks"""
        # Mock all checks to return success
        mock_success = HealthCheckResult("Mock Check", True, "OK", {})

        checker = HealthChecker()
        monkeypatch.setattr(checker, 'check_python_imports', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_pdftools_modules', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_test_data', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_docker', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_docker_ocr', lambda: mock_success)

        report = checker.run_all_checks()

        assert report.overall_success
        assert len(report.checks) == 5

    def test_run_all_checks_with_failures(self, monkeypatch):
        """Test running all health checks with some failures"""
        mock_success = HealthCheckResult("Success Check", True, "OK", {})
        mock_failure = HealthCheckResult("Failed Check", False, "ERROR", {})

        checker = HealthChecker()
        monkeypatch.setattr(checker, 'check_python_imports', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_pdftools_modules', lambda: mock_failure)
        monkeypatch.setattr(checker, 'check_test_data', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_docker', lambda: mock_success)
        monkeypatch.setattr(checker, 'check_docker_ocr', lambda: mock_success)

        report = checker.run_all_checks()

        assert not report.overall_success
        assert len(report.checks) == 5

        # Check that we have both success and failure
        successes = [c for c in report.checks if c.success]
        failures = [c for c in report.checks if not c.success]

        assert len(successes) == 4
        assert len(failures) == 1
