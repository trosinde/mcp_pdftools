"""
Installation Library for PDFTools

This module provides reusable installation functions for setting up
the PDFTools environment including virtualenv, dependencies, Docker, etc.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple
from enum import Enum
import json
import logging
import subprocess
import sys
import uuid
from datetime import datetime

logger = logging.getLogger('pdftools.install')


class InstallationStep(Enum):
    """Installation steps enumeration"""
    CHECK_PYTHON = "check_python"
    CREATE_VENV = "create_venv"
    INSTALL_DEPS = "install_deps"
    CHECK_DOCKER = "check_docker"
    PULL_DOCKER = "pull_docker"
    GENERATE_TEST_DATA = "generate_test_data"
    HEALTH_CHECK = "health_check"
    FINALIZE = "finalize"


@dataclass
class InstallationState:
    """Tracks installation progress for resume/rollback"""
    installation_id: str
    started_at: str
    completed_steps: List[str]
    current_step: Optional[str]
    failed: bool
    error_message: Optional[str]
    python_version: str
    venv_path: str
    docker_available: bool
    docker_image: Optional[str]

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'InstallationState':
        """Deserialize from JSON"""
        return cls(**json.loads(json_str))

    def mark_step_complete(self, step: InstallationStep):
        """Mark a step as completed"""
        self.completed_steps.append(step.value)

    def is_step_complete(self, step: InstallationStep) -> bool:
        """Check if step was already completed"""
        return step.value in self.completed_steps


class InstallationStateManager:
    """Manages installation state file"""

    def __init__(self, state_file: Path = Path(".install_state.json")):
        self.state_file = state_file
        self.state: Optional[InstallationState] = None

    def init_new_installation(self) -> InstallationState:
        """Initialize new installation state"""
        self.state = InstallationState(
            installation_id=str(uuid.uuid4()),
            started_at=datetime.now().isoformat(),
            completed_steps=[],
            current_step=None,
            failed=False,
            error_message=None,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            venv_path=".venv",
            docker_available=False,
            docker_image=None
        )
        self.save()
        return self.state

    def load(self) -> Optional[InstallationState]:
        """Load existing installation state"""
        if self.state_file.exists():
            self.state = InstallationState.from_json(self.state_file.read_text())
            return self.state
        return None

    def save(self):
        """Save current state to disk"""
        if self.state:
            self.state_file.write_text(self.state.to_json())

    def cleanup(self):
        """Remove state file"""
        if self.state_file.exists():
            self.state_file.unlink()


def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> Tuple[bool, str]:
    """
    Check if Python version meets minimum requirements

    Args:
        min_version: Minimum required version as tuple (major, minor)

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = check_python_version()
        >>> if not success:
        ...     print(f"Error: {msg}")
    """
    current = sys.version_info[:2]

    if current >= min_version:
        msg = f"✓ Python {current[0]}.{current[1]} found (>= {min_version[0]}.{min_version[1]} required)"
        logger.info(msg)
        return True, msg
    else:
        msg = f"✗ Python {current[0]}.{current[1]} found, but >= {min_version[0]}.{min_version[1]} required"
        logger.error(msg)
        return False, msg


def create_virtualenv(venv_path: Path = Path(".venv")) -> Tuple[bool, str]:
    """
    Create Python virtual environment

    Args:
        venv_path: Path where virtualenv should be created

    Returns:
        Tuple of (success: bool, message: str)

    Raises:
        subprocess.CalledProcessError: If venv creation fails
    """
    try:
        if venv_path.exists():
            msg = f"⚠ Virtualenv already exists at {venv_path}, skipping..."
            logger.warning(msg)
            return True, msg

        logger.info(f"Creating virtualenv at {venv_path}...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
            text=True
        )

        msg = f"✓ Virtualenv created successfully at {venv_path}"
        logger.info(msg)
        return True, msg

    except subprocess.CalledProcessError as e:
        msg = f"✗ Failed to create virtualenv: {e.stderr}"
        logger.error(msg)
        return False, msg


def install_dependencies(
    venv_path: Path = Path(".venv"),
    requirements_file: Path = Path("requirements.txt")
) -> Tuple[bool, str]:
    """
    Install Python dependencies from requirements.txt

    Args:
        venv_path: Path to virtualenv
        requirements_file: Path to requirements.txt

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Determine pip executable path
        if sys.platform == "win32":
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            pip_exe = venv_path / "bin" / "pip"

        if not pip_exe.exists():
            msg = f"✗ pip not found in virtualenv: {pip_exe}"
            logger.error(msg)
            return False, msg

        if not requirements_file.exists():
            msg = f"✗ requirements.txt not found: {requirements_file}"
            logger.error(msg)
            return False, msg

        logger.info(f"Installing dependencies from {requirements_file}...")
        result = subprocess.run(
            [str(pip_exe), "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True
        )

        msg = f"✓ Dependencies installed successfully"
        logger.info(msg)
        logger.debug(f"pip output: {result.stdout}")
        return True, msg

    except subprocess.CalledProcessError as e:
        msg = f"✗ Failed to install dependencies: {e.stderr}"
        logger.error(msg)
        return False, msg


def check_docker() -> Tuple[bool, str, Optional[str]]:
    """
    Check if Docker is available and running

    Returns:
        Tuple of (available: bool, message: str, version: Optional[str])
    """
    try:
        result = subprocess.run(
            ["docker", "--version"],
            check=True,
            capture_output=True,
            text=True
        )

        version = result.stdout.strip()
        msg = f"✓ Docker found: {version}"
        logger.info(msg)
        return True, msg, version

    except (subprocess.CalledProcessError, FileNotFoundError):
        msg = "⚠ Docker not found. OCR features will not be available."
        logger.warning(msg)
        return False, msg, None


def pull_docker_image(image: str = "jbarlow83/ocrmypdf:v14.4.0") -> Tuple[bool, str]:
    """
    Pull Docker image for OCR processing

    Args:
        image: Docker image name with tag

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        logger.info(f"Pulling Docker image: {image}")
        logger.info("This may take a few minutes on first installation...")

        result = subprocess.run(
            ["docker", "pull", image],
            check=True,
            capture_output=True,
            text=True
        )

        msg = f"✓ Docker image pulled successfully: {image}"
        logger.info(msg)
        return True, msg

    except subprocess.CalledProcessError as e:
        msg = f"✗ Failed to pull Docker image: {e.stderr}"
        logger.error(msg)
        return False, msg


def test_docker_ocr(
    image: str = "jbarlow83/ocrmypdf:v14.4.0",
    test_pdf: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Test Docker OCR functionality

    Args:
        image: Docker image to test
        test_pdf: Optional test PDF file (uses built-in test if None)

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Simple test: Run --version command
        result = subprocess.run(
            ["docker", "run", "--rm", image, "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        msg = f"✓ Docker OCR test successful: {result.stdout.strip()}"
        logger.info(msg)
        return True, msg

    except subprocess.CalledProcessError as e:
        msg = f"✗ Docker OCR test failed: {e.stderr}"
        logger.error(msg)
        return False, msg
    except subprocess.TimeoutExpired:
        msg = "✗ Docker OCR test timed out"
        logger.error(msg)
        return False, msg


def generate_test_pdfs_wrapper(output_dir: Path = Path("tests/test_data")) -> Tuple[bool, str]:
    """
    Wrapper to call generate_test_pdfs.py

    Args:
        output_dir: Directory for generated test PDFs

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating test PDFs in {output_dir}...")

        # Import and call the test PDF generator
        from generate_test_pdfs import TestPDFGenerator

        generator = TestPDFGenerator(output_dir)
        generated_files = generator.generate_all(include_large=False)

        msg = f"✓ Generated {len(generated_files)} test PDFs in {output_dir}"
        logger.info(msg)
        return True, msg

    except Exception as e:
        msg = f"✗ Failed to generate test PDFs: {str(e)}"
        logger.error(msg)
        return False, msg


def setup_logging(log_file: Optional[Path] = None, verbose: bool = False):
    """
    Setup logging configuration

    Args:
        log_file: Optional path to log file
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
