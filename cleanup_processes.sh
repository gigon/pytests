#!/usr/bin/env bash

# cleanup_processes.sh - Cross-platform process cleanup for Shufersal automation
# Handles Chrome, ChromeDriver, and uc_driver process cleanup across different OS

# Function to log messages with timestamp
log_cleanup() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OS" == "Windows_NT" ]]; then
        echo "windows"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Check if process exists (cross-platform)
process_exists() {
    local process_name="$1"
    local os="$2"
    
    case "$os" in
        "windows")
            tasklist 2>/dev/null | grep -q "$process_name"
            ;;
        "linux"|"macos")
            pgrep -f "$process_name" > /dev/null 2>&1
            ;;
        *)
            return 1
            ;;
    esac
}

# Kill process (cross-platform)
kill_process() {
    local process_name="$1"
    local os="$2"
    
    case "$os" in
        "windows")
            taskkill //F //IM "$process_name" //T > /dev/null 2>&1 || true
            ;;
        "linux"|"macos")
            pkill -f "$process_name" > /dev/null 2>&1 || true
            ;;
        *)
            log_cleanup "ERROR" "Unsupported OS for killing $process_name"
            return 1
            ;;
    esac
}

# Main cleanup function
cleanup_browser_processes() {
    local os=$(detect_os)
    log_cleanup "INFO" "Detected OS: $os"
    log_cleanup "INFO" "Starting browser process cleanup..."
    
    # List of processes to clean up (only automation-related)
    local processes=(
        "chrome.exe"
        "chromedriver.exe" 
        "uc_driver.exe"
    )
    
    # For non-Windows, remove .exe extension
    if [[ "$os" != "windows" ]]; then
        processes=(
            "chrome"
            "chromedriver"
            "uc_driver"
        )
    fi
    
    local found_processes=false
    
    # Check and kill each process type
    for process in "${processes[@]}"; do
        if process_exists "$process" "$os"; then
            log_cleanup "INFO" "Found $process processes. Killing them..."
            kill_process "$process" "$os"
            found_processes=true
            sleep 1
        else
            log_cleanup "INFO" "No $process processes found."
        fi
    done
    
    # Additional sleep if processes were killed
    if [[ "$found_processes" == "true" ]]; then
        log_cleanup "INFO" "Waiting for processes to terminate..."
        sleep 2
        
        # Verify cleanup
        log_cleanup "INFO" "Verifying cleanup..."
        for process in "${processes[@]}"; do
            if process_exists "$process" "$os"; then
                log_cleanup "WARN" "$process processes still running - attempting force kill..."
                kill_process "$process" "$os"
            fi
        done
    fi
    
    log_cleanup "INFO" "Browser process cleanup completed."
}

# Test mode - show current processes before and after cleanup
test_cleanup() {
    local os=$(detect_os)
    log_cleanup "INFO" "=== TESTING PROCESS CLEANUP ==="
    
    log_cleanup "INFO" "Processes BEFORE cleanup:"
    case "$os" in
        "windows")
            echo "Chrome processes:"
            tasklist 2>/dev/null | grep -i chrome || echo "  None found"
            echo "Driver processes:"
            tasklist 2>/dev/null | grep -i "driver\.exe" || echo "  None found"
            ;;
        "linux"|"macos")
            echo "Chrome processes:"
            pgrep -f chrome || echo "  None found"
            echo "Driver processes:"
            pgrep -f "driver" || echo "  None found"
            ;;
    esac
    
    echo ""
    cleanup_browser_processes
    echo ""
    
    log_cleanup "INFO" "Processes AFTER cleanup:"
    case "$os" in
        "windows")
            echo "Chrome processes:"
            tasklist 2>/dev/null | grep -i chrome || echo "  None found"
            echo "Driver processes:"
            tasklist 2>/dev/null | grep -i "driver\.exe" || echo "  None found"
            ;;
        "linux"|"macos")
            echo "Chrome processes:"
            pgrep -f chrome || echo "  None found"
            echo "Driver processes:"
            pgrep -f "driver" || echo "  None found"
            ;;
    esac
    
    log_cleanup "INFO" "=== TEST COMPLETED ==="
}

# Command line handling
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-cleanup}" in
        "test")
            test_cleanup
            ;;
        "cleanup"|*)
            cleanup_browser_processes
            ;;
    esac
fi
