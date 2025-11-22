"""
Unit tests for installation library
"""

import pytest
from pathlib import Path
import sys
import subprocess
from unittest.mock import Mock, patch, MagicMock
import json

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from install_lib import (
    check_python_version,
    create_virtualenv,
    install_dependencies,
    check_docker,
    pull_docker_image,
    test_docker_ocr,
    InstallationState,
    InstallationStateManager,
    InstallationStep
)


class TestPythonVersionCheck:
    """Tests for Python version checking"""

    def test_check_python_version_success(self, monkeypatch):
        """Test Python version check with valid version"""
        monkeypatch.setattr(sys, 'version_info', (3, 10, 5, 'final', 0))

        success, msg = check_python_version((3, 8))
        assert success
        assert "3.10" in msg
        assert "✓" in msg

    def test_check_python_version_failure(self, monkeypatch):
        """Test Python version check with old version"""
        monkeypatch.setattr(sys, 'version_info', (3, 7, 0, 'final', 0))

        success, msg = check_python_version((3, 8))
        assert not success
        assert "3.7" in msg
        assert "✗" in msg

    def test_check_python_version_exact_minimum(self, monkeypatch):
        """Test with exactly the minimum version"""
        monkeypatch.setattr(sys, 'version_info', (3, 8, 0, 'final', 0))

        success, msg = check_python_version((3, 8))
        assert success
        assert "3.8" in msg


class TestVirtualenvCreation:
    """Tests for virtualenv creation"""

    def test_create_virtualenv_success(self, tmp_path, monkeypatch):
        """Test successful virtualenv creation"""
        venv_path = tmp_path / ".venv"

        # Mock subprocess.run
        mock_run = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))
        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = create_virtualenv(venv_path)

        # Note: Success is true even if directory wasn't actually created
        # because we mocked the subprocess call
        assert "✓" in msg or "⚠" in msg

    def test_create_virtualenv_already_exists(self, tmp_path):
        """Test when virtualenv already exists"""
        venv_path = tmp_path / ".venv"
        venv_path.mkdir()

        success, msg = create_virtualenv(venv_path)
        assert success
        assert "already exists" in msg
        assert "⚠" in msg

    def test_create_virtualenv_failure(self, tmp_path, monkeypatch):
        """Test failed virtualenv creation"""
        venv_path = tmp_path / ".venv"

        # Mock subprocess.run to raise error
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr="Mock error")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = create_virtualenv(venv_path)
        assert not success
        assert "✗" in msg


class TestDependencyInstallation:
    """Tests for dependency installation"""

    def test_install_dependencies_missing_pip(self, tmp_path):
        """Test when pip executable is missing"""
        venv_path = tmp_path / ".venv"
        venv_path.mkdir()

        requirements_file = tmp_path / "requirements.txt"
        requirements_file.write_text("pytest>=7.0.0\n")

        success, msg = install_dependencies(venv_path, requirements_file)
        assert not success
        assert "pip not found" in msg

    def test_install_dependencies_missing_requirements(self, tmp_path):
        """Test when requirements.txt is missing"""
        venv_path = tmp_path / ".venv"
        venv_path.mkdir()

        # Create fake pip
        if sys.platform == "win32":
            pip_dir = venv_path / "Scripts"
        else:
            pip_dir = venv_path / "bin"
        pip_dir.mkdir(parents=True)
        pip_exe = pip_dir / ("pip.exe" if sys.platform == "win32" else "pip")
        pip_exe.touch()

        requirements_file = tmp_path / "requirements.txt"

        success, msg = install_dependencies(venv_path, requirements_file)
        assert not success
        assert "not found" in msg


class TestDockerCheck:
    """Tests for Docker availability check"""

    def test_check_docker_available(self, monkeypatch):
        """Test when Docker is available"""
        mock_result = Mock(stdout="Docker version 20.10.0", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        available, msg, version = check_docker()
        assert available
        assert "✓" in msg
        assert "20.10.0" in version

    def test_check_docker_not_found(self, monkeypatch):
        """Test when Docker is not found"""
        def mock_run(*args, **kwargs):
            raise FileNotFoundError("docker not found")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        available, msg, version = check_docker()
        assert not available
        assert "⚠" in msg
        assert version is None

    def test_check_docker_error(self, monkeypatch):
        """Test when Docker command fails"""
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr="Mock error")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        available, msg, version = check_docker()
        assert not available
        assert "⚠" in msg


class TestDockerImagePull:
    """Tests for Docker image pulling"""

    def test_pull_docker_image_success(self, monkeypatch):
        """Test successful Docker image pull"""
        mock_result = Mock(stdout="Pull complete", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = pull_docker_image("test/image:v1.0")
        assert success
        assert "✓" in msg
        assert "test/image:v1.0" in msg

    def test_pull_docker_image_failure(self, monkeypatch):
        """Test failed Docker image pull"""
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr="Pull failed")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = pull_docker_image("test/image:v1.0")
        assert not success
        assert "✗" in msg


class TestDockerOCRTest:
    """Tests for Docker OCR testing"""

    def test_docker_ocr_test_success(self, monkeypatch):
        """Test successful Docker OCR test"""
        mock_result = Mock(stdout="ocrmypdf 14.4.0", stderr="", returncode=0)
        mock_run = Mock(return_value=mock_result)
        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = test_docker_ocr("test/image:v1.0")
        assert success
        assert "✓" in msg
        assert "14.4.0" in msg

    def test_docker_ocr_test_failure(self, monkeypatch):
        """Test failed Docker OCR test"""
        def mock_run(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0], stderr="Test failed")

        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = test_docker_ocr("test/image:v1.0")
        assert not success
        assert "✗" in msg

    def test_docker_ocr_test_timeout(self, monkeypatch):
        """Test Docker OCR test timeout"""
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], 30)

        monkeypatch.setattr(subprocess, 'run', mock_run)

        success, msg = test_docker_ocr("test/image:v1.0")
        assert not success
        assert "timeout" in msg.lower()


class TestInstallationState:
    """Tests for Installation State Management"""

    def test_installation_state_creation(self):
        """Test creating an installation state"""
        state = InstallationState(
            installation_id="test-123",
            started_at="2025-11-22T10:00:00",
            completed_steps=[],
            current_step=None,
            failed=False,
            error_message=None,
            python_version="3.10",
            venv_path=".venv",
            docker_available=False,
            docker_image=None
        )

        assert state.installation_id == "test-123"
        assert state.completed_steps == []
        assert not state.failed

    def test_mark_step_complete(self):
        """Test marking a step as complete"""
        state = InstallationState(
            installation_id="test-123",
            started_at="2025-11-22T10:00:00",
            completed_steps=[],
            current_step=None,
            failed=False,
            error_message=None,
            python_version="3.10",
            venv_path=".venv",
            docker_available=False,
            docker_image=None
        )

        state.mark_step_complete(InstallationStep.CHECK_PYTHON)
        assert InstallationStep.CHECK_PYTHON.value in state.completed_steps

    def test_is_step_complete(self):
        """Test checking if step is complete"""
        state = InstallationState(
            installation_id="test-123",
            started_at="2025-11-22T10:00:00",
            completed_steps=["check_python", "create_venv"],
            current_step=None,
            failed=False,
            error_message=None,
            python_version="3.10",
            venv_path=".venv",
            docker_available=False,
            docker_image=None
        )

        assert state.is_step_complete(InstallationStep.CHECK_PYTHON)
        assert state.is_step_complete(InstallationStep.CREATE_VENV)
        assert not state.is_step_complete(InstallationStep.INSTALL_DEPS)

    def test_state_serialization(self):
        """Test JSON serialization/deserialization"""
        state = InstallationState(
            installation_id="test-123",
            started_at="2025-11-22T10:00:00",
            completed_steps=["check_python"],
            current_step="create_venv",
            failed=False,
            error_message=None,
            python_version="3.10",
            venv_path=".venv",
            docker_available=True,
            docker_image="jbarlow83/ocrmypdf:v14.4.0"
        )

        # Serialize
        json_str = state.to_json()
        assert "test-123" in json_str
        assert "check_python" in json_str

        # Deserialize
        restored = InstallationState.from_json(json_str)
        assert restored.installation_id == state.installation_id
        assert restored.completed_steps == state.completed_steps
        assert restored.docker_available == state.docker_available


class TestInstallationStateManager:
    """Tests for Installation State Manager"""

    def test_init_new_installation(self, tmp_path):
        """Test initializing new installation state"""
        state_file = tmp_path / ".install_state.json"
        manager = InstallationStateManager(state_file)

        state = manager.init_new_installation()

        assert state is not None
        assert state.installation_id is not None
        assert len(state.installation_id) > 0
        assert state.completed_steps == []
        assert state_file.exists()

    def test_load_existing_state(self, tmp_path):
        """Test loading existing installation state"""
        state_file = tmp_path / ".install_state.json"

        # Create initial state
        manager1 = InstallationStateManager(state_file)
        state1 = manager1.init_new_installation()
        state1.mark_step_complete(InstallationStep.CHECK_PYTHON)
        manager1.save()

        # Load state in new manager
        manager2 = InstallationStateManager(state_file)
        state2 = manager2.load()

        assert state2 is not None
        assert state2.installation_id == state1.installation_id
        assert InstallationStep.CHECK_PYTHON.value in state2.completed_steps

    def test_cleanup_state_file(self, tmp_path):
        """Test cleanup removes state file"""
        state_file = tmp_path / ".install_state.json"
        manager = InstallationStateManager(state_file)

        manager.init_new_installation()
        assert state_file.exists()

        manager.cleanup()
        assert not state_file.exists()
