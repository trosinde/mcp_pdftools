# Design Document: REQ-011 v1.1 - Shell Integration

**Document ID**: DESIGN-011-v1.1
**Requirement**: REQ-011 v1.1 - Shell Integration and PATH Configuration
**Version**: 1.0
**Status**: Draft
**Author**: Software Architect
**Date**: 2025-11-22
**Approved By**: (Pending Architecture Review)

---

## 1. Overview

### 1.1 Purpose
Design the shell integration functionality to automatically configure user shell environments, making CLI tools globally accessible without requiring virtual environment activation.

### 1.2 Scope
- **In Scope**:
  - Shell detection (bash, zsh, fish, PowerShell)
  - Automatic PATH configuration in shell config files
  - User consent mechanism
  - Immediate activation of changes
  - Cleanup during uninstallation
  - Fallback to manual instructions
  - Backup and validation mechanisms

- **Out of Scope**:
  - System-wide installation (/usr/local/bin symlinks)
  - Non-standard shells (tcsh, ksh, csh)
  - GUI-based configuration
  - Automatic shell reloading in existing terminals

### 1.3 Design Goals
1. **Simplicity**: One function call to configure shell
2. **Safety**: Always create backups, validate syntax
3. **User Control**: Explicit consent before modification
4. **Reversibility**: Clean uninstall removes all traces
5. **Robustness**: Handle edge cases gracefully

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    install.sh                           │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │         Main Installation Flow                    │ │
│  │  Step 7: Install Python dependencies             │ │
│  │  Step 8: Configure Shell Environment ◄── NEW     │ │
│  │  Step 9: Run functional tests                    │ │
│  └─────────────────┬─────────────────────────────────┘ │
│                    │                                   │
│                    ▼                                   │
│  ┌───────────────────────────────────────────────────┐ │
│  │     configure_shell_environment()                 │ │
│  │                                                   │ │
│  │  1. Check SKIP_SHELL_CONFIG flag                 │ │
│  │  2. Detect user shell                            │ │
│  │  3. Request user consent                         │ │
│  │  4. Create backup of shell config                │ │
│  │  5. Add PATH modification                        │ │
│  │  6. Validate syntax                              │ │
│  │  7. Activate in current session                  │ │
│  │  8. Verify tools are accessible                  │ │
│  └─────────────────┬─────────────────────────────────┘ │
└────────────────────┼─────────────────────────────────────┘
                     │
                     │ calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│           scripts/install_utils.sh (EXTENDED)           │
│                                                         │
│  New Functions:                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  detect_shell()                                 │   │
│  │  ├─ Returns: bash|zsh|fish|powershell|unknown   │   │
│  │  └─ Source: $SHELL environment variable         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  get_shell_config_file(shell_type)             │   │
│  │  ├─ bash → ~/.bashrc                            │   │
│  │  ├─ zsh → ~/.zshrc                              │   │
│  │  ├─ fish → ~/.config/fish/config.fish           │   │
│  │  └─ powershell → $PROFILE                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  add_path_to_shell_config(config_file, path)   │   │
│  │  ├─ Check for existing entry                    │   │
│  │  ├─ Create backup (.bashrc.backup.timestamp)    │   │
│  │  ├─ Add marker comment                          │   │
│  │  ├─ Add export PATH="$path:$PATH"               │   │
│  │  └─ Validate syntax                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  activate_path_current_session(path)            │   │
│  │  ├─ Export PATH in current shell                │   │
│  │  └─ Source shell config file                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  verify_tools_accessible()                      │   │
│  │  ├─ Test: which pdfmerge                        │   │
│  │  ├─ Test: pdfmerge --version                    │   │
│  │  └─ Returns: 0 if all tools found               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   uninstall.sh (EXTENDED)               │
│                                                         │
│  Step 4: Remove Shell Configuration ◄── NEW            │
│  ├─ remove_shell_configuration()                       │
│  │  ├─ Detect shell config files                      │
│  │  ├─ Search for marker comment                      │
│  │  ├─ Remove marker + PATH export lines              │
│  │  ├─ Create backup before removal                   │
│  │  └─ Validate shell still works                     │
│  └─ Log all removals                                   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
User runs install.sh
       │
       ▼
[1] Detect Shell
       │  $SHELL → /bin/bash
       ▼
[2] Find Config File
       │  bash → ~/.bashrc
       ▼
[3] Check for Existing Entry
       │  grep "mcp_pdftools" ~/.bashrc
       │  Not found
       ▼
[4] Request User Consent
       │  "Configure shell to make PDF tools globally available?"
       │  "This will add the following to your ~/.bashrc:"
       │  "  export PATH=\"$HOME/mcp_pdftools/venv/bin:$PATH\""
       │  "Proceed? [Y/n]: "
       │  User enters: Y
       ▼
[5] Create Backup
       │  cp ~/.bashrc ~/.bashrc.backup.2025-11-22_22-45-00
       │  Backup location logged
       ▼
[6] Add PATH Modification
       │  echo "" >> ~/.bashrc
       │  echo "# mcp_pdftools - Added by automated installation" >> ~/.bashrc
       │  echo "export PATH=\"$HOME/mcp_pdftools/venv/bin:$PATH\"" >> ~/.bashrc
       ▼
[7] Validate Syntax
       │  bash -n ~/.bashrc  # Check for syntax errors
       │  Exit code: 0 (valid)
       ▼
[8] Activate in Current Session
       │  export PATH="$HOME/mcp_pdftools/venv/bin:$PATH"
       │  source ~/.bashrc
       ▼
[9] Verify Tools Accessible
       │  which pdfmerge → /home/user/mcp_pdftools/venv/bin/pdfmerge
       │  pdfmerge --version → pdftools-merge 1.0.0
       ▼
[10] Success
       │  "✓ Shell configured successfully"
       │  "PDF tools are now available globally"
       │  "You can run: pdfmerge, pdfsplit, pdfgettxt, etc."
```

---

## 3. Detailed Design

### 3.1 Shell Detection

**Function**: `detect_shell()`

**Algorithm**:
```bash
detect_shell() {
    # Check if SKIP_SHELL_CONFIG is set
    if [ "$SKIP_SHELL_CONFIG" = "true" ]; then
        log_info "⊘ Skipping shell configuration (SKIP_SHELL_CONFIG=true)"
        return 1
    fi

    # Get shell from environment
    local shell_path="${SHELL:-}"

    # Handle missing $SHELL
    if [ -z "$shell_path" ]; then
        log_warn "SHELL environment variable not set"
        # Try to detect from parent process
        shell_path=$(ps -p $$ -o comm= 2>/dev/null)
    fi

    # Determine shell type
    case "$shell_path" in
        */bash)
            echo "bash"
            return 0
            ;;
        */zsh)
            echo "zsh"
            return 0
            ;;
        */fish)
            echo "fish"
            return 0
            ;;
        *powershell*|*pwsh*)
            echo "powershell"
            return 0
            ;;
        *)
            echo "unknown"
            return 1
            ;;
    esac
}
```

**Test Cases**:
- `$SHELL=/bin/bash` → returns "bash"
- `$SHELL=/usr/bin/zsh` → returns "zsh"
- `$SHELL=/usr/bin/fish` → returns "fish"
- `$SHELL=""` → attempts detection from `ps`, returns "unknown" if fails
- `SKIP_SHELL_CONFIG=true` → returns 1 (skip)

---

### 3.2 Config File Location

**Function**: `get_shell_config_file()`

**Algorithm**:
```bash
get_shell_config_file() {
    local shell_type="$1"
    local config_file=""

    case "$shell_type" in
        bash)
            # Prefer .bashrc, fallback to .bash_profile
            if [ -f "$HOME/.bashrc" ] || [ ! -f "$HOME/.bash_profile" ]; then
                config_file="$HOME/.bashrc"
            else
                config_file="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            config_file="$HOME/.zshrc"
            ;;
        fish)
            config_file="$HOME/.config/fish/config.fish"
            ;;
        powershell)
            # Windows PowerShell
            config_file="$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
            ;;
        *)
            return 1
            ;;
    esac

    echo "$config_file"
    return 0
}
```

**File Creation**:
- If config file doesn't exist, create it with proper permissions (0644)
- For fish, create parent directory: `mkdir -p ~/.config/fish`

---

### 3.3 Existing Entry Detection

**Function**: `check_path_already_configured()`

**Algorithm**:
```bash
check_path_already_configured() {
    local config_file="$1"
    local install_dir="$2"

    # Check if file exists
    if [ ! -f "$config_file" ]; then
        return 1  # Not configured
    fi

    # Search for marker comment
    if grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
        return 0  # Already configured
    fi

    # Search for PATH containing install directory
    if grep -q "$install_dir/venv/bin" "$config_file"; then
        log_warn "Found PATH entry without marker comment"
        log_warn "Manual configuration detected - skipping auto-config"
        return 0  # Assume configured
    fi

    return 1  # Not configured
}
```

**Behavior**:
- If marker found: Skip configuration, log "Already configured"
- If PATH found without marker: Skip configuration, log warning
- If nothing found: Proceed with configuration

---

### 3.4 User Consent

**Function**: `request_shell_config_consent()`

**Algorithm**:
```bash
request_shell_config_consent() {
    local shell_type="$1"
    local config_file="$2"
    local install_dir="$3"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Shell Configuration (Optional)                   ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "To make PDF tools globally available, we can configure your shell."
    echo ""
    echo "Detected shell: $shell_type"
    echo "Configuration file: $config_file"
    echo ""
    echo "The following will be added:"
    echo "  # mcp_pdftools - Added by automated installation"
    echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
    echo ""
    echo "Benefits:"
    echo "  ✓ Run 'pdfmerge' from any directory"
    echo "  ✓ No need to activate virtual environment"
    echo "  ✓ Uninstaller will automatically remove this configuration"
    echo ""
    echo "Alternative:"
    echo "  ○ Skip this step and activate venv manually:"
    echo "    $ cd $install_dir"
    echo "    $ source venv/bin/activate"
    echo ""

    if confirm "Configure shell automatically?"; then
        return 0
    else
        log_info "Shell configuration declined by user"
        show_manual_config_instructions "$shell_type" "$install_dir"
        return 1
    fi
}
```

---

### 3.5 Backup Creation

**Function**: `create_config_backup()`

**Algorithm**:
```bash
create_config_backup() {
    local config_file="$1"
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local backup_file="${config_file}.backup.${timestamp}"

    # Check if file exists
    if [ ! -f "$config_file" ]; then
        log_info "Config file doesn't exist yet, no backup needed"
        return 0
    fi

    # Create backup
    if cp "$config_file" "$backup_file"; then
        log_info "✓ Backup created: $backup_file"
        echo "$backup_file"  # Return backup path
        return 0
    else
        log_error "Failed to create backup"
        return 1
    fi
}
```

---

### 3.6 PATH Modification

**Function**: `add_path_to_shell_config()`

**Algorithm**:
```bash
add_path_to_shell_config() {
    local config_file="$1"
    local install_dir="$2"
    local shell_type="$3"

    # Create config file if it doesn't exist
    if [ ! -f "$config_file" ]; then
        touch "$config_file"
        chmod 644 "$config_file"
        log_info "Created new config file: $config_file"
    fi

    # Prepare PATH configuration
    local marker="# mcp_pdftools - Added by automated installation"
    local path_export=""

    case "$shell_type" in
        bash|zsh)
            path_export="export PATH=\"\$HOME/mcp_pdftools/venv/bin:\$PATH\""
            ;;
        fish)
            path_export="set -gx PATH \$HOME/mcp_pdftools/venv/bin \$PATH"
            ;;
        powershell)
            path_export="\$env:Path = \"\$env:USERPROFILE\\mcp_pdftools\\venv\\Scripts;\$env:Path\""
            ;;
    esac

    # Add to config file
    {
        echo ""
        echo "$marker"
        echo "$path_export"
    } >> "$config_file"

    log_info "✓ PATH configuration added to $config_file"
    return 0
}
```

---

### 3.7 Syntax Validation

**Function**: `validate_shell_config()`

**Algorithm**:
```bash
validate_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    local backup_file="$3"

    case "$shell_type" in
        bash)
            if bash -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (bash -n)"
                return 0
            fi
            ;;
        zsh)
            if zsh -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (zsh -n)"
                return 0
            fi
            ;;
        fish)
            if fish -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (fish -n)"
                return 0
            fi
            ;;
        *)
            log_warn "Syntax validation not supported for $shell_type"
            return 0  # Assume valid
            ;;
    esac

    # Validation failed - restore backup
    log_error "Syntax validation failed!"
    if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
        log_info "Restoring backup from $backup_file"
        mv "$backup_file" "$config_file"
    fi
    return 1
}
```

---

### 3.8 Activation in Current Session

**Function**: `activate_path_current_session()`

**Algorithm**:
```bash
activate_path_current_session() {
    local install_dir="$1"
    local venv_bin="$install_dir/venv/bin"

    # Add to PATH in current session
    export PATH="$venv_bin:$PATH"
    log_info "✓ PATH updated in current session"

    # Verify
    if [ -d "$venv_bin" ]; then
        log_info "✓ Virtual environment bin directory exists"
        return 0
    else
        log_error "Virtual environment bin directory not found: $venv_bin"
        return 1
    fi
}
```

---

### 3.9 Tool Verification

**Function**: `verify_tools_accessible()`

**Algorithm**:
```bash
verify_tools_accessible() {
    local tools=("pdfmerge" "pdfsplit" "pdfgettxt" "ocrutil" "pdfprotect" "pdfthumbnails" "pdfrename")
    local failed=0

    log_info "Verifying CLI tools are accessible..."

    for tool in "${tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            log_info "  ✓ $tool: $(which $tool)"
        else
            log_warn "  ✗ $tool: Not found in PATH"
            ((failed++))
        fi
    done

    if [ $failed -eq 0 ]; then
        log_info "✓ All 7 CLI tools are globally accessible"
        return 0
    else
        log_warn "$failed CLI tools not accessible"
        return 1
    fi
}
```

---

### 3.10 Uninstallation Cleanup

**Function**: `remove_shell_configuration()`

**Algorithm**:
```bash
remove_shell_configuration() {
    log_info "Removing shell configuration..."

    # Detect shell configs to clean
    local configs=(
        "$HOME/.bashrc"
        "$HOME/.bash_profile"
        "$HOME/.zshrc"
        "$HOME/.config/fish/config.fish"
    )

    for config_file in "${configs[@]}"; do
        if [ ! -f "$config_file" ]; then
            continue
        fi

        # Check if marker exists
        if ! grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
            continue
        fi

        log_info "Found mcp_pdftools configuration in $config_file"

        # Create backup
        local backup_file="${config_file}.backup.$(date +%Y-%m-%d_%H-%M-%S)"
        cp "$config_file" "$backup_file"
        log_info "  ✓ Backup created: $backup_file"

        # Remove marker and next line (PATH export)
        # Use sed to remove the marker line and the line after it
        sed -i '/# mcp_pdftools - Added by automated installation/,+1 d' "$config_file"

        # Also remove empty line before marker if it exists
        sed -i '/^$/{ N; /\n# mcp_pdftools/d; }' "$config_file"

        log_info "  ✓ Configuration removed from $config_file"
    done

    log_info "✓ Shell configuration cleanup complete"
    return 0
}
```

**Edge Cases**:
1. Multiple entries (shouldn't happen, but remove all)
2. Manual edits between marker and PATH export (remove both lines only)
3. Config file doesn't exist (skip)
4. No marker found (skip)

---

## 4. Integration Points

### 4.1 install.sh Integration

**Location**: After Step 7 (Install Python dependencies), before Step 9 (Run tests)

**New Step 8**:
```bash
# Step 8: Configure shell environment
log_info "Step 8/10: Configuring shell environment..."
configure_shell_environment || log_warn "Shell configuration completed with warnings"
```

**Function**:
```bash
configure_shell_environment() {
    # 1. Detect shell
    local shell_type=$(detect_shell)
    if [ "$shell_type" = "unknown" ]; then
        log_warn "Could not detect shell type"
        show_manual_config_instructions "$shell_type" "$INSTALL_DIR"
        return 0  # Non-fatal
    fi

    log_info "Detected shell: $shell_type"

    # 2. Get config file
    local config_file=$(get_shell_config_file "$shell_type")
    if [ -z "$config_file" ]; then
        log_error "Could not determine config file for $shell_type"
        return 1
    fi

    log_info "Configuration file: $config_file"

    # 3. Check if already configured
    if check_path_already_configured "$config_file" "$INSTALL_DIR"; then
        log_info "✓ Shell already configured, skipping"
        return 0
    fi

    # 4. Request user consent
    if ! request_shell_config_consent "$shell_type" "$config_file" "$INSTALL_DIR"; then
        return 0  # User declined, non-fatal
    fi

    # 5. Create backup
    local backup_file=$(create_config_backup "$config_file")

    # 6. Add PATH modification
    if ! add_path_to_shell_config "$config_file" "$INSTALL_DIR" "$shell_type"; then
        log_error "Failed to modify shell configuration"
        return 1
    fi

    # 7. Validate syntax
    if ! validate_shell_config "$config_file" "$shell_type" "$backup_file"; then
        log_error "Shell configuration syntax validation failed"
        return 1
    fi

    # 8. Activate in current session
    activate_path_current_session "$INSTALL_DIR"

    # 9. Verify tools accessible
    if verify_tools_accessible; then
        log_info "✓ Shell configured successfully"
        echo ""
        echo "PDF tools are now available globally:"
        echo "  $ pdfmerge file1.pdf file2.pdf -o merged.pdf"
        echo "  $ pdfsplit input.pdf -m pages"
        echo "  $ pdfgettxt document.pdf -o output.txt"
        echo ""
        return 0
    else
        log_warn "Some tools not accessible, but configuration applied"
        return 0  # Non-fatal
    fi
}
```

### 4.2 uninstall.sh Integration

**Location**: After Step 3 (Deactivate venv), before Step 4 (Remove venv)

**New Step 4**:
```bash
# Step 4: Remove shell configuration
log_info "Removing shell configuration..."
remove_shell_configuration || log_warn "Shell configuration removal completed with warnings"
```

---

## 5. Error Handling

### 5.1 Error Scenarios

| Scenario | Handling | Recovery |
|----------|----------|----------|
| **Shell not detected** | Show manual instructions | Continue installation |
| **Config file not writable** | Log error, skip auto-config | Show manual instructions |
| **Syntax validation fails** | Restore backup, log error | Show manual instructions |
| **Tools not accessible after config** | Log warning, continue | User can debug later |
| **User declines consent** | Show manual instructions | Continue installation |
| **Backup creation fails** | Abort config modification | Show manual instructions |
| **Multiple existing entries** | Remove all, log warning | Continue cleanup |

### 5.2 Fallback Strategy

If automatic configuration fails at any point:
```bash
show_manual_config_instructions() {
    local shell_type="$1"
    local install_dir="$2"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║       Manual Shell Configuration Instructions           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "To make PDF tools globally available, add to your shell config:"
    echo ""

    case "$shell_type" in
        bash)
            echo "For Bash (~/.bashrc):"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload:"
            echo "  source ~/.bashrc"
            ;;
        zsh)
            echo "For Zsh (~/.zshrc):"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload:"
            echo "  source ~/.zshrc"
            ;;
        fish)
            echo "For Fish (~/.config/fish/config.fish):"
            echo "  set -gx PATH $install_dir/venv/bin \$PATH"
            echo ""
            echo "Then reload:"
            echo "  source ~/.config/fish/config.fish"
            ;;
        *)
            echo "Add the following to your shell configuration file:"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload your shell."
            ;;
    esac

    echo ""
    echo "To verify:"
    echo "  which pdfmerge"
    echo "  pdfmerge --version"
    echo ""
}
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

Test each function in isolation:

1. **detect_shell()**
   - Test with `SHELL=/bin/bash`
   - Test with `SHELL=/usr/bin/zsh`
   - Test with `SHELL=/usr/bin/fish`
   - Test with `SHELL=""` (missing)
   - Test with `SKIP_SHELL_CONFIG=true`

2. **get_shell_config_file()**
   - Test with bash (returns ~/.bashrc)
   - Test with zsh (returns ~/.zshrc)
   - Test with fish (returns ~/.config/fish/config.fish)
   - Test with unknown shell (returns empty)

3. **check_path_already_configured()**
   - Test with marker present
   - Test with PATH present but no marker
   - Test with neither marker nor PATH
   - Test with non-existent file

4. **add_path_to_shell_config()**
   - Test with existing file
   - Test with non-existent file (creates new)
   - Test with bash syntax
   - Test with fish syntax

5. **validate_shell_config()**
   - Test with valid syntax
   - Test with syntax error (should restore backup)
   - Test with unsupported shell (should skip validation)

6. **remove_shell_configuration()**
   - Test with marker present
   - Test with marker absent
   - Test with multiple configs
   - Test with manual edits around marker

### 6.2 Integration Tests

Test full workflow:

1. **Fresh Installation**
   ```bash
   # Given: Clean system, no shell config
   # When: Run install.sh with shell config consent
   # Then:
   #   - ~/.bashrc contains marker and PATH
   #   - Backup file created
   #   - Tools accessible globally
   #   - which pdfmerge succeeds
   ```

2. **Upgrade Installation**
   ```bash
   # Given: v2.2.0 installed (no shell config)
   # When: Upgrade to v2.3.0
   # Then:
   #   - Shell config added
   #   - No duplicate entries
   #   - Old installation still works
   ```

3. **Skip Shell Config**
   ```bash
   # Given: SKIP_SHELL_CONFIG=true
   # When: Run install.sh
   # Then:
   #   - No shell modification
   #   - Manual instructions shown
   #   - Installation succeeds
   ```

4. **User Declines Consent**
   ```bash
   # Given: User enters "n" at consent prompt
   # When: Installation continues
   # Then:
   #   - No shell modification
   #   - Manual instructions shown
   #   - Installation succeeds
   ```

5. **Uninstallation**
   ```bash
   # Given: Shell configured with marker
   # When: Run uninstall.sh
   # Then:
   #   - Marker and PATH removed from ~/.bashrc
   #   - Backup created
   #   - Shell still functional
   #   - which pdfmerge fails (not found)
   ```

6. **Multiple Shells**
   ```bash
   # Given: User has both ~/.bashrc and ~/.zshrc
   # When: Install with bash, then switch to zsh
   # Then:
   #   - Only active shell configured
   #   - No interference between shells
   ```

### 6.3 Edge Case Tests

1. **Missing Config File**
   - File should be created with proper permissions

2. **Corrupted Config File**
   - Syntax validation should catch and restore backup

3. **Multiple Installations**
   - Should detect existing entry and skip

4. **Manual Modification**
   - User manually added PATH → skip auto-config
   - User removed marker → treated as manual config

5. **Permissions Issues**
   - Config file not writable → show manual instructions
   - Backup directory not writable → abort config

---

## 7. Security Considerations

### 7.1 Path Injection Prevention

**Risk**: Install directory contains malicious characters
**Mitigation**:
```bash
validate_install_dir() {
    local dir="$1"

    # Check for dangerous characters
    if echo "$dir" | grep -qE '[;&|$`]'; then
        log_error "Install directory contains dangerous characters: $dir"
        return 1
    fi

    return 0
}
```

### 7.2 Backup Validation

**Risk**: Backup file overwritten or corrupted
**Mitigation**:
- Use timestamp in backup filename
- Verify backup file exists and is readable before modifying original
- Log backup location for user reference

### 7.3 Syntax Validation

**Risk**: Syntax error breaks user's shell
**Mitigation**:
- Always validate with `bash -n`, `zsh -n`, etc.
- Restore backup if validation fails
- Test in subshell before applying

### 7.4 Privilege Escalation

**Risk**: Configuration grants elevated privileges
**Mitigation**:
- Only modify user-level configs (no sudo)
- Never modify system-wide configs (/etc/profile, /etc/bash.bashrc)
- Document that only user can execute installed tools

---

## 8. Performance Considerations

### 8.1 Execution Time

Expected overhead per step:
- Shell detection: < 0.1s
- Config file lookup: < 0.1s
- Backup creation: < 0.5s (depends on file size)
- PATH modification: < 0.1s
- Syntax validation: < 0.5s
- Tool verification: < 0.5s (7 tools × ~0.07s each)

**Total overhead**: ~2 seconds (acceptable for installation)

### 8.2 Shell Startup Impact

Adding one export to PATH has negligible impact:
- Bash startup time increase: < 0.01s
- No runtime performance impact
- No memory overhead

---

## 9. Documentation Requirements

### 9.1 User Documentation

**INSTALLATION.md** needs:
- Section on automatic shell configuration
- FAQ: "Why is my shell being modified?"
- FAQ: "How do I undo shell configuration?"
- Manual configuration instructions

**README.md** needs:
- Updated "Quick Start" to mention global availability
- Note: "After installation, tools are available globally"

### 9.2 Developer Documentation

**CONTRIBUTING.md** needs:
- Testing shell configuration locally
- How to add support for new shells

---

## 10. Acceptance Criteria

All criteria from US-011-7 must be met:

- [x] Script detects user's shell (bash, zsh, fish, PowerShell)
- [x] Adds virtual environment bin directory to PATH in shell configuration
- [x] Configuration allows tools to be called directly
- [x] Changes take effect immediately
- [x] Uninstallation script removes PATH modifications
- [x] Asks for user confirmation before modifying shell configuration files
- [x] Provides manual instructions if automatic configuration fails
- [x] Logs all shell configuration changes

---

## 11. Open Questions

1. **Q**: Should we support .bash_profile vs .bashrc?
   **A**: Prefer .bashrc (non-login shell), fallback to .bash_profile if .bashrc doesn't exist

2. **Q**: What if user has both bash and zsh configs?
   **A**: Only configure the currently active shell ($SHELL)

3. **Q**: Should we warn about PATH shadowing?
   **A**: Yes, check for conflicts with common system tools and warn

4. **Q**: Windows support in v2.3.0?
   **A**: Start with Linux/macOS, Windows in future release

---

## 12. Implementation Plan

### Phase 1: Core Functions (2 hours)
- `detect_shell()`
- `get_shell_config_file()`
- `check_path_already_configured()`

### Phase 2: Configuration (2 hours)
- `request_shell_config_consent()`
- `create_config_backup()`
- `add_path_to_shell_config()`
- `validate_shell_config()`

### Phase 3: Activation & Verification (1 hour)
- `activate_path_current_session()`
- `verify_tools_accessible()`

### Phase 4: Uninstallation (1 hour)
- `remove_shell_configuration()`

### Phase 5: Integration (1 hour)
- Integrate into install.sh (Step 8)
- Integrate into uninstall.sh (Step 4)
- Manual fallback instructions

### Phase 6: Testing (2 hours)
- Unit tests for all functions
- Integration tests for full workflow
- Edge case testing

**Total Estimated Effort**: 9 hours

---

## 13. Dependencies

- **Requirement**: REQ-011 v1.1
- **Team Review**: TEAM-REVIEW-011-v1.1 (✅ Approved)
- **Architecture Review**: ARCH-REVIEW-011-v1.1 (Pending)

---

## 14. Risks

| Risk | Mitigation | Status |
|------|------------|--------|
| Shell config corruption | Backup + syntax validation | ✅ Mitigated |
| PATH hijacking concerns | Document, warn on conflicts | ✅ Mitigated |
| Non-standard shell support | Fallback to manual | ✅ Mitigated |
| User confusion | Clear consent prompts | ✅ Mitigated |

---

**Document Version**: 1.0
**Status**: Ready for Architecture Review
**Next Steps**: Submit for ARCH-REVIEW-011-v1.1
