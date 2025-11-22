#!/usr/bin/env python3
"""
Health Check System for PDFTools

Validates installation by checking:
- Python modules can be imported
- PDFTools modules are accessible
- Test data exists
- Docker is available
- Docker OCR image is present
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import logging
import importlib
import subprocess
import sys

logger = logging.getLogger('pdftools.health_check')


@dataclass
class HealthCheckResult:
    """Result of a single health check"""
    name: str
    success: bool
    message: str
    details: Dict[str, str]


@dataclass
class HealthReport:
    """Complete health check report"""
    timestamp: str
    overall_success: bool
    checks: List[HealthCheckResult]

    def __str__(self) -> str:
        """Format report as string"""
        lines = [
            "=" * 60,
            "PDFTools Health Check Report",
            f"Timestamp: {self.timestamp}",
            "=" * 60,
            ""
        ]

        for check in self.checks:
            status = "✓ PASS" if check.success else "✗ FAIL"
            lines.append(f"{status} - {check.name}")
            lines.append(f"    {check.message}")

            if check.details:
                for key, value in check.details.items():
                    lines.append(f"    {key}: {value}")
            lines.append("")

        lines.append("=" * 60)
        lines.append(f"Overall Result: {'✓ PASSED' if self.overall_success else '✗ FAILED'}")
        lines.append("=" * 60)

        return "\n".join(lines)


class HealthChecker:
    """Performs post-installation health checks"""

    def __init__(self):
        self.results: List[HealthCheckResult] = []

    def check_python_imports(self) -> HealthCheckResult:
        """Check that all required Python modules can be imported"""
        required_modules = [
            "PyPDF2",
            "PIL",  # Pillow
            "pdf2image",
            "pytest",
        ]

        failed_imports = []

        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
                logger.debug(f"✓ Successfully imported {module_name}")
            except ImportError as e:
                logger.error(f"✗ Failed to import {module_name}: {e}")
                failed_imports.append(module_name)

        if failed_imports:
            return HealthCheckResult(
                name="Python Imports",
                success=False,
                message=f"Failed to import: {', '.join(failed_imports)}",
                details={}
            )
        else:
            return HealthCheckResult(
                name="Python Imports",
                success=True,
                message=f"All {len(required_modules)} required modules importable",
                details={"modules": ", ".join(required_modules)}
            )

    def check_pdftools_modules(self) -> HealthCheckResult:
        """Check that pdftools modules are accessible"""
        try:
            # Add src to path if not already there
            src_path = Path(__file__).parent.parent / "src"
            if src_path.exists() and str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))

            # Try importing main modules
            from pdftools.merge import merge_pdfs
            from pdftools.core.exceptions import PDFToolsError

            return HealthCheckResult(
                name="PDFTools Modules",
                success=True,
                message="PDFTools modules accessible",
                details={"merge_module": "OK"}
            )
        except ImportError as e:
            return HealthCheckResult(
                name="PDFTools Modules",
                success=False,
                message=f"Failed to import pdftools modules: {e}",
                details={}
            )

    def check_test_data(self) -> HealthCheckResult:
        """Check that test PDFs exist"""
        test_data_dir = Path("tests/test_data")

        if not test_data_dir.exists():
            return HealthCheckResult(
                name="Test Data",
                success=False,
                message=f"Test data directory not found: {test_data_dir}",
                details={}
            )

        pdf_files = list(test_data_dir.glob("*.pdf"))

        if len(pdf_files) == 0:
            return HealthCheckResult(
                name="Test Data",
                success=False,
                message="No test PDF files found",
                details={"directory": str(test_data_dir)}
            )

        return HealthCheckResult(
            name="Test Data",
            success=True,
            message=f"Found {len(pdf_files)} test PDF files",
            details={"directory": str(test_data_dir), "count": str(len(pdf_files))}
        )

    def check_docker(self) -> HealthCheckResult:
        """Check Docker availability"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                check=True,
                capture_output=True,
                text=True
            )

            return HealthCheckResult(
                name="Docker",
                success=True,
                message="Docker is available",
                details={"version": result.stdout.strip()}
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return HealthCheckResult(
                name="Docker",
                success=False,
                message="Docker not available (OCR features disabled)",
                details={"note": "Install Docker to enable OCR"}
            )

    def check_docker_ocr(self) -> HealthCheckResult:
        """Check Docker OCR image"""
        try:
            result = subprocess.run(
                ["docker", "images", "jbarlow83/ocrmypdf", "--format", "{{.Tag}}"],
                check=True,
                capture_output=True,
                text=True
            )

            tags = result.stdout.strip().split("\n")
            if tags and tags[0]:
                return HealthCheckResult(
                    name="Docker OCR Image",
                    success=True,
                    message="OCR Docker image found",
                    details={"tags": ", ".join(tags)}
                )
            else:
                return HealthCheckResult(
                    name="Docker OCR Image",
                    success=False,
                    message="OCR Docker image not found",
                    details={"hint": "Run: docker pull jbarlow83/ocrmypdf:v14.4.0"}
                )

        except (subprocess.CalledProcessError, FileNotFoundError):
            return HealthCheckResult(
                name="Docker OCR Image",
                success=False,
                message="Cannot check Docker images",
                details={}
            )

    def run_all_checks(self) -> HealthReport:
        """Run all health checks and generate report"""
        logger.info("Running health checks...")

        self.results = [
            self.check_python_imports(),
            self.check_pdftools_modules(),
            self.check_test_data(),
            self.check_docker(),
            self.check_docker_ocr(),
        ]

        overall_success = all(check.success for check in self.results)

        return HealthReport(
            timestamp=datetime.now().isoformat(),
            overall_success=overall_success,
            checks=self.results
        )


def main():
    """Main entry point for health check"""
    import argparse

    parser = argparse.ArgumentParser(description='PDFTools Health Check')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--output', type=Path, help='Write report to file')

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Run health checks
    checker = HealthChecker()
    report = checker.run_all_checks()

    # Print report
    print(report)

    # Write to file if specified
    if args.output:
        args.output.write_text(str(report))
        print(f"\nReport written to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if report.overall_success else 7)


if __name__ == '__main__':
    main()
