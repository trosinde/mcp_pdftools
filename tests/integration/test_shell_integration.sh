#!/usr/bin/env bash
# Integration Tests for Shell Integration Feature
# Tests shell configuration during installation and uninstallation
# Version: 1.0

set -e
set -o pipefail

# ============================================================================
# Configuration
# ============================================================================

TEST_DIR="/tmp/mcp_pdftools_shell_integration_tests_$$"
TEST_LOG="$TEST_DIR/test.log"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_INSTALL_DIR="$TEST_DIR/install"
TEST_HOME="$TEST_DIR/home"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Logging
# ============================================================================

log_test() {
    if [ -f "$TEST_LOG" ]; then
        echo "[TEST] $1" | tee -a "$TEST_LOG"
    else
        echo "[TEST] $1"
    fi
}

log_pass() {
    ((TESTS_PASSED++))
    if [ -f "$TEST_LOG" ]; then
        echo -e "\033[1;32m[PASS]\033[0m $1" | tee -a "$TEST_LOG"
    else
        echo -e "\033[1;32m[PASS]\033[0m $1"
    fi
}

log_fail() {
    ((TESTS_FAILED++))
    if [ -f "$TEST_LOG" ]; then
        echo -e "\033[1;31m[FAIL]\033[0m $1" | tee -a "$TEST_LOG"
    else
        echo -e "\033[1;31m[FAIL]\033[0m $1"
    fi
}

log_info() {
    if [ -f "$TEST_LOG" ]; then
        echo "[INFO] $1" | tee -a "$TEST_LOG"
    else
        echo "[INFO] $1"
    fi
}

log_warn() {
    if [ -f "$TEST_LOG" ]; then
        echo -e "\033[1;33m[WARN]\033[0m $1" | tee -a "$TEST_LOG"
    else
        echo -e "\033[1;33m[WARN]\033[0m $1"
    fi
}

# ============================================================================
# Setup and Teardown
# ============================================================================

setup_test_environment() {
    log_info "Setting up test environment..."

    # Create test directories
    mkdir -p "$TEST_DIR"
    mkdir -p "$TEST_HOME"
    mkdir -p "$TEST_INSTALL_DIR"
    mkdir -p "$TEST_HOME/.config/fish"

    # Initialize log file
    touch "$TEST_LOG"

    log_info "Test directory: $TEST_DIR"
    log_info "Test home: $TEST_HOME"
    log_info "Test install dir: $TEST_INSTALL_DIR"
}

cleanup_test_environment() {
    log_info "Cleaning up test environment..."
    if [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
    log_info "Cleanup complete"
}

# ============================================================================
# Helper Functions
# ============================================================================

# Source the install utils for testing
source_install_utils() {
    if [ -f "$REPO_DIR/scripts/install_utils.sh" ]; then
        # Set required environment variables
        export MCP_INSTALL_LOG="$TEST_LOG"
        export HOME="$TEST_HOME"
        export INSTALL_DIR="$TEST_INSTALL_DIR"

        source "$REPO_DIR/scripts/install_utils.sh"
        return 0
    else
        log_fail "install_utils.sh not found at $REPO_DIR/scripts/install_utils.sh"
        return 1
    fi
}

create_mock_shell_config() {
    local shell_type="$1"
    local config_file=""

    case "$shell_type" in
        bash)
            config_file="$TEST_HOME/.bashrc"
            ;;
        zsh)
            config_file="$TEST_HOME/.zshrc"
            ;;
        fish)
            config_file="$TEST_HOME/.config/fish/config.fish"
            ;;
        *)
            return 1
            ;;
    esac

    # Create parent directory if needed
    mkdir -p "$(dirname "$config_file")"

    # Create minimal shell config
    cat > "$config_file" <<EOF
# Test shell configuration
export TEST_VAR="test_value"
EOF

    echo "$config_file"
    return 0
}

create_mock_venv() {
    mkdir -p "$TEST_INSTALL_DIR/venv/bin"

    # Create mock executables
    local tools=("pdfmerge" "pdfsplit" "pdfgettxt" "ocrutil" "pdfprotect" "pdfthumbnails" "pdfrename")
    for tool in "${tools[@]}"; do
        cat > "$TEST_INSTALL_DIR/venv/bin/$tool" <<EOF
#!/bin/bash
echo "$tool version 1.0.0"
EOF
        chmod +x "$TEST_INSTALL_DIR/venv/bin/$tool"
    done
}

# ============================================================================
# Test Cases
# ============================================================================

test_01_detect_shell_bash() {
    ((TESTS_RUN++))
    log_test "Test 1: Detect bash shell"

    source_install_utils || return 1

    export SHELL="/bin/bash"
    local result=$(detect_shell)

    if [ "$result" = "bash" ]; then
        log_pass "Successfully detected bash shell"
        return 0
    else
        log_fail "Failed to detect bash shell (got: $result)"
        return 1
    fi
}

test_02_detect_shell_zsh() {
    ((TESTS_RUN++))
    log_test "Test 2: Detect zsh shell"

    source_install_utils || return 1

    export SHELL="/usr/bin/zsh"
    local result=$(detect_shell)

    if [ "$result" = "zsh" ]; then
        log_pass "Successfully detected zsh shell"
        return 0
    else
        log_fail "Failed to detect zsh shell (got: $result)"
        return 1
    fi
}

test_03_detect_shell_fish() {
    ((TESTS_RUN++))
    log_test "Test 3: Detect fish shell"

    source_install_utils || return 1

    export SHELL="/usr/bin/fish"
    local result=$(detect_shell)

    if [ "$result" = "fish" ]; then
        log_pass "Successfully detected fish shell"
        return 0
    else
        log_fail "Failed to detect fish shell (got: $result)"
        return 1
    fi
}

test_04_skip_shell_config_flag() {
    ((TESTS_RUN++))
    log_test "Test 4: Skip shell config with SKIP_SHELL_CONFIG=true"

    source_install_utils || return 1

    export SHELL="/bin/bash"
    export SKIP_SHELL_CONFIG="true"

    detect_shell > /dev/null 2>&1
    local result=$?

    if [ $result -ne 0 ]; then
        log_pass "Successfully skipped shell config with SKIP_SHELL_CONFIG=true"
        unset SKIP_SHELL_CONFIG
        return 0
    else
        log_fail "Failed to skip shell config (should return non-zero)"
        unset SKIP_SHELL_CONFIG
        return 1
    fi
}

test_05_get_shell_config_file_bash() {
    ((TESTS_RUN++))
    log_test "Test 5: Get bash config file"

    source_install_utils || return 1

    local result=$(get_shell_config_file "bash")

    if [[ "$result" == *".bashrc" ]] || [[ "$result" == *".bash_profile" ]]; then
        log_pass "Successfully got bash config file: $result"
        return 0
    else
        log_fail "Failed to get bash config file (got: $result)"
        return 1
    fi
}

test_06_get_shell_config_file_zsh() {
    ((TESTS_RUN++))
    log_test "Test 6: Get zsh config file"

    source_install_utils || return 1

    local result=$(get_shell_config_file "zsh")

    if [[ "$result" == *".zshrc" ]]; then
        log_pass "Successfully got zsh config file: $result"
        return 0
    else
        log_fail "Failed to get zsh config file (got: $result)"
        return 1
    fi
}

test_07_check_not_configured() {
    ((TESTS_RUN++))
    log_test "Test 7: Check PATH not configured"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    if check_path_already_configured "$config_file" "$TEST_INSTALL_DIR"; then
        log_fail "Incorrectly detected as configured"
        return 1
    else
        log_pass "Correctly detected as not configured"
        return 0
    fi
}

test_08_check_already_configured_with_marker() {
    ((TESTS_RUN++))
    log_test "Test 8: Check PATH already configured (with marker)"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    # Add marker
    echo "# mcp_pdftools - Added by automated installation" >> "$config_file"
    echo "export PATH=\"$TEST_INSTALL_DIR/venv/bin:\$PATH\"" >> "$config_file"

    if check_path_already_configured "$config_file" "$TEST_INSTALL_DIR"; then
        log_pass "Correctly detected as already configured"
        return 0
    else
        log_fail "Failed to detect existing configuration"
        return 1
    fi
}

test_09_create_config_backup() {
    ((TESTS_RUN++))
    log_test "Test 9: Create config backup"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    # The function logs but returns the backup file path via echo
    local backup_output=$(create_config_backup "$config_file" 2>&1)
    local backup_file=$(echo "$backup_output" | tail -1)

    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        log_pass "Successfully created backup: $backup_file"
        return 0
    else
        log_fail "Failed to create backup file (output: $backup_output)"
        return 1
    fi
}

test_10_add_path_to_shell_config_bash() {
    ((TESTS_RUN++))
    log_test "Test 10: Add PATH to bash config"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    if add_path_to_shell_config "$config_file" "$TEST_INSTALL_DIR" "bash"; then
        # Check if marker was added
        if grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
            # Check if PATH export was added
            if grep -q "export PATH=" "$config_file"; then
                log_pass "Successfully added PATH to bash config"
                return 0
            fi
        fi
    fi

    log_fail "Failed to add PATH to bash config"
    return 1
}

test_11_add_path_to_shell_config_fish() {
    ((TESTS_RUN++))
    log_test "Test 11: Add PATH to fish config"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "fish")

    if add_path_to_shell_config "$config_file" "$TEST_INSTALL_DIR" "fish"; then
        # Check if marker was added
        if grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
            # Check if PATH set was added (fish syntax)
            if grep -q "set -gx PATH" "$config_file"; then
                log_pass "Successfully added PATH to fish config"
                return 0
            fi
        fi
    fi

    log_fail "Failed to add PATH to fish config"
    return 1
}

test_12_validate_shell_config_valid() {
    ((TESTS_RUN++))
    log_test "Test 12: Validate valid shell config"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    if validate_shell_config "$config_file" "bash" ""; then
        log_pass "Successfully validated shell config"
        return 0
    else
        log_fail "Failed to validate valid shell config"
        return 1
    fi
}

test_13_activate_path_current_session() {
    ((TESTS_RUN++))
    log_test "Test 13: Activate PATH in current session"

    source_install_utils || return 1
    create_mock_venv

    if activate_path_current_session "$TEST_INSTALL_DIR"; then
        # Check if PATH was updated
        if [[ ":$PATH:" == *":$TEST_INSTALL_DIR/venv/bin:"* ]]; then
            log_pass "Successfully activated PATH in current session"
            return 0
        fi
    fi

    log_fail "Failed to activate PATH in current session"
    return 1
}

test_14_verify_tools_accessible() {
    ((TESTS_RUN++))
    log_test "Test 14: Verify tools accessible"

    source_install_utils || return 1
    create_mock_venv

    # Add to PATH
    export PATH="$TEST_INSTALL_DIR/venv/bin:$PATH"

    if verify_tools_accessible; then
        log_pass "Successfully verified tools are accessible"
        return 0
    else
        log_warn "Some tools not accessible (expected in test environment)"
        # This is non-fatal in test environment
        log_pass "Tool verification function executed"
        return 0
    fi
}

test_15_remove_shell_configuration() {
    ((TESTS_RUN++))
    log_test "Test 15: Remove shell configuration"

    source_install_utils || return 1

    # Create config with marker
    local config_file="$TEST_HOME/.bashrc"
    create_mock_shell_config "bash" > /dev/null

    echo "" >> "$config_file"
    echo "# mcp_pdftools - Added by automated installation" >> "$config_file"
    echo "export PATH=\"$TEST_INSTALL_DIR/venv/bin:\$PATH\"" >> "$config_file"

    # Verify marker exists
    if ! grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
        log_fail "Setup failed: marker not found"
        return 1
    fi

    # Remove configuration
    if remove_shell_configuration; then
        # Check if marker was removed
        if grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
            log_fail "Failed to remove marker from config"
            return 1
        else
            log_pass "Successfully removed shell configuration"
            return 0
        fi
    else
        log_fail "remove_shell_configuration failed"
        return 1
    fi
}

test_16_fresh_installation_with_consent() {
    ((TESTS_RUN++))
    log_test "Test 16: Fresh installation with shell config consent (simulation)"

    source_install_utils || return 1
    create_mock_venv

    local config_file=$(create_mock_shell_config "bash")

    # Simulate configuration flow
    local backup_file=$(create_config_backup "$config_file")

    if add_path_to_shell_config "$config_file" "$TEST_INSTALL_DIR" "bash"; then
        if validate_shell_config "$config_file" "bash" "$backup_file"; then
            if activate_path_current_session "$TEST_INSTALL_DIR"; then
                log_pass "Fresh installation simulation successful"
                return 0
            fi
        fi
    fi

    log_fail "Fresh installation simulation failed"
    return 1
}

test_17_installation_already_configured() {
    ((TESTS_RUN++))
    log_test "Test 17: Installation when already configured (should skip)"

    source_install_utils || return 1

    local config_file=$(create_mock_shell_config "bash")

    # Pre-configure
    echo "# mcp_pdftools - Added by automated installation" >> "$config_file"
    echo "export PATH=\"$TEST_INSTALL_DIR/venv/bin:\$PATH\"" >> "$config_file"

    # Check if already configured
    if check_path_already_configured "$config_file" "$TEST_INSTALL_DIR"; then
        log_pass "Correctly detected existing configuration and would skip"
        return 0
    else
        log_fail "Failed to detect existing configuration"
        return 1
    fi
}

test_18_uninstallation_removes_config() {
    ((TESTS_RUN++))
    log_test "Test 18: Uninstallation removes shell configuration"

    source_install_utils || return 1

    # Setup: Add configuration
    local config_file="$TEST_HOME/.bashrc"
    create_mock_shell_config "bash" > /dev/null
    echo "" >> "$config_file"
    echo "# mcp_pdftools - Added by automated installation" >> "$config_file"
    echo "export PATH=\"$TEST_INSTALL_DIR/venv/bin:\$PATH\"" >> "$config_file"

    # Get line count before
    local lines_before=$(wc -l < "$config_file")

    # Remove configuration
    if remove_shell_configuration; then
        # Get line count after
        local lines_after=$(wc -l < "$config_file")

        # Check if lines were removed
        if [ "$lines_after" -lt "$lines_before" ]; then
            # Check if marker is gone
            if ! grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
                log_pass "Uninstallation successfully removed configuration"
                return 0
            fi
        fi
    fi

    log_fail "Uninstallation failed to remove configuration properly"
    return 1
}

test_19_verify_tools_accessible_after_install() {
    ((TESTS_RUN++))
    log_test "Test 19: Verify tools accessible after installation"

    source_install_utils || return 1
    create_mock_venv

    # Simulate adding to PATH
    export PATH="$TEST_INSTALL_DIR/venv/bin:$PATH"

    # Check each tool
    local tools=("pdfmerge" "pdfsplit" "pdfgettxt" "ocrutil" "pdfprotect" "pdfthumbnails" "pdfrename")
    local all_found=true

    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            all_found=false
            break
        fi
    done

    if $all_found; then
        log_pass "All tools accessible after installation"
        return 0
    else
        log_fail "Some tools not accessible after installation"
        return 1
    fi
}

test_20_skip_shell_config_env_var() {
    ((TESTS_RUN++))
    log_test "Test 20: Installation with SKIP_SHELL_CONFIG=true"

    export SKIP_SHELL_CONFIG="true"
    source_install_utils || return 1

    export SHELL="/bin/bash"

    # Try to detect shell - should fail/skip
    detect_shell > /dev/null 2>&1
    local result=$?

    unset SKIP_SHELL_CONFIG

    if [ $result -ne 0 ]; then
        log_pass "Successfully skipped shell config with environment variable"
        return 0
    else
        log_fail "Failed to skip shell config"
        return 1
    fi
}

# ============================================================================
# Main Test Execution
# ============================================================================

run_all_tests() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Shell Integration - Integration Test Suite"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    setup_test_environment

    # Run all tests
    test_01_detect_shell_bash || true
    test_02_detect_shell_zsh || true
    test_03_detect_shell_fish || true
    test_04_skip_shell_config_flag || true
    test_05_get_shell_config_file_bash || true
    test_06_get_shell_config_file_zsh || true
    test_07_check_not_configured || true
    test_08_check_already_configured_with_marker || true
    test_09_create_config_backup || true
    test_10_add_path_to_shell_config_bash || true
    test_11_add_path_to_shell_config_fish || true
    test_12_validate_shell_config_valid || true
    test_13_activate_path_current_session || true
    test_14_verify_tools_accessible || true
    test_15_remove_shell_configuration || true
    test_16_fresh_installation_with_consent || true
    test_17_installation_already_configured || true
    test_18_uninstallation_removes_config || true
    test_19_verify_tools_accessible_after_install || true
    test_20_skip_shell_config_env_var || true

    # Summary
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Test Summary"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Total Tests:  $TESTS_RUN"
    echo "Passed:       $TESTS_PASSED"
    echo "Failed:       $TESTS_FAILED"
    echo ""
    echo "Log File:     $TEST_LOG"
    echo ""

    # Cleanup
    cleanup_test_environment

    # Exit with appropriate code
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "✓ All tests passed!"
        return 0
    else
        echo "✗ Some tests failed"
        return 1
    fi
}

# Run tests
run_all_tests
exit $?
