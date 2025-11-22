"""
De-Installation Library for PDFTools

This module provides functions for clean removal of PDFTools installation
including virtualenv, test data, Docker images, and logs.
"""

from pathlib import Path
from typing import List, Tuple
import subprocess
import shutil
import logging

logger = logging.getLogger('pdftools.uninstall')


def remove_virtualenv(venv_path: Path = Path(".venv")) -> Tuple[bool, str]:
    """
    Remove Python virtual environment

    Args:
        venv_path: Path to virtualenv directory

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if not venv_path.exists():
            msg = f"⚠ Virtualenv not found at {venv_path}, skipping..."
            logger.warning(msg)
            return True, msg

        logger.info(f"Removing virtualenv at {venv_path}...")
        shutil.rmtree(venv_path)

        msg = f"✓ Virtualenv removed: {venv_path}"
        logger.info(msg)
        return True, msg

    except Exception as e:
        msg = f"✗ Failed to remove virtualenv: {str(e)}"
        logger.error(msg)
        return False, msg


def cleanup_test_data(test_data_dir: Path = Path("tests/test_data")) -> Tuple[bool, str]:
    """
    Remove generated test PDFs

    Args:
        test_data_dir: Directory containing test PDFs

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if not test_data_dir.exists():
            msg = f"⚠ Test data directory not found: {test_data_dir}"
            logger.warning(msg)
            return True, msg

        pdf_files = list(test_data_dir.glob("test_*.pdf"))

        for pdf_file in pdf_files:
            pdf_file.unlink()
            logger.debug(f"Removed: {pdf_file}")

        msg = f"✓ Removed {len(pdf_files)} test PDF files"
        logger.info(msg)
        return True, msg

    except Exception as e:
        msg = f"✗ Failed to cleanup test data: {str(e)}"
        logger.error(msg)
        return False, msg


def remove_docker_images(images: List[str]) -> Tuple[bool, str]:
    """
    Remove Docker images

    Args:
        images: List of Docker image names to remove

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        removed = []

        for image in images:
            try:
                subprocess.run(
                    ["docker", "rmi", image],
                    check=True,
                    capture_output=True,
                    text=True
                )
                removed.append(image)
                logger.info(f"Removed Docker image: {image}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Could not remove {image}: {e.stderr}")

        if removed:
            msg = f"✓ Removed {len(removed)} Docker image(s)"
        else:
            msg = "⚠ No Docker images were removed"

        logger.info(msg)
        return True, msg

    except FileNotFoundError:
        msg = "⚠ Docker not found, skipping image removal"
        logger.warning(msg)
        return True, msg


def cleanup_logs(log_dir: Path = Path(".")) -> Tuple[bool, str]:
    """
    Remove installation log files

    Args:
        log_dir: Directory containing log files

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        log_files = list(log_dir.glob("install*.log"))
        log_files.extend(log_dir.glob(".install_state.json"))

        for log_file in log_files:
            log_file.unlink()
            logger.debug(f"Removed: {log_file}")

        msg = f"✓ Removed {len(log_files)} log/state file(s)"
        logger.info(msg)
        return True, msg

    except Exception as e:
        msg = f"✗ Failed to cleanup logs: {str(e)}"
        logger.error(msg)
        return False, msg


def setup_logging(log_file: Path | None = None, verbose: bool = False):
    """
    Setup logging configuration

    Args:
        log_file: Optional path to log file
        verbose: Enable verbose (DEBUG) logging
    """
    import sys

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
